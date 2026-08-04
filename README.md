# Git Push 工具

一个图形化的 Git 推送小工具。打开后选择本地文件夹或文件，填写远程仓库地址，点击按钮即可自动完成初始化、添加、提交与推送。

## 功能特性

- 选择文件夹或单个文件进行推送
- 自动完成 git init（若目标还不是仓库）、add、commit、remote、push
- 实时显示每一步执行日志
- 分支名与远程名可自定义（默认 main / origin）
- 提供可选的强制推送开关（默认关闭，避免误操作）
- 对 git 命令输出做了空值防护，兼容不同环境

## 使用方法

方式一：双击 `launch_gitpush.bat`，在弹出的窗口中操作。

方式二：命令行运行

    python git_push_tool.py

## 使用前准备

1. 本机已安装 Git，且可在命令行直接调用。
2. 首次使用请配置提交身份：

    git config --global user.name "你的名字"
    git config --global user.email "你的邮箱"

3. 推送到 GitHub 时，HTTPS 地址建议在地址中带上个人访问令牌：

    https://<TOKEN>@github.com/用户名/仓库.git

   或将凭证保存到系统的凭据管理器中。GitHub 已不支持使用账户密码直接推送。

## 文件说明

- `git_push_tool.py`：工具主程序
- `launch_gitpush.bat`：Windows 下一键启动脚本

## 许可

本项目归属 NekoAiDev 组织。
