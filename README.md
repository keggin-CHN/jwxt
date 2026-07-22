# 成绩监控系统

再也不用心惊胆战地每天打开 800 次教务系统查成绩了 ✨(★ᴗ★)

**在线 Demo：** [https://gpa.keggin.tech](https://gpa.keggin.tech)

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/keggin-CHN/jwxt/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)](https://github.com/keggin-CHN/jwxt/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

## 使用声明

本项目仅供学习交流使用，请勿用于非法用途。使用本项目产生的任何后果由使用者自行承担。

## 快速开始（推荐：下载 Release）

1. 打开 [Releases](https://github.com/keggin-CHN/jwxt/releases/latest)
2. 按系统下载对应压缩包：

   | 系统 | 资源文件 | 说明 |
   | --- | --- | --- |
   | Windows x64 | `jwxt-monitor-windows-x64-2.0.0.zip` | 解压后双击 `start.bat` |
   | Linux x86_64 | `jwxt-monitor-linux-x86_64-release.zip` | 解压后执行 `./start.sh` |

3. 浏览器访问 [http://localhost:7861](http://localhost:7861)
4. 在 Web 面板中添加学号 / 密码，并配置企业微信 Webhook

Linux 可选装 systemd：`sudo ./install-systemd.sh`（日志：`journalctl -u jwxt-monitor -f`）

## 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE)。欢迎 Issue / PR。

---

**下载地址：** [https://github.com/keggin-CHN/jwxt/releases/latest](https://github.com/keggin-CHN/jwxt/releases/latest)
