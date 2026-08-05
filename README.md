# Git Push 工具

一个图形化的 Git 推送小工具。打开后选择本地文件夹或文件，填写远程仓库地址，点击按钮即可自动完成初始化、添加、提交与推送。

## 功能特性

- 选择文件夹或单个文件进行推送
- 自动完成 git init（若目标还不是仓库）、add、commit、remote、push
- 实时显示每一步执行日志
- 分支名与远程名可自定义（默认 main / origin）
- 提供可选的强制推送开关（默认关闭，避免误操作）
- 对 git 命令输出做了空值防护，兼容不同环境
- 内置自动更新：菜单栏「更新(U)」→「检查更新」，拉取 GitHub Releases 最新版并自动替换 exe
- 专属 Git 风格应用图标：任务栏、窗口标题栏与 `GitPush.exe` 文件图标统一
- 自签名数字签名：`GitPush.exe` 附带代码签名证书（右键 → 属性 → 数字签名可查看）

## 使用方法

直接下载 `GitPush.exe`，双击即可运行，无需安装 Python。

## 使用前准备

1. 本机已安装 Git，且可在命令行直接调用。
2. 首次使用请配置提交身份：

    git config --global user.name "你的名字"
    git config --global user.email "你的邮箱"

3. 推送到 GitHub 时，HTTPS 地址建议在地址中带上个人访问令牌：

    https://<TOKEN>@github.com/用户名/仓库.git

   或将凭证保存到系统的凭据管理器中。GitHub 已不支持使用账户密码直接推送。

## 自动更新

1. 打开工具后，点击菜单栏「更新(U)」→「检查更新」。
2. 工具会自动连接 GitHub Releases，获取最新版本号与更新说明。
3. 发现新版本时，点击「立即更新」，工具会下载新 exe 并自动替换当前程序，随后重启。
4. 若当前运行的是 Python 脚本（开发模式），则只会下载新 exe 到临时目录，需要手动覆盖。

## 文件说明

- `git_push_tool.py`：工具主程序
- `launch_gitpush.bat`：Windows 下一键启动脚本
- `dist/GitPush.exe`：打包好的 Windows 单文件可执行程序
- `appicon.ico`：应用图标文件（Git 橙渐变 + 推送箭头 + 分支节点）
- `refresh_icon_cache.bat`：刷新 Windows 图标缓存脚本（图标显示异常时运行）

## 图标没显示出来？

如果下载 `GitPush.exe` 后，资源管理器里看到的是一个默认程序图标而不是橙色 Git 图标，那是 Windows 图标缓存还没刷新。请双击运行仓库里的 `refresh_icon_cache.bat`，或手动执行以下命令：

    taskkill /f /im explorer.exe
    del /f /s /q %localappdata%\IconCache.db
    start explorer.exe

刷新后重新打开文件夹即可看到新图标。

## 数字签名说明

从 v1.1.2 起，`GitPush.exe` 会附带一个自签名的代码签名证书。右键 exe →「属性」→「数字签名」可以看到签名信息。

> 自签名证书默认不会被 Windows 自动信任，所以 SmartScreen 仍可能提示「未知发布者」。如需消除提示，需要把证书安装到系统的「受信任的根证书颁发机构」存储中；普通使用直接双击运行即可。

## 许可

本项目归属 NekoAiDev 组织。
