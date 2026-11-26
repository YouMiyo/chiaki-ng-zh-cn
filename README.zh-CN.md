# chiaki-ng 简体中文维护版

基于上游 **v1.10.1**（`f30da0aaeb96fc0026cc03683153f682352e7d7c`）。本仓库保留上游历史、许可证与英文源文案，中文资源单独维护，便于后续合并更新。

这是个人维护的非官方中文版本。上游项目：[chiaki-ng/chiaki-ng](https://github.com/chiaki-ng/chiaki-ng)。

## 使用

从本仓库的 Releases 下载 Windows x64 压缩包，完整解压后运行 `chiaki.exe`。不要只复制 exe，旁边的 DLL、QML 与 translations 目录也需要保留。

默认简体中文；英文界面可使用 `chiaki.exe --language en`，中文使用 `--language zh_CN`。这些选项应放在 `stream` 等子命令之前。

正常运行沿用上游的 `Chiaki/Chiaki` 配置位置，不改变 PSN 登录、配对、网络、手柄或串流协议。首次使用独立目录版本时先确认配置已正确读取。

仓库和发行包不包含任何用户的 PSN 令牌、配对密钥、主机信息、个人 INI 或运行日志。不要把导出的真实配置添加到仓库。

## 翻译范围

- 主界面、设置、主机注册、PSN 连接提示、手柄映射、串流菜单与统计。
- libplacebo 色彩映射、缩放、显示及高级渲染选项。
- Qt 文件对话框使用 Qt 自带简中翻译。
- 标准名称、编码器/算法名称、按键代号及单位保留必要英文。
- Sony 网页、游戏画面、操作系统设备名称、第三方库底层错误与诊断日志不由此翻译包控制。

翻译文件为 `gui/translations/chiaki_zh_CN.ts`。目前有 719 条条目，其中 718 条非空；构建检查覆盖完成状态、占位符、换行、富文本标签。条目完成率不代表所有窗口和串流功能均已人工验收。

## 与上游的差异

1. 在 GUI CMake 中编译并嵌入 Qt 翻译资源。
2. 启动时安装翻译器，增加 `--language`，默认中文。
3. 为少量原本未标记的按钮补充 `qsTr()`，给统计悬浮窗明确翻译上下文。
4. 增加翻译检查、更新脚本以及中文 Windows 构建工作流。
5. `CHIAKI_TRANSLATION_PREVIEW=1` 仅供开发验证：使用 `Chiaki-TranslationPreview` 独立配置，避免读取或覆盖正常账号配置。正常使用不要设置此变量。

未修改串流、网络、加密、配对或手柄协议实现。

## Windows 构建与运行库一致性

以 [.github/workflows/zh-windows.yml](.github/workflows/zh-windows.yml) 为构建入口，可在 GitHub Actions 手动运行 **Build Simplified Chinese Windows**。本地复现时在独立的 MSYS2 MINGW64 环境按该工作流顺序执行，避免覆盖其他项目的 SDK。

工作流沿用官方 v1.10.1 的 MINGW64 构建方式，并校验 Qt 6.12.0、FFmpeg avcodec 63.1.102（9.0.2 系列）、libplacebo 7.387.0。FFmpeg SDK ZIP 与官方运行包使用固定 SHA256；libplacebo 使用固定提交。若上游滚动下载内容改变，构建会失败，需要人工审核更新。

打包时直接解压官方 v1.10.1 Windows 便携包，只替换汉化 `chiaki.exe`，另加翻译、源码获取说明及许可告知。**其余原有文件必须逐个 SHA256 一致**，不把 SDK 里的另一套 DLL 混进发行包。新 exe 导入的第三方 DLL 符号也必须在官方运行库中存在，否则打包失败。

产物是 `chiaki-ng-1.10.1-zh.2-windows-x64.zip`，含 `RUNTIME-VERIFICATION.json` 和 `SOURCE-INFO.txt`。SDK 的具体包版本另记于 `sdk-packages.txt`；构建工具链未声称与官方历史构建逐字节一致。运行库一致也不等于已经通过游戏串流稳定性验收。

历史 `zh.1` 使用 UCRT64、Qt 6.11.1、FFmpeg 8.1.1、libplacebo 7.360.1。正在排查其丢帧后画面冻结问题，不能排除依赖差异带来的回归。旧 `scripts/build-zh-windows.sh` 仅保留供明确设置 `ALLOW_LEGACY_SDK=1` 的开发实验，不作为当前发行流程。

构建产物不会自动替换本机正在使用的客户端；先在独立目录测试，再决定日常使用版本。

## 同步上游新版

`main` 保存汉化；`upstream-stable` 保存当前基线。本仓库是 `chiaki-ng/chiaki-ng` 的公开 GitHub fork，保留上游历史，汉化改动在本仓库中维护。

工作区干净后，在 PowerShell 执行（版本号替换为已核实的稳定版）：

```powershell
./scripts/sync-upstream.ps1 -Tag v1.10.2 -LUpdate C:/msys64/ucrt64/bin/lupdate.exe
```

脚本会获取官方标签，在 `sync/v版本号` 分支合并并刷新 `.ts` 文件。若存在代码冲突或未完成译文会停止，保留现场供处理；不强制覆盖，不自动推送。

然后：

1. 解决冲突，在 Qt Linguist 或文本编辑器中检查新增、变更译文。
2. 运行 `python scripts/check-zh-translations.py`，构建并检查中文和英文界面。
3. 测试连接、画面、声音、手柄，再提交合并请求到 `main`。
4. 合并后将 `upstream-stable` 更新到实际采用的官方标签，更新本文基线与构建记录。
5. 创建新的中文版本标签和 Release，保留可回退的旧发行包。

仅刷新译文可运行 `scripts/update-zh-translations.ps1`。英语原文是匹配键，翻译时不要直接把内部配置键或原文标识替换成中文。

本仓库禁用上游专用的定时构建、自动发行、Discord 通知和旧 PR 构建工作流，仅保留中文检查及手动构建。不要在未核对目的和权限前重新启用这些上游工作流。

## 许可

保留上游 `COPYING` 与各源文件许可标记，汉化代码和资源沿用适用的上游许可。向其他人分发二进制时，须按许可证同时提供对应源码与相关告知；私密仓库本身不免除分发义务。
