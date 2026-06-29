import requests
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime, time as dt_time, timedelta
import random
import string
import base64
import time
import json
import os
import threading
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

urllib3.disable_warnings()
stu_id = ""
stu_pwd = ""
webhook_url = "" 
app_url = 'http://jwxt.njfu.edu.cn/sso.jsp'
uia_url = f'https://uia.njfu.edu.cn/authserver/login?service={app_url}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
}

HISTORY_FILE = 'grades_history.json'
DAILY_GRADES_FILE = 'daily_grades.json'
LOGS_FILE = 'monitor_logs.json'
STATUS_FILE = 'monitor_status.json'

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

monitor_status = {
    'is_running': False,
    'last_check_time': None,
    'next_check_time': None,
    'total_courses': 0,
    'current_gpa': 0.0,
    'total_credits': 0.0,
    'today_new_count': 0,
    'last_daily_push_date': None
}


def random_string(length):
    chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
    return ''.join(random.choice(chars) for _ in range(length))


# NJFU CAS 新版 RSA 公钥 (2025+ 从 login.js 提取)
_CAS_RSA_N = int("008aed7e057fe8f14c73550b0e6467b023616ddc8fa91846d2613cdb7f7621e3cada4cd5d812d627af6b87727ade4e26d26208b7326815941492b2204c3167ab2d53df1e3a2c9153bdb7c8c2e968df97a5e7e01cc410f92c4c2c2fba529b3ee988ebc1fca99ff5119e036d732c368acf8beba01aa2fdafa45b21e4de4928d0d403", 16)
_CAS_RSA_E = 0x10001

