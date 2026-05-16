# 🎓 成绩监控系统

再也不用心惊胆战地每天打开800次教务系统查成绩了✨(★ᴗ★) 

## 在线demo:https://gpa.keggin.tech

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![React](https://img.shields.io/badge/react-18.2.0-61dafb)
![License](https://img.shields.io/badge/license-MIT-orange)

## ⚠️ 使用声明
**免责声明本项目仅供学习交流使用，请勿用于非法用途。使用本项目产生的任何后果由使用者自行承担。**

## ✨ 主要特性

### 🔄 自动监控
- ⏰ **24小时自动监控**：6:00-24:00 每分钟检查一次，其他时段每5分钟检查一次
- 📱 **实时推送通知**：新成绩即时通过企业微信推送，包含详细成绩信息和GPA变化
- 📊 **每日汇总**：每天22:00自动推送当日成绩汇总


## 🚀 快速开始

### 环境要求

- **Python**: 3.7+
- **Node.js**: 14+
- **npm**: 6+
- **操作系统**: Windows / Linux / macOS

### Windows系统

#### 1. 安装依赖

双击运行 `install_deps.bat` 或在命令行中执行：

```batch
install_deps.bat
```

#### 2. 配置账号

编辑 `monitor.py` 文件，修改以下信息：

```python
stu_id = "你的学号"
stu_pwd = "你的密码"
webhook_url = "你的企业微信webhook地址"
```

#### 3. 启动系统

双击运行 `start.bat` 或在命令行中执行：

```batch
start.bat
```

### Linux/macOS系统

#### 1. 赋予执行权限

```bash
chmod +x install_deps.sh start.sh
```

#### 2. 安装依赖

```bash
./install_deps.sh
```

#### 3. 配置账号

编辑 `monitor.py` 文件，修改以下信息：

```python
stu_id = "你的学号"
stu_pwd = "你的密码"
webhook_url = "你的企业微信webhook地址"
```

#### 4. 启动系统

```bash
./start.sh
```

## 🌐 访问界面

启动成功后，在浏览器中访问：

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000

## 🔔 推送通知

### 企业微信配置

1. 创建企业微信群聊机器人
2. 获取Webhook地址
3. 在 `monitor.py` 中配置 `webhook_url`

### 通知类型

#### 新成绩通知

每当有新成绩发布时，立即推送包含：
- 课程信息（名称、编号、学期）
- 成绩详情（成绩、学分、绩点）
- GPA变化（出分前后对比、变化趋势）
- 统计信息（已出成绩课程数）

## 📄 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交Issue和Pull Request！

---


