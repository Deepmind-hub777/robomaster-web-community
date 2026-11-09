# 课堂 Windows 主机：Python 3.8 隔离环境

目标是 64 位 CPython 3.8。不要改系统 Python，也不要在 3.12 环境里强装旧 SDK。

## 安装步骤

1. 从 Python 官方下载页安装 **Python 3.8 x64**，安装时勾选 Python Launcher。确保选择 64 位安装包。
2. 打开 PowerShell，进入探针包目录：

   ```powershell
   cd <探针包目录>
   py -3.8 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. 验证解释器、SDK 版本和视频解码模块：

   ```powershell
   .\.venv\Scripts\python.exe --version
   .\.venv\Scripts\python.exe -c "import robomaster, cv2; print(robomaster.__version__); print(cv2.__version__)"
   ```

   预期 SDK 版本为 `0.1.1.68`。若 pip 找不到与 CPython 3.8 / Windows x64 匹配的 wheel，停止安装并记录完整错误；不要让 pip 静默从源码重编译旧版媒体扩展。

## 连接前检查

- Windows 主机与 EP Core 在同一个课堂局域网，关闭访客网络和 AP client isolation。
- 记录主机的 Wi-Fi/Ethernet 接口和机器人 IP；使用组网模式 `sta`。
- 先在路由器管理页确认机器人在线，再启动脚本。
- Windows 防火墙只允许专用网络的本地探针端口；不为公用网络开放。

## 运行

只观察 30 秒：

```powershell
.\.venv\Scripts\python.exe .\probe.py --observe-seconds 30
```

同一局域网有多台机器人时，可指定目标序列号：

```powershell
.\.venv\Scripts\python.exe .\probe.py --sn "YOUR_ROBOT_SN" --observe-seconds 30
```

运动租约试验（须先清场、装好载荷、安排观察员）：

```powershell
.\.venv\Scripts\python.exe .\probe.py --arm-motion --lease-ms 400 --speed 0.15
```

脚本会二次确认且每次只发一条速度命令；`--trial-count` 不适用。输出写入 `results\`，每次运行使用新的时间戳文件名。该试验不能代替断网、bridge 崩溃、睡眠等故障注入，也不能测浏览器端到端延迟。