def encrypt_aes(data, key=None):
    """CAS 新版 RSA 加密 (textbook RSA，与前端 security.js RSAUtils 一致)"""
    try:
        cc = [ord(c) for c in data]
        cs = 126
        while len(cc) % cs:
            cc.append(0)
        m = 0
        for i in range(0, cs, 2):
            m += (cc[i] + cc[i + 1] * 256) * (65536 ** (i // 2))
        c = pow(m, _CAS_RSA_E, _CAS_RSA_N)
        return format(c, '0256x')
    except Exception as e:
        print(f'加密错误: {e}')
        return data


def uia_login(stu_id, stu_pwd):
    try:
        session = requests.Session()
        session.get(app_url, headers=headers, verify=False, timeout=10)
        res = session.get(uia_url, verify=False, timeout=10).text
        soup = BeautifulSoup(res, 'html.parser')
        
        try:
            execution = soup.find('input', {'name': 'execution'})['value']
        except Exception as e:
            print(f'✗ 获取登录参数失败: {e}')
            return None

        encrypted_pwd = encrypt_aes(stu_pwd)
        
        data = {
            'username': stu_id,
            'password': encrypted_pwd,
            'execution': execution,
            'encrypted': 'true',
            '_eventId': 'submit',
            'loginType': '1',
            'submit': '登 录'
        }

        import time as t
        captcha_res = requests.get(
            f'https://uia.njfu.edu.cn/authserver/needCaptcha.html?username={stu_id}&_={int(t.time() * 1000)}',
            verify=False,
            timeout=10
        )
        
        if captcha_res.text == 'false':
            res = session.post(uia_url, data=data, verify=False, allow_redirects=True, timeout=10)
            if res.status_code == 200 and 'uia.njfu.edu.cn' not in res.url:
                return session
        return None
    except requests.exceptions.SSLError as e:
        print(f'✗ SSL连接错误: {e}')
        add_log(f'SSL连接错误，将在下次检查时重试', 'warning')
        return None
    except requests.exceptions.Timeout as e:
        print(f'✗ 连接超时: {e}')
        add_log(f'连接超时，将在下次检查时重试', 'warning')
        return None
    except requests.exceptions.ConnectionError as e:
        print(f'✗ 网络连接错误: {e}')
        add_log(f'网络连接错误，将在下次检查时重试', 'warning')
        return None
    except Exception as e:
        print(f'✗ 登录过程发生未知错误: {e}')
        add_log(f'登录失败: {str(e)}', 'error')
        return None


def query_grades(session):
    list_url = 'https://jwxt.njfu.edu.cn/jsxsd/kscj/cjcx_list'
    query_data = {'kksj': '', 'kcxz': '', 'kcsx': '', 'kcmc': '', 'xsfs': 'all'}
    
    try:
        response = session.post(list_url, data=query_data, headers=headers, verify=False, timeout=30)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'dataList'})
        if not table:
            return []
        
        grades = []
        rows = table.find_all('tr')[1:]
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 10:
                continue
            
            grade_info = {
                '课程编号': cols[2].text.strip(),
                '课程名称': cols[3].text.strip(),
                '成绩': cols[4].text.strip(),
                '学分': cols[6].text.strip() if len(cols) > 6 else '',
                '绩点': cols[8].text.strip() if len(cols) > 8 else '',
                '开课学期': cols[1].text.strip(),
                '课程性质': cols[13].text.strip() if len(cols) > 13 else '',
            }
            grades.append(grade_info)
        
        return grades
    except Exception as e:
        print(f'查询失败: {e}')
        return []


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_history(grades):
    history = {grade['课程编号']: grade for grade in grades}
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def load_daily_grades():
    if os.path.exists(DAILY_GRADES_FILE):
        try:
            with open(DAILY_GRADES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                if data.get('date') == today:
                    return data.get('grades', [])
        except:
            pass
    return []


def save_daily_grades(new_grades):
    today = datetime.now().strftime('%Y-%m-%d')
    data = {'date': today, 'grades': new_grades}
    with open(DAILY_GRADES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_log(message, level='info'):
    logs = []
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    
    log_entry = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': message,
        'level': level
    }
    logs.insert(0, log_entry)
    logs = logs[:200]
    
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def update_status():
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(monitor_status, f, ensure_ascii=False, indent=2)


def calculate_total_credits(grades):
    total_credits = 0.0
    for grade in grades:
        try:
            credit = float(grade['学分'])
            if credit > 0:
                total_credits += credit
        except (ValueError, KeyError):
            continue
    return round(total_credits, 1)


def calculate_gpa(grades):
    total_credits = 0.0
    total_grade_points = 0.0
    
    for grade in grades:
        try:
            credit = float(grade['学分'])
            gpa = float(grade['绩点'])
            if gpa > 0:
                total_credits += credit
                total_grade_points += credit * gpa
        except (ValueError, KeyError):
            continue
    
    if total_credits > 0:
        return round(total_grade_points / total_credits, 2)
    return 0.0


def send_wechat_notification(new_grade, old_gpa, new_gpa, total_courses):
    if not webhook_url:
        print('未配置企业微信webhook地址')
        return
    
    grade_value = new_grade['成绩']
    credit = new_grade['学分']
    gpa = new_grade['绩点']
    course_name = new_grade['课程名称']
    course_code = new_grade['课程编号']
    semester = new_grade['开课学期']
    
    gpa_change = new_gpa - old_gpa
    gpa_change_text = f"+{gpa_change:.2f}" if gpa_change > 0 else f"{gpa_change:.2f}"
    
    if gpa_change > 0:
        emoji = "📈"
        trend = "上升"
    elif gpa_change < 0:
        emoji = "📉"
        trend = "下降"
    else:
        emoji = "➡️"
        trend = "持平"
    
    content = f"""🎓 **新成绩通知**

📚 **课程信息**
课程名称：{course_name}
课程编号：{course_code}
开课学期：{semester}

📊 **成绩详情**
成绩：{grade_value}
学分：{credit}
绩点：{gpa}

{emoji} **GPA变化**
出分前：{old_gpa:.2f}
出分后：{new_gpa:.2f}
变化：{gpa_change_text} ({trend})

📝 **统计信息**
已出成绩课程数：{total_courses}

⏰ 通知时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    
    try:
        response = requests.post(webhook_url, json=data, timeout=10)
        if response.status_code == 200:
            print('✓ 企业微信通知发送成功')
        else:
            print(f'✗ 企业微信通知发送失败: {response.status_code}')
    except Exception as e:
        print(f'✗ 发送通知失败: {e}')


def send_daily_summary(daily_grades, total_courses, current_gpa, gpa_change):
    if not webhook_url:
        print('未配置企业微信webhook地址')
        return
    
    today = datetime.now().strftime('%-m月%-d日' if os.name != 'nt' else '%#m月%#d日')
    new_count = len(daily_grades)
    
    new_courses_text = ''
    if new_count > 0:
        course_list = [f"{g['课程名称']}{g['成绩']}" for g in daily_grades]
        new_courses_text = '、'.join(course_list)
    else:
        new_courses_text = '无'
    
    if gpa_change > 0:
        gpa_text = f"GPA：{current_gpa:.2f} (↑{gpa_change:.2f})"
    elif gpa_change < 0:
        gpa_text = f"GPA：{current_gpa:.2f} (↓{abs(gpa_change):.2f})"
    else:
        gpa_text = f"GPA：{current_gpa:.2f}"
    
    content = f"""📅 {today}成绩日报

今日：+{new_count}门 | 总计：{total_courses}门
{gpa_text}

新增：{new_courses_text}"""
    
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    
    try:
        response = requests.post(webhook_url, json=data, timeout=10)
        if response.status_code == 200:
            print('✓ 每日汇总发送成功')
            add_log(f'每日汇总已发送：今日+{new_count}门', 'success')
        else:
            print(f'✗ 每日汇总发送失败: {response.status_code}')
            add_log(f'每日汇总发送失败: {response.status_code}', 'error')
    except Exception as e:
        print(f'✗ 发送每日汇总失败: {e}')
        add_log(f'发送每日汇总失败: {e}', 'error')


def get_check_interval():
    current_time = datetime.now().time()
    start_time = dt_time(6, 0)
    end_time = dt_time(23, 59)
    
    if start_time <= current_time <= end_time:
        return 60
    else:
        return 300


def check_grades():
    try:
        print(f'\n[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 开始检查成绩...')
        add_log('开始检查成绩')
        
        session = uia_login(stu_id, stu_pwd)
        if not session:
            print('✗ 登录失败，跳过本次检查')
            add_log('登录失败，将在下次检查时重试', 'warning')
            return
        
        current_grades = query_grades(session)
        if not current_grades:
            print('✗ 获取成绩失败，跳过本次检查')
            add_log('获取成绩失败，将在下次检查时重试', 'warning')
            return
    except Exception as e:
        print(f'✗ 检查成绩时发生错误: {e}')
        add_log(f'检查成绩时发生错误: {str(e)}', 'error')
        return
    
    print(f'✓ 成功获取成绩，共 {len(current_grades)} 门课程')
    
    monitor_status['last_check_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    monitor_status['total_courses'] = len(current_grades)
    monitor_status['current_gpa'] = calculate_gpa(current_grades)
    monitor_status['total_credits'] = calculate_total_credits(current_grades)
    
    history = load_history()
    new_courses = []
    
    for grade in current_grades:
        course_code = grade['课程编号']
        if course_code not in history:
            new_courses.append(grade)
            print(f'🆕 发现新成绩: {grade["课程名称"]} - {grade["成绩"]}')
            add_log(f'发现新成绩: {grade["课程名称"]} - {grade["成绩"]}', 'success')
    
    if new_courses:
        old_history_grades = list(history.values())
        old_gpa = calculate_gpa(old_history_grades)
        new_gpa = calculate_gpa(current_grades)
        
        print(f'\n📊 GPA变化: {old_gpa:.2f} → {new_gpa:.2f}')
        
        daily_grades = load_daily_grades()
        daily_grades.extend(new_courses)
        save_daily_grades(daily_grades)
        monitor_status['today_new_count'] = len(daily_grades)
        
        for new_grade in new_courses:
            send_wechat_notification(new_grade, old_gpa, new_gpa, len(current_grades))
        
        save_history(current_grades)
        print(f'✓ 已更新历史记录')
    else:
        print('无新成绩')
        add_log(f'检查完成，共{len(current_grades)}门课程，无新成绩')
    
    update_status()


def check_daily_push():
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    current_time = now.time()
    target_time = dt_time(22, 0)
    
    if (current_time.hour == 22 and current_time.minute == 0 and 
        monitor_status.get('last_daily_push_date') != today):
        
        daily_grades = load_daily_grades()
        history = load_history()
        all_grades = list(history.values())
        
        current_gpa = calculate_gpa(all_grades)
        
        gpa_change = 0.0
        if len(daily_grades) > 0:
            grades_without_new = [g for g in all_grades if g['课程编号'] not in [dg['课程编号'] for dg in daily_grades]]
            old_gpa = calculate_gpa(grades_without_new) if grades_without_new else 0.0
            gpa_change = current_gpa - old_gpa
        
        send_daily_summary(daily_grades, len(all_grades), current_gpa, gpa_change)
        monitor_status['last_daily_push_date'] = today
        update_status()


def monitor_thread():
    global monitor_status
    monitor_status['is_running'] = True
    
    print('='*60)
    print(' 南京林业大学成绩监控系统 v2.0 ')
    print(' 24小时自动监控 + Web前端 + 每日推送 ')
    print('='*60)
    print(f'\n监控账号: {stu_id}')
    print(f'监控频率: 6:00-24:00 每分钟一次')
    print(f'          0:00-6:00  每5分钟一次')
    print(f'每日推送: 22:00')
    print(f'Web前端: http://localhost:3000')
    
    if not webhook_url:
        print('\n⚠️  警告: 未配置企业微信webhook地址，将无法发送通知')
        print('请在代码顶部设置 webhook_url 变量\n')
    
    if not os.path.exists(HISTORY_FILE):
        print('\n初始化历史记录...')
        session = uia_login(stu_id, stu_pwd)
        if session:
            grades = query_grades(session)
            if grades:
                save_history(grades)
                gpa = calculate_gpa(grades)
                total_credits = calculate_total_credits(grades)
                monitor_status['total_courses'] = len(grades)
                monitor_status['current_gpa'] = gpa
                monitor_status['total_credits'] = total_credits
                print(f'✓ 已记录 {len(grades)} 门课程，当前GPA: {gpa:.2f}')
                add_log(f'系统初始化：{len(grades)}门课程，GPA: {gpa:.2f}', 'success')
            else:
                print('✗ 初始化失败，无法获取成绩')
                add_log('系统初始化失败：无法获取成绩', 'error')
                monitor_status['is_running'] = False
                return
        else:
            print('✗ 初始化失败，登录失败')
            add_log('系统初始化失败：登录失败', 'error')
            monitor_status['is_running'] = False
            return
    
    print('\n✓ 监控系统启动成功！')
    add_log('监控系统启动', 'success')
    
    error_count = 0
    max_errors = 10
    
    while monitor_status['is_running']:
        try:
            check_grades()
            check_daily_push()
            error_count = 0
            
            interval = get_check_interval()
            next_check = datetime.now() + timedelta(seconds=interval)
            monitor_status['next_check_time'] = next_check.strftime('%Y-%m-%d %H:%M:%S')
            update_status()
            
            next_check_time = next_check.strftime('%H:%M:%S')
            print(f'下次检查时间: {next_check_time} (间隔{interval//60}分钟)')
            time.sleep(interval)
        except KeyboardInterrupt:
            print('\n\n✓ 监控系统已停止')
            monitor_status['is_running'] = False
            break
        except Exception as e:
            error_count += 1
            print(f'\n监控循环异常 ({error_count}/{max_errors}): {e}')
            add_log(f'监控循环异常: {str(e)}', 'error')
            
            if error_count >= max_errors:
                print(f'\n连续错误次数过多，监控系统停止')
                add_log(f'连续错误{max_errors}次，监控系统停止', 'error')
                monitor_status['is_running'] = False
                break
            else:
                print(f'将在30秒后重试...')
                time.sleep(30)


@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/status')
def get_status():
    return jsonify(monitor_status)


@app.route('/api/grades')
def get_grades():
    history = load_history()
    grades = list(history.values())
    return jsonify(grades)


@app.route('/api/daily')
def get_daily_grades():
    daily_grades = load_daily_grades()
    return jsonify(daily_grades)


@app.route('/api/logs')
def get_logs():
    logs = []
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    return jsonify(logs)


@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    try:
        with open(LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        add_log('日志已清空', 'info')
        return jsonify({'success': True, 'message': '日志已清空'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def main():
    thread = threading.Thread(target=monitor_thread, daemon=True)
    thread.start()
    
    print('\n🌐 启动Web服务器...')
    print('请在浏览器访问前端: http://localhost:3000')
    print('API地址: http://localhost:5000')
    print('\n按 Ctrl+C 停止所有服务\n')
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print('\n\n✓ 系统已停止')
        monitor_status['is_running'] = False


if __name__ == '__main__':
    missing_libs = []
    
    try:
        import requests
    except ImportError:
        missing_libs.append('requests')
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        missing_libs.append('beautifulsoup4')
    
    try:
        from Crypto.Cipher import AES  # noqa: unused import kept for compat
    except ImportError:
        missing_libs.append('pycryptodome')
    
    try:
        from flask import Flask
    except ImportError:
        missing_libs.append('flask')
    
    try:
        from flask_cors import CORS
    except ImportError:
        missing_libs.append('flask-cors')
    
    if missing_libs:
        print(f'\n✗ 缺少必要的库: {", ".join(missing_libs)}')
        print(f'\n请先安装：pip install {" ".join(missing_libs)}')
        exit(1)
    
    main()

