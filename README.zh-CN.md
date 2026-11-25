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

## Windows 本地构建

使用 MSYS2 UCRT64，以下命令在 UCRT64 shell 中执行：

```sh
pacman -S --needed git zip \
  mingw-w64-ucrt-x86_64-{gcc,cmake,ninja,pkgconf,python,python-protobuf,qt6-base,qt6-declarative,qt6-svg,qt6-tools,qt6-translations,ffmpeg,libplacebo,curl,openssl,opus,speexdsp,json-c,miniupnpc,protobuf,libevent}
git submodule update --init --depth 1 third-party/nanopb third-party/jerasure third-party/gf-complete third-party/curl third-party/cpp-steam-tools
export CMAKE_BUILD_PARALLEL_LEVEL=2
INSTALL_PREFIX=/ucrt64 scripts/build-sdl2-compat.sh .
INSTALL_PREFIX=/ucrt64 scripts/build-hidapi.sh .
cp /ucrt64/lib/pkgconfig/sdl2-compat.pc /ucrt64/lib/pkgconfig/sdl2.pc
scripts/build-zh-windows.sh
```

输出目录为 `dist-zh/`。本次使用 Qt 6.11.1、FFmpeg 8.1.1、libplacebo 7.360.1，SDL3/sdl2-compat 由上游脚本固定版本构建。与上游官方发布包的依赖组合可能不同，须实测后再替换日常版本。每次构建写入 `BUILD-INFO.txt`，MSYS2 是滚动发行，未来依赖版本可能变化。

GitHub Actions 的 **Build Simplified Chinese Windows** 可手动触发并下载构建产物，不会自动安装到电脑。

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
