# RoboMaster Android 16 静态初检

## 输入与完整性

- 来源页面：[NAC AI & Robotics — Interactive Roadmap](https://4kzb9dszdgfsh.doubao.link/app/app_17hqpxsgc3f)
- 页面指向的 APK：[RoboMaster Android v1.2.0 GitHub Release](https://github.com/Deepmind-hub777/robomaster-app-mirror/releases/tag/robomaster-app-v1.2.0)
- 已下载到本任务输出目录：`RoboMaster-1.2.0.apk`（406.9 MiB）
- SHA-256：`82c86a9e77c4dbf9fb4c18660b3d0fbbfd6095c4c4b0eb03e9b2c6aae13059a1`，与 GitHub Release 的 asset digest 一致。
- 同一哈希的 APK 已存在于本机 Downloads，说明这次页面下载与现有副本逐字节相同。
- 注意：哈希一致只证明下载文件匹配 Release 元数据，不能单独证明其由 DJI 发布或文件内容安全。

## APK 初步画像

| 项目 | 观察结果 |
|---|---|
| Application ID | `com.dji.robomaster` |
| versionCode | `382` |
| versionName | Release 声明 `1.2.0`（尚未单独从 Manifest 输出核对） |
| minSdk / targetSdk | `21 / 28` |
| Unity | `2019.2.11f1`（从 `globalgamemanagers` 中的版本字符串观察） |
| 执行架构 | Unity IL2CPP；含 `libil2cpp.so`、`global-metadata.dat` |
| 原生 ABI | `armeabi-v7a`、`arm64-v8a` |
| 加固迹象 | Manifest 使用 `com.sagittarius.v6.StubApplication`；含 `libbaiduprotect.so` |
| 权限/组件线索 | 含位置、录音、存储、Wi-Fi、电话状态、安装包请求权限；含 Huawei/Xiaomi 推送与 Google/Firebase 组件 |

APK 内嵌的 v1 证书条目可读出主体 `CN=ares.li, OU=SZ DJI TECHNOLOGY CO., LTD`，SHA-256 指纹为 `9E:70:1D:2B:B9:31:4A:F4:21:C0:CC:BA:BD:14:DA:6A:53:E7:00:8E`。这只是证书元数据读取结果；尚未通过 DJI 官方发布渠道核对指纹，也尚未运行 apksigner/jarsigner 对 APK 的签名完整性做验证。

## Android 16 评估

1. **不要只改 `targetSdkVersion`。** 从 API 28 直接提到 API 36 会启用面向 Android 15/16 的目标版本行为，包括 edge-to-edge、预测性返回，以及大屏方向/尺寸限制变化。需要按 Android 官方迁移说明处理和测试。[Android 16 行为变更](https://developer.android.com/about/versions/16/behavior-changes-16) · [Edge-to-edge 指南](https://developer.android.com/develop/ui/views/layout/edge-to-edge)
2. **Unity 引擎过旧。** 2019.2.11f1 距 Android 16 已跨越多代 Android Gradle Plugin、Gradle、SDK、NDK、Unity Android 导出与插件接口。应在可重建的 Unity 工程里升级到仍受支持的 Unity 版本，并逐个更新/替换 DJI、Huawei、Xiaomi、Firebase 相关插件。
3. **主要应用逻辑不是普通 Java/Kotlin。** IL2CPP 把 C# 逻辑编译进原生库；APK 里有元数据和资源，但没有可直接恢复的原始 Unity 工程。若没有原始工程，完整恢复场景、脚本、资产和构建管线会是重大工作，且加固可能进一步增加难度。
4. **原包名的升级签名是硬门槛。** 用户设备只有在新 APK 使用原开发者的签名密钥（或有效签名轮换链）时，才能作为 `com.dji.robomaster` 的原位升级。证书公钥不能生成对应私钥；本次任务未取得 DJI 私钥。因此目前不能承诺产出可覆盖安装的官方包。可行技术路线是取得 DJI 授权和原工程，或制作包名不同、明确标注为社区分支的独立应用。
5. **机器人链路需要实机验证。** Android 16 上的 Wi-Fi 发现/连接、局域网通信、相机、USB、蓝牙、固件更新和厂商推送需要逐项验证；静态包信息无法证明这些功能可用。

## 建议的下一阶段

- 首先取得原 Unity 工程、构建说明、依赖插件源码/版本和合法签名方案；优先向 DJI 或原开发者索取。
- 若没有原工程，先做隔离环境中的 IL2CPP/Java 静态逆向与功能清单，评估可复建程度，再决定是否做独立 fork。
- 建立 Android 16/API 36 的构建链和模拟器矩阵；之后在实体 RoboMaster S1/EP/EP Core 上验收 Wi-Fi、控制、视频、编程、USB/蓝牙与固件流程。

## 未知 / 待核验

- 当前 Release 是否确由 DJI 授权镜像；证书指纹是否与 DJI 官方 APK 的可信指纹一致。
- APK 的 v2/v3 签名验证结果、实际 `versionName`、所有 exported 组件和网络端点。
- Unity 工程是否可从现有资产和 IL2CPP 元数据重建，以及防护层的实际作用范围。
- 目标 Android 16 设备型号、机器人型号、必须保留的功能和发布渠道。
- 能否获得原始 Unity 工程和签名密钥/授权。
