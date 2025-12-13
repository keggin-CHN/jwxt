import requests
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime, time as dt_time
import random
import string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64
import time
import json
import os

urllib3.disable_warnings()
stu_id = "2410403132"
stu_pwd = "Zhouwenjie@790920"
webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=bddf9ca2-b763-4a56-9014-2ecaa7fc712a" 
app_url = 'http://jwxt.njfu.edu.cn/sso.jsp'
uia_url = f'https://uia.njfu.edu.cn/authserver/login?service={app_url}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
}

HISTORY_FILE = 'grades_history.json'


def random_string(length):
    chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
    return ''.join(random.choice(chars) for _ in range(length))


def encrypt_aes(data, key):
    if not key:
        return data
    try:
        key = key.strip()
        random_prefix = random_string(64)
        iv = random_string(16)
        plaintext = random_prefix + data
        key_bytes = key.encode('utf-8')
        iv_bytes = iv.encode('utf-8')
        plaintext_bytes = plaintext.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        ciphertext = cipher.encrypt(pad(plaintext_bytes, AES.block_size))
        return base64.b64encode(ciphertext).decode('utf-8')
    except Exception as e:
        print(f'加密错误: {e}')
        return data


def uia_login(stu_id, stu_pwd):
    session = requests.Session()
    session.get(app_url, headers=headers, verify=False)
    res = session.get(uia_url, verify=False).text
    soup = BeautifulSoup(res, 'html.parser')
    
    try:
        lt = soup.find('input', {'name': 'lt'})['value']
        salt = soup.find('input', {'id': 'pwdDefaultEncryptSalt'})['value']
        dllt = soup.find('input', {'name': 'dllt'})['value']
    except Exception as e:
        print(f'✗ 获取登录参数失败: {e}')
        return None

    encrypted_pwd = encrypt_aes(stu_pwd, salt)
    
    data = {
        'username': stu_id,
        'password': encrypted_pwd,
        'lt': lt,
        'dllt': dllt,
        'execution': 'e1s1',
        '_eventId': 'submit',
        'rmShown': '1'
    }

    import time as t
    captcha_res = requests.get(
        f'https://uia.njfu.edu.cn/authserver/needCaptcha.html?username={stu_id}&pwdEncrypt2=pwdEncryptSalt&_={int(t.time() * 1000)}',
        verify=False
    )
    
    if captcha_res.text == 'false':
        res = session.post(uia_url, data=data, verify=False, allow_redirects=True)
        if res.status_code == 200 and 'uia.njfu.edu.cn' not in res.url:
            return session
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


def get_check_interval():
    current_time = datetime.now().time()
    start_time = dt_time(6, 0)
    end_time = dt_time(23, 59)
    
    if start_time <= current_time <= end_time:
        return 60
    else:
        return 300


def check_grades():
    print(f'\n[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] 开始检查成绩...')
    
    session = uia_login(stu_id, stu_pwd)
    if not session:
        print('✗ 登录失败，跳过本次检查')
        return
    
    current_grades = query_grades(session)
    if not current_grades:
        print('✗ 获取成绩失败，跳过本次检查')
        return
    
    print(f'✓ 成功获取成绩，共 {len(current_grades)} 门课程')
    
    history = load_history()
    new_courses = []
    
    for grade in current_grades:
        course_code = grade['课程编号']
        if course_code not in history:
            new_courses.append(grade)
            print(f'🆕 发现新成绩: {grade["课程名称"]} - {grade["成绩"]}')
    
    if new_courses:
        old_history_grades = list(history.values())
        old_gpa = calculate_gpa(old_history_grades)
        new_gpa = calculate_gpa(current_grades)
        
        print(f'\n📊 GPA变化: {old_gpa:.2f} → {new_gpa:.2f}')
        
        for new_grade in new_courses:
            send_wechat_notification(new_grade, old_gpa, new_gpa, len(current_grades))
        
        save_history(current_grades)
        print(f'✓ 已更新历史记录')
    else:
        print('无新成绩')


def main():
    print('='*60)
    print(' 南京林业大学成绩监控系统 ')
    print(' 24小时自动监控 - 智能调度 ')
    print('='*60)
    print(f'\n监控账号: {stu_id}')
    print(f'监控频率: 6:00-24:00 每分钟一次')
    print(f'          0:00-6:00  每5分钟一次')
    
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
                print(f'✓ 已记录 {len(grades)} 门课程，当前GPA: {gpa:.2f}')
            else:
                print('✗ 初始化失败，无法获取成绩')
                return
        else:
            print('✗ 初始化失败，登录失败')
            return
    
    print('\n✓ 监控系统启动成功！')
    print('按 Ctrl+C 停止监控\n')
    
    try:
        while True:
            check_grades()
            interval = get_check_interval()
            next_check = datetime.now().timestamp() + interval
            next_check_time = datetime.fromtimestamp(next_check).strftime('%H:%M:%S')
            print(f'下次检查时间: {next_check_time} (间隔{interval//60}分钟)')
            time.sleep(interval)
    except KeyboardInterrupt:
        print('\n\n✓ 监控系统已停止')


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
        from Crypto.Cipher import AES
    except ImportError:
        missing_libs.append('pycryptodome')
    
    if missing_libs:
        print(f'\n✗ 缺少必要的库: {", ".join(missing_libs)}')
        print(f'\n请先安装：pip install {" ".join(missing_libs)}')
        exit(1)
    
    main()
