#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Push 工具 
================================
一个带图形界面的小工具：打开后，选择本地文件夹（或单个文件），
填写远程仓库地址，点一下按钮，就能自动完成：
    git init（如果还不是仓库）
    git add
    git commit
    git remote add / set-url
    git push -u <remote> <branch>
并在界面上实时显示每一步的日志

运行方式（本机）：
    python git_push_tool.py
需要本机已安装 git 且能在命令行直接调用。
"""

import json
import os
import time
import re
from datetime import datetime
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
import urllib.request
from tkinter import ttk, filedialog, scrolledtext, messagebox, font as tkfont
import webbrowser
import uuid as _uuid

# 统计上报接口（匿名、仅收集合法使用数据，绝不收集任何隐私）
STATS_URL = "https://install.nekoaidev.top/api/report"

APP_TITLE = "Git Push 工具推送"
APP_VERSION = "1.3.4"

# ---- 内置文档（与安装目录中的 .txt 内容一致），供「帮助」菜单直接展示 ----
DOC_EULA = r"""
Git Push 工具 用户服务协议

版本生效日期：2026 年 8 月 12 日

欢迎使用 Git Push 工具（以下简称"本软件"或"本工具"）。本软件由 NekoAiDev 团队（以下简称"运营方"）开发、维护并提供分发服务。在您下载、安装、复制、运行或继续使用本软件之前，请务必仔细阅读并充分理解本协议的全部内容，特别是以加粗方式标注的免责、责任限制、协议变更与争议解决等条款。

如果您尚未满十八周岁，请在法定监护人的陪同与同意下阅读本协议，并在取得监护人明确同意后方可使用本软件。

一旦您下载、安装、运行或继续使用本软件，即视为您已阅读、理解并完全同意接受本协议各项条款的约束。若您不同意本协议的任何内容，请立即停止下载、安装或使用本软件，并删除已安装的全部程序文件。

一、软件概述与服务说明
1.1 本软件是一款运行于 Microsoft Windows 操作系统的图形化 Git 辅助工具，旨在帮助不熟悉命令行操作的用户，通过简单的图形界面选择本地文件或文件夹、填写远程仓库地址，并一键完成 git add、git commit、git remote 设置与 git push 等操作。
1.2 本软件本身不包含任何独立版本控制系统，其功能完全依赖于您计算机上已安装的 Git 命令行程序。若您的计算机尚未安装 Git，本软件将无法完成推送操作，并会在界面中给出相应提示。
1.3 本软件提供可选的自动更新功能，可在您授权后从运营方指定的官方分发服务器（域名：install.nekoaidev.top）下载并安装新版本程序。
1.4 本软件为免费软件，运营方不向任何用户收取任何使用费用，亦不承诺提供任何形式的付费保障或商业支持。

二、用户数据与匿名统计
2.1 为持续改进产品体验、了解功能使用情况、发现并修复潜在问题，本软件在获得您明确同意的前提下，会向运营方服务器上报极少量的匿名使用统计数据。
2.2 我们收集的匿名统计数据仅限于以下字段，绝不包含任何可识别您个人身份的信息，也绝不包含您的文件内容、仓库地址、文件路径、计算机硬件信息或任何系统隐私数据：
    （一）一个由软件在您设备上随机生成的匿名设备标识（UUID）。该标识仅用于区分不同的安装实例，不与您的真实身份、账号或设备序列号关联；
    （二）本软件当前的版本号；
    （三）您使用本工具成功完成"推送"操作的累计次数；
    （四）您使用本工具成功完成"更新"操作的累计次数；
    （五）本次使用会话的启动时间与持续时长（以毫秒计）；
    （六）本次上报所对应的事件类型（包括：推送成功、更新成功、会话结束）。
2.3 上述数据在您首次启动软件时，会弹出提示明确征询您的同意。只有在您选择"同意"后，软件才会进行上述上报；若您选择"拒绝"，或在本地删除对应的匿名标识文件，软件将完全停止此类上报，且不影响任何其它功能的正常使用。
2.4 关于上述数据的收集、使用、存储与保护等更多细节，请参阅与本协议一并提供的《Git Push 工具 隐私政策》。

三、用户的权利与义务
3.1 您有权在遵守本协议及国家相关法律法规的前提下，免费使用本软件提供的全部功能。
3.2 您理解并同意：您使用本软件进行的任何 Git 推送操作，均代表您本人的真实意愿；由此产生的代码提交记录、仓库内容、授权行为以及对外公开信息，一切后果由您自行承担。
3.3 您应妥善保管自己的远程仓库凭证（包括但不限于用户名、密码、个人访问令牌 Token 等）。本软件仅在您本地计算机上调用 Git 命令行程序完成操作，不会将您的凭证上传至任何第三方服务器；但请您注意，通过不安全的网络或向公开仓库推送敏感信息可能导致信息泄露，由此产生的风险由您自行承担。
3.4 您不得利用本软件从事任何违反国家法律法规、侵犯他人合法权益、破坏网络安全、干扰其他网络服务正常运行或损害社会公共利益的行为。
3.5 您不得对本软件进行反向工程、反向汇编、反向编译，或试图提取其源代码（法律另有明确规定或为权利义务保护所必须的除外）。

四、知识产权
4.1 本软件及其相关的一切著作权、商标权、专利权、商业秘密等知识产权，均归运营方或相关权利人所有，并受相关法律法规保护。
4.2 本软件采用自签名代码签名证书，其作用仅限于在您计算机上标识发布者身份、减少 Windows 系统弹出的"未知发布者"安全提示，并不代表本软件已通过任何第三方权威机构的认证或担保。
4.3 未经运营方书面许可，您不得将本软件用于任何商业性再分发、捆绑销售或营利性服务；您可出于个人学习、使用目的，在不修改软件本体及署名的前提下自由复制与传播。

五、免责声明
5.1 本软件按"现状"提供。运营方已尽合理努力保障其功能正常，但不对本软件的适用性、可靠性、无中断性、无错误或满足特定用途作出任何明示或默示担保。
5.2 因下列原因之一造成您任何损失的，运营方不承担责任：
    （一）您计算机环境异常（如未安装 Git、系统组件缺失、权限不足、防病毒软件拦截）导致功能无法使用；
    （二）您的网络、代理、防火墙或远程仓库服务（如 GitHub、Gitee 等）本身的故障、限流、变更或停止服务；
    （三）您填写的仓库地址、凭证错误，或远程仓库的访问权限、存储容量、配额限制；
    （四）不可抗力（包括但不限于自然灾害、网络基础设施故障、政策调整、电力中断）或第三方服务中断。
5.3 您使用本软件所作的任何操作（包括但不限于误推送、覆盖提交、删除分支、强制推送等），风险由您自行承担，运营方不提供任何数据恢复服务。

六、协议的变更
6.1 运营方保留在必要时修改本协议条款的权利。修改后的协议将在软件更新或官方页面中予以公示。
6.2 若您在协议变更后继续使用本软件，即视为您接受变更后的协议；若您不同意变更后的协议，应停止使用并删除本软件。

七、法律适用与争议解决
7.1 本协议的订立、执行、解释及争议的解决，均适用中华人民共和国大陆地区相关法律法规。
7.2 因本协议引起的或与本协议有关的任何争议，双方应友好协商解决；协商不成的，任何一方均可向运营方所在地有管辖权的人民法院提起诉讼。

八、联系我们
8.1 如您对本协议、隐私政策或本软件本身有任何疑问、意见或投诉，可通过以下方式联系运营方：
    （一）在软件"帮助"菜单中点击"问题反馈"，前往 GitHub Issues 页面提交您的问题；
    （二）发送电子邮件至运营方指定的联系邮箱（以官方页面公示为准）。
8.2 运营方将在合理期限内对您的反馈予以回应，但不保证对所有反馈均提供个性化解决方案。

九、其他
9.1 本协议构成您与运营方之间关于本软件使用的完整协议，并取代此前任何口头或书面的沟通与约定。
9.2 本协议任一条款被认定为无效或不可执行的，不影响其余条款的效力。
9.3 运营方未行使或延迟行使本协议项下的任何权利，不构成对该权利的放弃。

感谢您使用 Git Push 工具。愿本工具能让您的代码推送更简单、更顺手。
"""

DOC_PRIVACY = r"""
Git Push 工具 隐私政策

版本生效日期：2026 年 8 月 12 日

本《隐私政策》（以下简称"本政策"）向您说明：当您使用 Git Push 工具（以下简称"本软件"或"本工具"，由 NekoAiDev 团队运营）时，我们如何收集、使用、存储与保护您的个人信息及相关数据。请您在使用本软件前仔细阅读本政策。

本软件的设计理念是"最小必要、匿名优先"。我们坚信，一款帮助您推送代码的工具，没有必要、也没有权利窥探您的文件与隐私。因此，本政策的核心结论是：本软件默认不收集任何可识别您个人身份的信息，仅在您明确同意后收集极少量的匿名使用统计数据，且绝不涉及您的代码、仓库与计算机隐私。

一、我们收集的信息
在您明确同意匿名统计后，本软件仅向运营方服务器上报以下匿名字段：
1.1 匿名设备标识（UUID）：由软件在您设备上随机生成的字符串，用于区分不同的安装实例。它不与您的姓名、账号、邮箱、设备序列号或任何真实身份关联。
1.2 软件版本号：用于了解用户群体所使用的版本分布，从而决定需要维护哪些旧版本。
1.3 推送成功次数：您使用本工具成功完成"推送"操作的累计次数。
1.4 更新成功次数：您使用本工具成功完成"更新"操作的累计次数。
1.5 会话启动时间与持续时长：本次使用会话的开始时刻，以及自开始到本次上报时的运行时长（毫秒）。
1.6 事件类型：本次上报对应的事件，包括"推送成功""更新成功""会话结束"。

二、我们如何收集这些信息
2.1 匿名设备标识在您首次运行本软件时于本地随机生成，并保存在您计算机上的本地配置文件中，不会在生成过程中上传任何信息。
2.2 使用统计数据由本软件在您完成相应操作（推送、更新）或退出会话时，通过 HTTPS 协议自动发送至运营方指定的统计接口（位于 install.nekoaidev.top 域名下）。
2.3 发送过程在后台线程中进行，不会阻塞您对本软件的正常使用；若网络不可用或发送失败，软件将静默忽略，不会影响您继续使用其它功能。

三、我们如何使用这些信息
3.1 我们仅将匿名统计数据用于以下合法目的：
    （一）了解功能使用情况，判断哪些功能受欢迎、哪些需要改进；
    （二）统计整体推送与更新频次，评估软件稳定性与活跃度；
    （三）发现异常使用模式或潜在故障，以便及时修复。
3.2 我们不会将匿名统计数据用于广告投放、用户画像、商业营销，亦不会将其出售、出租或交换给任何第三方。

四、我们明确不会收集的信息
为保护您的隐私，本软件在设计上明确排除以下信息的收集与上传：
4.1 您的文件内容：本软件不会读取、上传、扫描您选择推送之外的任何文件，也不会上传您实际推送的代码、文档或资源。
4.2 您的仓库地址与路径：本软件不会将您填写的远程仓库地址、本地文件夹路径或文件名上报给服务器。
4.3 您的个人身份信息：本软件不要求注册账号，因此不收集您的姓名、手机号、邮箱、社交媒体账号等任何可识别个人身份的信息。
4.4 您的凭证：本软件仅在本地调用 Git 完成操作，绝不收集或上传您的密码、Token、SSH 密钥等凭证。
4.5 您的计算机隐私信息：本软件不会收集您的硬件序列号、MAC 地址、操作系统详细配置、已安装软件列表、浏览记录、地理位置等与代码推送无关的计算机信息。
4.6 您在使用过程中的具体输入内容（如填写的仓库地址、提交说明等），均仅在本地用于完成 Git 操作，不会被记录或上报。

五、数据存储与安全
5.1 匿名统计数据存储在运营方托管的 Cloudflare KV 存储服务中，与具体的个人身份无任何关联。
5.2 我们采取合理的访问控制措施保护存储的数据，仅限于授权维护人员为上述目的进行必要查阅。
5.3 您的匿名设备标识以本地文件形式保存在您的计算机上，您可以随时通过删除该本地文件（或在软件提示时选择"拒绝"）来停止一切上报行为。
5.4 由于互联网传输的固有特性，任何数据传输都无法保证绝对安全。我们将尽合理努力保护您的数据，但不对不可抗力或第三方攻击导致的泄露承担责任。

六、数据的共享与披露
6.1 我们不会与任何第三方共享、出售或交换本软件收集的匿名统计数据。
6.2 仅在下列情形下，我们可能依法披露相关信息：
    （一）根据适用法律、法规、司法或行政程序的要求；
    （二）为保护运营方、用户或公众的合法权益、安全与财产所必须。
6.3 除上述情形外，您的匿名统计数据不会被披露给任何外部组织或个人。

七、您的权利
7.1 您有权决定是否同意匿名统计。首次启动时软件会明确询问，您可随时选择拒绝；选择拒绝后不会进行任何上报。
7.2 您有权撤回已作出的同意：只需删除本软件所在目录下的本地统计配置文件（通常名为 stats.json），即可彻底停止上报，且不影响其它功能。
7.3 您有权了解我们收集的数据范围——本政策第四条已详尽列明我们"不会"收集的内容，第五条列明了我们"会"收集的内容。
7.4 由于本软件不收集可识别个人身份的信息，因此不存在"删除个人账号数据"的场景；您所拥有的匿名标识本质上只是一串随机字符，删除本地文件即等同于彻底脱离统计。

八、服务器访问日志
8.1 为支撑统计接口的安全运行，服务器的基础设施（Cloudflare）可能会在短时间内记录每次请求的来源 IP 地址、时间、响应状态等基础访问日志，用于抵御恶意请求与保障服务稳定。
8.2 此类基础访问日志不与本软件上报的匿名统计数据做关联分析，运营方亦不会据此识别您的身份。相关日志的留存周期由基础设施提供方按照其通用安全策略管理。

九、未成年人保护
9.1 我们高度重视未成年人个人信息保护。本软件不面向未满十八周岁的未成年人定向设计，亦不主动收集未成年人个人信息。
9.2 若您是未成年人，请在法定监护人同意并由其陪同下使用本软件。

十、本政策的变更
10.1 我们可能适时更新本政策。更新后的政策将在软件更新或官方页面中公示，并在文件顶部标注新的生效日期。
10.2 若您在本政策变更后继续使用本软件，即视为您接受变更后的政策。

十一、联系我们
11.1 如您对本政策有任何疑问、意见或投诉，可通过以下方式联系运营方：
    （一）在软件"帮助"菜单中点击"问题反馈"，前往 GitHub Issues 页面提交；
    （二）发送电子邮件至运营方指定的联系邮箱（以官方页面公示为准）。
11.2 我们将在合理期限内对您的关切予以回应。

本政策所述内容，均以"保护用户隐私、最小必要收集"为基本原则。感谢您对 Git Push 工具的信任。
"""

GITHUB_OWNER = "NekoAiDev"
GITHUB_REPO = "Git-Push"
# 版本信息文件（跟随 main 分支，始终是最新版）；更新系统从这里读取最新版本号与更新包地址
VERSION_JSON_URL = "https://install.nekoaidev.top/version.json"


def is_git_available():
    """检查本机 git 是否可用。"""
    try:
        subprocess.run(["git", "--version"],
                       capture_output=True, text=True, timeout=10,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except Exception:
        return False


class GitPushTool:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_TITLE}  v{APP_VERSION}")
        self.root.geometry("720x620")
        self.root.minsize(640, 520)
        self.root.maxsize(900, 800)
        try:
            # 尝试给窗口加个小图标感（无图标文件时忽略）
            pass
        except Exception:
            pass

        self.running = False

        self._build_styles()
        self._build_ui()
        self._build_menu()

        # 初始化匿名统计（默认开启；首次启动不再弹窗询问，可在「服务」→「使用收集」中修改）
        self._init_stats()
        self._apply_settings()
        # 关闭窗口确认（若开启）
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # 启动时检查 git
        if not is_git_available():
            self.set_status("⚠️ 未发现 git，请先安装 git 并加入 PATH")
            messagebox.showwarning(
                " git 没找到",
                "本机似乎没有安装 git，或者 git 不在系统 PATH 里\n"
                "请先安装 git：https://git-scm.com/downloads\n"
                "安装后重启本工具即可~"
            )
        else:
            self.set_status("就绪，请选择文件夹并填写仓库地址")

    # ---------------------------------------------------------------- UI
    def _build_styles(self):
        self.style = ttk.Style()
        try:
            self.style.theme_use("vista")
        except Exception:
            pass
        # 用 tkfont.Font 对象指定字体，避免 Tcl/Tk 错误解析中文字体名
        self.title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.small_font = tkfont.Font(family="Segoe UI", size=9)
        self.btn_font   = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.style.configure("Title.TLabel", font=self.title_font)
        self.style.configure("Small.TLabel", font=self.small_font)
        self.style.configure("Run.TButton",  font=self.btn_font)

    def _build_ui(self):
        pad = {"padx": 12, "pady": 5}

        # 标题
        head = ttk.Label(self.root, text="  " + APP_TITLE, style="Title.TLabel")
        head.pack(anchor="w", **pad)

        sub = ttk.Label(self.root,
                        text="选好文件夹、填好仓库地址，一键自动推送",
                        style="Small.TLabel")
        sub.pack(anchor="w", **pad)

        # 输入区
        frm = ttk.LabelFrame(self.root, text="推送设置", padding=(12, 8))
        frm.pack(fill="x", padx=12, pady=6)
        frm.columnconfigure(1, weight=1)

        # 本地路径
        ttk.Label(frm, text="本地路径：").grid(row=0, column=0, sticky="w", pady=4)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(frm, textvariable=self.path_var)
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=(0, 6))
        ttk.Button(frm, text="选择文件夹", width=11,
                   command=self._pick_folder).grid(row=0, column=2, padx=2)
        ttk.Button(frm, text="选择文件", width=10,
                   command=self._pick_file).grid(row=0, column=3)

        # 远程仓库
        ttk.Label(frm, text="远程仓库：").grid(row=1, column=0, sticky="w", pady=4)
        self.repo_var = tk.StringVar()
        self.repo_entry = ttk.Entry(frm, textvariable=self.repo_var)
        self.repo_entry.grid(row=1, column=1, columnspan=3, sticky="ew")
        ttk.Label(frm, text="例：https://github.com/用户名/仓库.git",
                  style="Small.TLabel").grid(row=2, column=1, columnspan=3, sticky="w")

        # 分支 / 远程名
        ttk.Label(frm, text="分支名：").grid(row=3, column=0, sticky="w", pady=4)
        self.branch_var = tk.StringVar(value="main")
        ttk.Entry(frm, textvariable=self.branch_var, width=16).grid(row=3, column=1, sticky="w", padx=(0, 6))

        ttk.Label(frm, text="远程名：").grid(row=3, column=2, sticky="w", padx=(10, 4), pady=4)
        self.remote_var = tk.StringVar(value="origin")
        ttk.Entry(frm, textvariable=self.remote_var, width=12).grid(row=3, column=3, sticky="w")

        # 提交信息
        ttk.Label(frm, text="提交信息：").grid(row=4, column=0, sticky="w", pady=4)
        self.commit_var = tk.StringVar(value="Auto push by Git Push工具")
        ttk.Entry(frm, textvariable=self.commit_var).grid(row=4, column=1, columnspan=3, sticky="ew")

        # 选项
        self.force_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="强制推送 --force（危险！仅私人分支使用）",
                        variable=self.force_var).grid(row=5, column=0, columnspan=4, sticky="w", pady=(6, 0))

        # 推送按钮
        self.push_btn = ttk.Button(self.root, text="🚀 开始推送", style="Run.TButton",
                                   command=self.start_push)
        self.push_btn.pack(fill="x", padx=12, pady=(4, 8))

        # 日志区（固定高度，不无限撑大，避免把底部状态栏挤出屏幕）
        log_frm = ttk.LabelFrame(self.root, text="运行日志", padding=(8, 6))
        log_frm.pack(fill="x", padx=12, pady=(0, 6))

        self.log_box = scrolledtext.ScrolledText(log_frm, wrap="word",
                                                  font=("Consolas", 10),
                                                  height=10)
        self.log_box.pack(fill="both", expand=True)
        self.log_box.configure(state="disabled")

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var,
                                    relief="sunken", anchor="w", padding=(6, 3))
        self.status_bar.pack(fill="x", side="bottom")

    def _build_menu(self):
        menubar = tk.Menu(self.root)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_separator()
        help_menu.add_command(label="问题反馈", command=self._open_issues)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        update_menu = tk.Menu(menubar, tearoff=0)
        update_menu.add_command(label="检查更新", command=self._open_updater)
        menubar.add_cascade(label="更新", menu=update_menu)

        service_menu = tk.Menu(menubar, tearoff=0)
        service_menu.add_command(label="用户服务协议", command=lambda: self._show_doc("用户服务协议", DOC_EULA))
        service_menu.add_command(label="隐私政策", command=lambda: self._show_doc("隐私政策", DOC_PRIVACY))
        service_menu.add_separator()
        service_menu.add_command(label="使用收集", command=self._open_data_collection)
        menubar.add_cascade(label="服务", menu=service_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="推送设置", command=self._open_settings)
        menubar.add_cascade(label="设置", menu=settings_menu)

        self.root.config(menu=menubar)

    # ---------------------------------------------------------------- 选择
    def _save_last_path(self, p):
        """记录最近一次选择的本地路径（供「记住路径」功能使用）。"""
        try:
            s = self._load_settings()
            s["last_path"] = p
            self._save_settings(s)
        except Exception:
            pass

    def _pick_folder(self):
        p = filedialog.askdirectory(title="选择要推送的文件夹")
        if p:
            self.path_var.set(p)
            self._save_last_path(p)

    def _pick_file(self):
        p = filedialog.askopenfilename(title="选择要推送的单个文件")
        if p:
            self.path_var.set(p)
            self._save_last_path(p)

    # ---------------------------------------------------------------- 日志
    def log(self, text):
        self.root.after(0, self._append_log, str(text))

    def _append_log(self, text):
        try:
            settings = self._load_settings()
        except Exception:
            settings = {}
        ts = settings.get("log_timestamp", True)
        prefix = datetime.now().strftime("[%H:%M:%S] ") if ts else ""
        line = prefix + str(text) + "\n"

        # 日志存档（若开启）
        if settings.get("save_log"):
            try:
                lp = (settings.get("log_path", "") or "").strip()
                if not lp:
                    lp = os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "GitPush.log")
                with open(lp, "a", encoding="utf-8") as f:
                    f.write(line)
            except Exception:
                pass

        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, line)
        # 行数上限截断（超出自动删除最旧的行）
        try:
            max_lines = max(50, int(settings.get("log_max_lines", 1000) or 1000))
            cnt = int(self.log_box.index("end-1c").split(".")[0])
            if cnt > max_lines:
                self.log_box.delete("1.0", f"{cnt - max_lines + 1}.0")
        except Exception:
            pass
        self.log_box.configure(state="disabled")
        self.log_box.see(tk.END)

    def set_status(self, text):
        self.root.after(0, self.status_var.set, text)

    # ---------------------------------------------------------------- 运行
    def start_push(self):
        if self.running:
            return
        settings = self._load_settings()

        # 推送前确认
        if settings.get("confirm_push"):
            if not messagebox.askyesno("确认推送", "确定要推送当前的更改吗？"):
                return

        path = self.path_var.get().strip()
        repo = self.repo_var.get().strip()
        branch = self.branch_var.get().strip() or "main"
        remote = self.remote_var.get().strip() or "origin"
        force = self.force_var.get()

        # 强制推送二次确认
        if force and settings.get("confirm_force"):
            if not messagebox.askyesno("强制推送确认",
                                       "你勾选了强制推送（--force），这会覆盖远程历史，确定要继续吗？"):
                return

        # 提交信息：启用模板则按模板生成，否则用主窗口填写的内容
        if settings.get("commit_template_enabled") and settings.get("commit_template", "").strip():
            commit = self._fill_template(settings["commit_template"], branch)
        else:
            commit = self.commit_var.get().strip() or "Auto push by Git Push工具"

        # 其他推送行为设置
        add_mode = settings.get("add_mode", "all")
        push_tags = bool(settings.get("push_tags", False))
        auto_tag = settings.get("auto_tag", "").strip()
        allow_empty = bool(settings.get("allow_empty", False))
        no_verify = bool(settings.get("no_verify", False))
        gpg_sign = bool(settings.get("gpg_sign", False))
        amend = bool(settings.get("amend", False))
        pull_before_push = bool(settings.get("pull_before_push", False))
        try:
            retry_on_fail = max(0, int(settings.get("retry_on_fail", 0) or 0))
        except Exception:
            retry_on_fail = 0
        use_proxy = bool(settings.get("use_proxy", False))
        proxy_url = settings.get("proxy_url", "").strip()
        # 新增：Git 身份 / 概览 / 通知 / 整理
        default_user_name = settings.get("default_user_name", "").strip()
        default_user_email = settings.get("default_user_email", "").strip()
        diff_preview = bool(settings.get("diff_preview", False))
        desktop_notify = bool(settings.get("desktop_notify", False))
        play_sound = bool(settings.get("play_sound", False))
        auto_gc = bool(settings.get("auto_gc", False))

        if not path:
            messagebox.showerror("出错啦", "请先选择要 Push 的文件夹或文件")
            return
        if not repo:
            messagebox.showerror("出错啦", "请填写要 Push 的远程仓库地址")
            return
        if not os.path.exists(path):
            messagebox.showerror("出错啦", "填的路径不存在请检查一下")
            return

        # 记住本次选择的路径（供「记住路径」功能使用）
        try:
            if settings.get("remember_path") and path:
                s2 = dict(settings)
                s2["last_path"] = path
                self._save_settings(s2)
        except Exception:
            pass

        self.running = True
        self.root.after(0, lambda: self.push_btn.config(state="disabled"))
        self.set_status("正在推送中…")
        t = threading.Thread(target=self.do_push,
                             args=(path, repo, branch, commit, remote, force,
                                   add_mode, push_tags, auto_tag,
                                   allow_empty, no_verify, gpg_sign, amend,
                                   pull_before_push, retry_on_fail,
                                   use_proxy, proxy_url,
                                   default_user_name, default_user_email,
                                   diff_preview, desktop_notify,
                                   play_sound, auto_gc),
                             daemon=True)
        t.start()

    def _git_exe(self):
        """返回 git 可执行文件：未配置则使用系统 git。"""
        try:
            p = (self._load_settings().get("git_path", "") or "").strip()
        except Exception:
            p = ""
        return p if p else "git"

    def run(self, cmd, cwd):
        """执行一条 git 命令，把输出实时写进日志，返回 returncode。"""
        # 支持自定义 git 路径：把命令首元素 git 替换为配置的路径
        if cmd and cmd[0] == "git":
            cmd = [self._git_exe()] + cmd[1:]
        self.log("💻 " + " ".join(cmd))
        t0 = time.perf_counter()
        try:
            proc = subprocess.Popen(
                cmd, cwd=cwd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            for line in proc.stdout:
                self.log(line.rstrip())
            proc.wait()
            dt = time.perf_counter() - t0
            self.log(f"⏱ 命令完成，耗时 {dt:.2f}s，返回码 {proc.returncode}")
            return proc.returncode
        except FileNotFoundError:
            self.log("❌ 找不到 git 命令，请确认 git 已安装并在 PATH 中")
            return 1
        except Exception as e:
            self.log(f"❌ 执行命令时出错：{e}")
            return 1

    def _git_out(self, args, cwd):
        """安全地取 git 命令的 stdout 文本，永不返回 None """
        try:
            r = subprocess.run([self._git_exe()] + args, cwd=cwd,
                               capture_output=True, text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            return r.stdout or ""
        except Exception:
            return ""

    def do_push(self, path, repo, branch, commit, remote, force,
                add_mode="all", push_tags=False, auto_tag="",
                allow_empty=False, no_verify=False, gpg_sign=False,
                amend=False, pull_before_push=False, retry_on_fail=0,
                use_proxy=False, proxy_url="",
                default_user_name="", default_user_email="",
                diff_preview=False, desktop_notify=False,
                play_sound=False, auto_gc=False):
        t_start = time.perf_counter()
        # 参数汇总（一次性打全，运行日志更完整）
        self.log("═" * 52)
        self.log(f"🚀 开始推送 · 分支 <{branch}> · 远程 <{remote}>"
                 f"{' · 强制' if force else ''}")
        self.log(f"   本地路径 ：{path}")
        self.log(f"   远程仓库 ：{repo}")
        self.log(f"   提交信息 ：{commit}")
        self.log(f"   选项     ：add={add_mode} · 标签={auto_tag or '无'} · "
                 f"pull={pull_before_push} · 重试={retry_on_fail}")
        self.log("═" * 52)
        try:
            # 代理参数（仅作用到 push / pull 这类网络命令）
            proxy_args = []
            if use_proxy and proxy_url:
                proxy_args = ["-c", f"http.proxy={proxy_url}",
                              "-c", f"https.proxy={proxy_url}"]

            # 单个文件 -> 用所在目录作为仓库根，并只 add 该文件
            if os.path.isfile(path):
                repo_dir = os.path.dirname(path)
                add_target = os.path.basename(path)
                self.log(f"📄 检测到单个文件，仓库目录：{repo_dir}")
            else:
                repo_dir = path
                add_target = "."
                self.log(f"📂 仓库目录：{repo_dir}")

            # 1) 是否已是 git 仓库
            inside = self._git_out(["rev-parse", "--is-inside-work-tree"], repo_dir).strip().lower()
            if inside != "true":
                self.log("🔧 还不是 Git 仓库，正在 git init")
                self.run(["git", "init"], repo_dir)
                self.run(["git", "checkout", "-B", branch], repo_dir)
            else:
                self.log("✅ 已经是 Git 仓库啦~")
                cur = self._git_out(["branch", "--show-current"], repo_dir).strip()
                self.log(f"   当前本地分支：{cur or '(分离头指针 / 未知)'}")

            # 2) 检查 / 自动配置 user 身份
            name = self._git_out(["config", "user.name"], repo_dir).strip()
            email = self._git_out(["config", "user.email"], repo_dir).strip()
            if not name or not email:
                if default_user_name or default_user_email:
                    self.log("⚙️ 仓库未配置 user 身份，按「设置」自动写入默认身份")
                    if default_user_name:
                        self.run(["git", "config", "user.name", default_user_name], repo_dir)
                        self.log(f"   user.name = {default_user_name}")
                    if default_user_email:
                        self.run(["git", "config", "user.email", default_user_email], repo_dir)
                        self.log(f"   user.email = {default_user_email}")
                else:
                    self.log("⚠️ 此仓库（及全局）未配置 user.name / user.email，commit 可能失败")
                    self.log("   可在命令行先执行：")
                    self.log("   git config --global user.name \"你的名字\"")
                    self.log("   git config --global user.email \"你的邮箱\"")

            # 3) 认证提示
            if repo.startswith("https://") and "@" not in repo:
                self.log("🔐 提示：HTTPS 地址未带凭证。若本机未缓存 Git 凭证可能会弹窗或失败")
                self.log("   方案 A：用已缓存凭证的系统的凭据管理器；")
                self.log("   方案 B：地址写成 https://<TOKEN>@github.com/用户/仓库.git")

            # 4) git add（按设置的 add 方式）
            if add_mode == "all":
                self.log("➕ 添加所有改动（git add -A）")
                self.run(["git", "add", "-A"], repo_dir)
            elif add_mode == "update":
                self.log("➕ 添加已跟踪文件的修改（git add -u）")
                self.run(["git", "add", "-u"], repo_dir)
            else:
                self.log(f"➕ 添加所选内容：{add_target}")
                self.run(["git", "add", add_target], repo_dir)

            # 4.5) 暂存区文件清单（信息更丰富）
            staged = [x for x in self._git_out(
                ["diff", "--cached", "--name-only"], repo_dir).strip().splitlines() if x]
            self.log(f"📊 已暂存文件数：{len(staged)}")
            for f in staged[:25]:
                self.log(f"   + {f}")
            if len(staged) > 25:
                self.log(f"   … 其余 {len(staged) - 25} 个文件省略")

            # 4.6) 推送前改动概览
            if diff_preview:
                self.log("🔍 推送前改动概览 (git diff --stat)：")
                for line in self._git_out(["diff", "--stat", "HEAD"], repo_dir).strip().splitlines():
                    if line:
                        self.log("   " + line)

            # 4.7) 提交前整理仓库
            if auto_gc:
                self.log("🧹 提交前自动整理仓库 (git gc --auto)")
                self.run(["git", "gc", "--auto"], repo_dir)

            # 5) git commit
            commit_cmd = ["git", "commit", "-m", commit]
            if amend:
                commit_cmd = ["git", "commit", "--amend", "-m", commit]
            if no_verify:
                commit_cmd.append("--no-verify")
            if gpg_sign:
                commit_cmd.append("--gpg-sign")
            committed = False
            if amend:
                self.run(commit_cmd, repo_dir)
                committed = True
            else:
                status = self._git_out(["status", "--porcelain"], repo_dir).strip()
                if status or allow_empty:
                    if allow_empty and not status:
                        self.log("💡 没有新改动，但已开启「允许空提交」，仍创建空提交")
                    self.run(commit_cmd, repo_dir)
                    committed = True
                else:
                    self.log("💡 没有新的改动，跳过 commit")

            if committed:
                new_hash = self._git_out(["rev-parse", "HEAD"], repo_dir).strip()
                self.log(f"🆔 本次提交：{new_hash[:12] if new_hash else '未知'}")

            # 6) git remote
            remotes = self._git_out(["remote"], repo_dir).split()
            if remote in remotes:
                self.run(["git", "remote", "set-url", remote, repo], repo_dir)
            else:
                self.run(["git", "remote", "add", remote, repo], repo_dir)
            remote_url = self._git_out(["remote", "get-url", remote], repo_dir).strip()
            self.log(f"🔗 远程 {remote} 地址：{remote_url}")

            # 6.5) 确定要推送的本地 ref —— 修复 issue #2「src refspec main does not match any」
            local_branches = [b.strip() for b in
                              self._git_out(["branch", "--format=%(refname:short)"], repo_dir).split()
                              if b.strip()]
            head_branch = self._git_out(["rev-parse", "--abbrev-ref", "HEAD"], repo_dir).strip()

            if branch in local_branches:
                push_ref = branch
            elif head_branch and head_branch != "HEAD" and head_branch in local_branches:
                push_ref = f"{head_branch}:{branch}"
                self.log(f"ℹ️ 本地没有名为 '{branch}' 的分支，将把当前分支 '{head_branch}' 推送到远程分支 '{branch}'")
            else:
                self.log(f"⚠️ 本地不存在分支 '{branch}'，也没有其他可推送的本地分支。")
                if not local_branches:
                    self.log("   这看起来是个还没有任何提交的新仓库——请先添加文件再提交。")
                self.log("   若为分支名填写错误，请修改「分支」框后重试。")
                self.set_status("❌ 推送失败：本地无对应分支")
                self.running = False
                self.root.after(0, lambda: self.push_btn.config(state="normal"))
                return

            # 6.8) 推送前自动打标签
            if auto_tag:
                self.log(f"🏷️ 自动打标签：{auto_tag}")
                self.run(["git", "tag", "-f", auto_tag], repo_dir)

            # 6.9) 推送前先拉取并变基（可选）
            if pull_before_push:
                self.log("⬇️ 推送前先拉取并变基（git pull --rebase）")
                self.run(["git"] + proxy_args + ["pull", "--rebase", remote, branch], repo_dir)

            # 7) git push（支持失败重试）
            cmd = ["git"] + proxy_args + ["push"]
            if force:
                cmd.append("--force")
            if push_tags:
                cmd.append("--follow-tags")
            cmd += ["-u", remote, push_ref]
            self.log(f"📤 推送命令：{' '.join(cmd)}")
            attempts = 1 + max(0, int(retry_on_fail or 0))
            rc = 1
            for attempt in range(1, attempts + 1):
                if attempt > 1:
                    self.log(f"🔁 第 {attempt} 次重试推送…")
                rc = self.run(cmd, repo_dir)
                if rc == 0:
                    break

            # 7.5) 推送自动打的标签
            if rc == 0 and auto_tag:
                self.run(["git", "push", "-u", remote, auto_tag], repo_dir)

            total = time.perf_counter() - t_start
            if rc == 0:
                self.log(f"🎉 推送成功！总耗时 {total:.2f}s")
                self.set_status("✅ 推送成功")
                self._report_event("push")
                if play_sound:
                    self._beep(True)
                if desktop_notify:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "推送完成", f"推送成功！\n耗时 {total:.1f}s"))
            else:
                # 尝试从日志里抓取常见失败原因，给出更直白的提示
                self.log("⚠️ 推送失败，请查看上方日志找原因（多半是凭证或分支冲突）")
                self.set_status("❌ 推送失败")
                if play_sound:
                    self._beep(False)
                if desktop_notify:
                    self.root.after(0, lambda: messagebox.showerror(
                        "推送完成", "推送失败，请查看运行日志"))
        except Exception as e:
            self.log(f"❌ 发生异常：{e}")
            self.set_status("❌ 出错")
        finally:
            self.running = False
            self.root.after(0, lambda: self.push_btn.config(state="normal"))

    def _beep(self, ok=True):
        """推送结束播放提示音：成功高音、失败低音。任何异常静默。"""
        try:
            import winsound
            winsound.Beep(880 if ok else 320, 180)
        except Exception:
            pass

    # ---------------------------------------------------------------- 帮助
    def _show_help(self):
        msg = (
            "【Git Push 工具 · 使用说明】\n\n"
            "1. 点「选择文件夹」或「选择文件」，指定要推送的本地内容。\n"
            "2. 在「远程仓库」填入仓库地址，例如：\n"
            "      https://github.com/用户名/仓库.git\n"
            "   （GitHub 等平台现在不支持密码，HTTPS 建议在地址里嵌入 token：\n"
            "      https://<TOKEN>@github.com/用户名/仓库.git ）\n"
            "3. 分支名默认 main，远程名默认 origin，可按需修改。\n"
            "4. 点「开始推送」，工具会自动完成：\n"
            "      git init（若还不是仓库）→ add → commit → remote → push\n"
            "5. 日志区会实时显示每一步输出，失败时可据此排查\n\n"
            "注意：本机需已安装 git 并能在命令行直接调用。"
        )
        messagebox.showinfo("使用说明", msg)

    def _show_about(self):
        messagebox.showinfo("关于",
                            f"{APP_TITLE}\n版本 {APP_VERSION}\n\n"
                            "由小红蛋精心编写的Git 推送工具")

    def _open_issues(self):
        issues_url = "https://github.com/NekoAiDev/Git-Push/issues"
        try:
            webbrowser.open(issues_url, new=2)
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开浏览器：{e}\n可手动访问：{issues_url}")

    # ---------------------------------------------------------------- 更新
    # ---------------------------------------------------------------- 统计/合规
    def _stats_path(self):
        try:
            base = os.path.dirname(os.path.abspath(sys.executable))
        except Exception:
            base = os.getcwd()
        return os.path.join(base, "stats.json")

    def _settings_path(self):
        try:
            base = os.path.dirname(os.path.abspath(sys.executable))
        except Exception:
            base = os.getcwd()
        return os.path.join(base, "settings.json")

    def _init_stats(self):
        self.started_at = int(time.time())
        self.stats_path = self._stats_path()
        self.stats = {"uuid": "", "push_count": 0, "update_count": 0,
                      "consent": True, "first_run": 0, "last_run": 0}
        try:
            if os.path.exists(self.stats_path):
                with open(self.stats_path, "r", encoding="utf-8") as f:
                    self.stats.update(json.load(f))
        except Exception:
            pass
        if not self.stats.get("uuid"):
            try:
                self.stats["uuid"] = str(_uuid.uuid4())
            except Exception:
                self.stats["uuid"] = "anon-" + str(int(time.time()))

    def _save_stats(self):
        try:
            with open(self.stats_path, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _maybe_ask_consent(self):
        if self.stats.get("consent") is not None:
            return
        try:
            ans = messagebox.askyesno(
                "匿名使用统计",
                "为了持续改进 Git Push 工具，我们想收集极少量的匿名使用数据，\n"
                "例如：推送成功次数、更新次数、使用时长（仅统计，不含任何文件/仓库/隐私）。\n\n"
                "是否同意在您使用时发送这些匿名统计数据？"
            )
            self.stats["consent"] = bool(ans)
            self._save_stats()
        except Exception:
            pass

    def _open_data_collection(self):
        """服务菜单「使用收集」入口：打开独立设置窗口，不再弹 messagebox 阻塞提示。"""
        try:
            win = tk.Toplevel(self.root)
            win.title("使用收集 - 匿名统计")
            win.geometry("470x250")
            win.transient(self.root)
            win.resizable(False, False)

            cur = bool(self.stats.get("consent", True))
            var = tk.BooleanVar(value=cur)

            ttk.Label(win, text="匿名使用统计",
                      font=("Microsoft YaHei", 13, "bold")).pack(pady=(14, 6))
            ttk.Label(win,
                      text="默认已开启匿名使用统计。\n"
                           "我们仅收集极少量匿名数据（推送次数 / 更新次数 / 使用时长），\n"
                           "不含任何文件、仓库路径或个人隐私。",
                      justify="left", wraplength=410).pack(padx=18)
            ttk.Checkbutton(win, text="允许发送匿名使用统计", variable=var).pack(pady=(10, 4))

            def _save():
                try:
                    self.stats["consent"] = bool(var.get())
                    self._save_stats()
                except Exception:
                    pass
                win.destroy()

            btn = ttk.Frame(win)
            btn.pack(side="bottom", fill="x", padx=14, pady=10)
            ttk.Button(btn, text="保存", command=_save).pack(side="right", padx=(6, 0))
            ttk.Button(btn, text="取消", command=win.destroy).pack(side="right")
        except Exception:
            pass

    def _load_settings(self):
        defaults = {
            "remote_repo": "",
            "branch": "main",
            "remote_name": "origin",
            "commit_msg": "Auto push by Git Push工具",
            "force_push": False,
            "auto_fill": False,
            "last_path": "",              # 记住上次选择的本地路径
            # 提交信息模板
            "commit_template_enabled": False,
            "commit_template": "Auto push {date} {time}",
            # 提交选项
            "allow_empty": False,         # git commit --allow-empty
            "no_verify": False,           # git commit --no-verify（跳过钩子）
            "gpg_sign": False,            # git commit --gpg-sign
            "amend": False,               # git commit --amend（追加到上次提交）
            # 推送行为
            "add_mode": "all",            # all / update / selected
            "push_tags": False,           # push 时 --follow-tags
            "auto_tag": "",               # 推送前自动打的标签名（留空不打）
            "pull_before_push": False,    # push 前 git pull --rebase
            "retry_on_fail": 0,           # push 失败重试次数（0=不重试）
            # 网络
            "use_proxy": False,           # 使用 HTTP/HTTPS 代理
            "proxy_url": "",              # 代理地址，如 http://127.0.0.1:7890
            # Git 身份（仓库未配置 user.name/email 时自动应用，避免 commit 失败）
            "default_user_name": "",      # 默认 Git 用户名
            "default_user_email": "",     # 默认 Git 邮箱
            # 推送高级补充
            "git_path": "",               # 自定义 git 可执行文件路径（留空=系统 git）
            "confirm_force": False,       # 强制推送前再弹一次二次确认
            "diff_preview": False,        # 推送前在日志打印改动概览 (git diff --stat)
            "auto_gc": False,             # 提交前自动 git gc --auto 整理仓库
            # 日志
            "log_timestamp": True,        # 每条日志加 [HH:MM:SS] 前缀
            "log_max_lines": 1000,        # 日志最大行数（超出自动截断）
            "save_log": False,            # 推送日志自动保存到文件
            "log_path": "",               # 日志文件路径（留空=程序同目录 GitPush.log）
            "log_font_size": 10,          # 运行日志字体大小
            # 通知与外观
            "desktop_notify": False,      # 推送结束后弹窗报告成功/失败
            "play_sound": False,          # 推送结束播放提示音
            "maximize_on_start": False,   # 启动时窗口最大化
            # 隐私与统计
            "allow_stats": True,          # 允许发送匿名使用统计（默认开启）
            # 自动与界面
            "auto_check_update": True,    # 启动后静默检查更新
            "skip_version": "",           # 跳过提示的版本号（留空=不跳过）
            "topmost": False,             # 窗口置顶
            "confirm_push": False,        # 推送前确认
            "remember_path": False,       # 启动时自动填入上次选择的路径
            "confirm_exit": False,         # 关闭窗口时确认（防误关）
        }
        try:
            path = self._settings_path()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        defaults.update(loaded)
        except Exception:
            pass
        return defaults

    def _save_settings(self, settings):
        try:
            with open(self._settings_path(), "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _apply_settings(self):
        settings = self._load_settings()
        # 运行日志字体大小
        try:
            fs = int(settings.get("log_font_size", 10))
            fs = max(7, min(20, fs))
            self.log_box.configure(font=("Consolas", fs))
        except Exception:
            pass
        # 启动时窗口最大化
        try:
            if settings.get("maximize_on_start"):
                self.root.state("zoomed")
        except Exception:
            pass
        # 界面：窗口置顶
        try:
            self.root.attributes("-topmost", bool(settings.get("topmost", False)))
        except Exception:
            pass
        # 自动检查更新（后台静默，仅在发现新版本时提示）
        try:
            if settings.get("auto_check_update", True):
                self.root.after(2500, self._background_check_update)
        except Exception:
            pass
        # 记住路径：仅在当前未填写时自动填入上次路径
        if settings.get("remember_path") and not self.path_var.get().strip():
            lp = settings.get("last_path", "").strip()
            if lp and os.path.exists(lp):
                self.path_var.set(lp)
        # 自动填入默认推送信息
        if not settings.get("auto_fill"):
            return
        if settings.get("remote_repo"):
            self.repo_var.set(settings["remote_repo"])
        if settings.get("branch"):
            self.branch_var.set(settings["branch"])
        if settings.get("remote_name"):
            self.remote_var.set(settings["remote_name"])
        if settings.get("commit_msg"):
            self.commit_var.set(settings["commit_msg"])
        self.force_var.set(bool(settings.get("force_push", False)))

    def _on_close(self):
        try:
            settings = self._load_settings()
        except Exception:
            settings = {}
        if settings.get("confirm_exit"):
            try:
                if self.running:
                    if not messagebox.askyesno("退出确认", "正在推送中，确定要退出吗？"):
                        return
                else:
                    if not messagebox.askyesno("退出确认", "确定要退出 Git Push 工具吗？"):
                        return
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def _fill_template(self, tpl, branch):
        """把提交信息模板里的占位符替换成实际值。"""
        now = datetime.now()
        return (tpl
                .replace("{date}", now.strftime("%Y-%m-%d"))
                .replace("{time}", now.strftime("%H:%M:%S"))
                .replace("{datetime}", now.strftime("%Y-%m-%d %H:%M:%S"))
                .replace("{branch}", branch or ""))

    def _version_lt(self, cur, remote):
        """返回 True 表示 remote 版本比 cur 新。"""
        def parse(v):
            parts = []
            for x in re.split(r"[.\-]", str(v)):
                parts.append(int(x) if x.isdigit() else 0)
            return parts
        try:
            a, b = parse(cur), parse(remote)
            n = max(len(a), len(b))
            a += [0] * (n - len(a))
            b += [0] * (n - len(b))
            return a < b
        except Exception:
            return False

    def _urlopen_with_proxy(self, req, timeout=8):
        """发起 HTTP 请求；若设置了代理则走 HTTP/HTTPS 代理。"""
        try:
            settings = self._load_settings()
        except Exception:
            settings = {}
        proxy = (settings.get("proxy_url", "") or "").strip()
        if settings.get("use_proxy") and proxy:
            try:
                handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
                opener = urllib.request.build_opener(handler)
                return opener.open(req, timeout=timeout)
            except Exception:
                pass
        return urllib.request.urlopen(req, timeout=timeout)

    def _background_check_update(self):
        """后台静默检查更新，仅发现新版本时弹窗提示，不主动打扰。"""
        try:
            req = urllib.request.Request(
                "https://install.nekoaidev.top/version.json",
                headers={"User-Agent": "GitPush"})
            with self._urlopen_with_proxy(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            remote_ver = data.get("version", "")
            if self._version_lt(APP_VERSION, remote_ver):
                try:
                    skip = self._load_settings().get("skip_version", "") or ""
                except Exception:
                    skip = ""
                if str(skip).strip() == str(remote_ver).strip():
                    return  # 用户已选择跳过此版本
                messagebox.showinfo(
                    "发现新版本",
                    f"检测到新版本 {remote_ver}（当前 {APP_VERSION}）\n\n"
                    f"请在菜单「更新」→「检查更新」中进行升级")
        except Exception:
            pass

    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("设置 - 推送与行为")
        win.geometry("600x680")
        win.transient(self.root)
        win.resizable(False, True)

        settings = self._load_settings()

        # 可滚动容器（设置项较多，整体可滚动查看）
        _sc = ttk.Scrollbar(win, orient="vertical")
        _cv = tk.Canvas(win, yscrollcommand=_sc.set, borderwidth=0, highlightthickness=0)
        _sc.config(command=_cv.yview)
        _cv.pack(side="left", fill="both", expand=True)
        _sc.pack(side="right", fill="y")
        content = ttk.Frame(_cv, padding=(2, 2))
        _cwin = _cv.create_window((0, 0), window=content, anchor="nw")
        content.bind("<Configure>", lambda e: _cv.configure(scrollregion=_cv.bbox("all")))
        _cv.bind("<Configure>", lambda e: _cv.itemconfig(_cwin, width=e.width))
        _cv.bind_all("<MouseWheel>", lambda e: _cv.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # 通用变量
        auto_fill_var = tk.BooleanVar(value=bool(settings.get("auto_fill", False)))
        repo_var = tk.StringVar(value=settings.get("remote_repo", ""))
        branch_var = tk.StringVar(value=settings.get("branch", "main"))
        remote_var = tk.StringVar(value=settings.get("remote_name", "origin"))
        commit_var = tk.StringVar(value=settings.get("commit_msg", "Auto push by Git Push工具"))
        force_var = tk.BooleanVar(value=bool(settings.get("force_push", False)))
        add_mode_var = tk.StringVar(value=settings.get("add_mode", "all"))
        push_tags_var = tk.BooleanVar(value=bool(settings.get("push_tags", False)))
        auto_tag_var = tk.StringVar(value=settings.get("auto_tag", ""))
        tmpl_enabled_var = tk.BooleanVar(value=bool(settings.get("commit_template_enabled", False)))
        tmpl_var = tk.StringVar(value=settings.get("commit_template", "Auto push {date} {time}"))
        # 提交选项
        allow_empty_var = tk.BooleanVar(value=bool(settings.get("allow_empty", False)))
        no_verify_var = tk.BooleanVar(value=bool(settings.get("no_verify", False)))
        gpg_sign_var = tk.BooleanVar(value=bool(settings.get("gpg_sign", False)))
        amend_var = tk.BooleanVar(value=bool(settings.get("amend", False)))
        # 推送前拉取 / 重试
        pull_var = tk.BooleanVar(value=bool(settings.get("pull_before_push", False)))
        retry_var = tk.StringVar(value=str(settings.get("retry_on_fail", 0)))
        # 网络
        proxy_en_var = tk.BooleanVar(value=bool(settings.get("use_proxy", False)))
        proxy_url_var = tk.StringVar(value=settings.get("proxy_url", ""))
        # 日志
        ts_var = tk.BooleanVar(value=bool(settings.get("log_timestamp", True)))
        maxlines_var = tk.StringVar(value=str(settings.get("log_max_lines", 1000)))
        save_log_var = tk.BooleanVar(value=bool(settings.get("save_log", False)))
        logpath_var = tk.StringVar(value=settings.get("log_path", ""))
        # 隐私与统计
        stats_var = tk.BooleanVar(value=bool(settings.get("allow_stats", True)))
        # 自动与界面
        auto_check_var = tk.BooleanVar(value=bool(settings.get("auto_check_update", True)))
        topmost_var = tk.BooleanVar(value=bool(settings.get("topmost", False)))
        confirm_var = tk.BooleanVar(value=bool(settings.get("confirm_push", False)))
        remember_var = tk.BooleanVar(value=bool(settings.get("remember_path", False)))
        confirm_exit_var = tk.BooleanVar(value=bool(settings.get("confirm_exit", False)))
        # Git 身份
        user_name_var = tk.StringVar(value=settings.get("default_user_name", ""))
        user_email_var = tk.StringVar(value=settings.get("default_user_email", ""))
        # 推送高级补充
        git_path_var = tk.StringVar(value=settings.get("git_path", ""))
        confirm_force_var = tk.BooleanVar(value=bool(settings.get("confirm_force", False)))
        diff_preview_var = tk.BooleanVar(value=bool(settings.get("diff_preview", False)))
        auto_gc_var = tk.BooleanVar(value=bool(settings.get("auto_gc", False)))
        # 通知与外观
        desktop_notify_var = tk.BooleanVar(value=bool(settings.get("desktop_notify", False)))
        play_sound_var = tk.BooleanVar(value=bool(settings.get("play_sound", False)))
        log_font_var = tk.StringVar(value=str(settings.get("log_font_size", 10)))
        maximize_var = tk.BooleanVar(value=bool(settings.get("maximize_on_start", False)))
        # 更新
        skip_ver_var = tk.StringVar(value=settings.get("skip_version", ""))

        add_mode_map = {"all": "全部文件 (git add -A)",
                        "update": "仅已跟踪修改 (git add -u)",
                        "selected": "仅所选路径 / 文件"}
        add_mode_rev = {v: k for k, v in add_mode_map.items()}

        # ---- 默认推送信息 ----
        frm1 = ttk.LabelFrame(content, text="默认推送信息", padding=(12, 8))
        frm1.pack(fill="x", padx=14, pady=(6, 4))
        ttk.Label(frm1, text="远程仓库：").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(frm1, textvariable=repo_var).grid(row=0, column=1, sticky="ew", padx=(0, 6))
        ttk.Label(frm1, text="例：https://github.com/用户名/仓库.git", style="Small.TLabel").grid(row=1, column=1, sticky="w")
        ttk.Label(frm1, text="分支名：").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(frm1, textvariable=branch_var, width=16).grid(row=2, column=1, sticky="w", padx=(0, 6))
        ttk.Label(frm1, text="远程名：").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Entry(frm1, textvariable=remote_var, width=12).grid(row=3, column=1, sticky="w", padx=(0, 6))
        ttk.Label(frm1, text="提交信息：").grid(row=4, column=0, sticky="w", pady=3)
        ttk.Entry(frm1, textvariable=commit_var).grid(row=4, column=1, sticky="ew", padx=(0, 6))
        ttk.Checkbutton(frm1, text="强制推送 --force（危险！仅私人分支使用）", variable=force_var).grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 0))
        frm1.columnconfigure(1, weight=1)

        # ---- Git 身份 ----
        frm_id = ttk.LabelFrame(content, text="Git 身份（仓库未配置时自动应用）", padding=(12, 8))
        frm_id.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Label(frm_id, text="默认用户名：").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(frm_id, textvariable=user_name_var).grid(row=0, column=1, sticky="ew", padx=(0, 6))
        ttk.Label(frm_id, text="默认邮箱：").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(frm_id, textvariable=user_email_var).grid(row=1, column=1, sticky="ew", padx=(0, 6))
        ttk.Label(frm_id, text="仅当仓库及全局未配置 git user.name/email 时自动写入，避免 commit 失败", style="Small.TLabel").grid(row=2, column=1, sticky="w")
        frm_id.columnconfigure(1, weight=1)

        # ---- 提交信息模板 ----
        frm2 = ttk.LabelFrame(content, text="提交信息模板", padding=(12, 8))
        frm2.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Checkbutton(frm2, text="启用提交信息模板（将覆盖上方“提交信息”）", variable=tmpl_enabled_var).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(frm2, text="模板：").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(frm2, textvariable=tmpl_var).grid(row=1, column=1, sticky="ew", padx=(0, 6))
        ttk.Label(frm2, text="可用占位符：{date} 日期  {time} 时间  {datetime} 日期时间  {branch} 分支", style="Small.TLabel").grid(row=2, column=1, sticky="w")
        frm2.columnconfigure(1, weight=1)

        # ---- 提交选项 ----
        frm_commit = ttk.LabelFrame(content, text="提交选项", padding=(12, 8))
        frm_commit.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Checkbutton(frm_commit, text="允许空提交 (--allow-empty)", variable=allow_empty_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(frm_commit, text="跳过 Git 钩子 (--no-verify，谨慎使用)", variable=no_verify_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(frm_commit, text="GPG 签名提交 (--gpg-sign，需本机已配置 GPG)", variable=gpg_sign_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(frm_commit, text="追加到上次提交 (--amend，不新建提交)", variable=amend_var).pack(anchor="w", pady=2)

        # ---- 推送行为 ----
        frm3 = ttk.LabelFrame(content, text="推送行为", padding=(12, 8))
        frm3.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Label(frm3, text="git add 方式：").grid(row=0, column=0, sticky="w", pady=3)
        add_cb = ttk.Combobox(frm3, textvariable=add_mode_var, state="readonly", width=26,
                              values=list(add_mode_map.values()))
        add_cb.set(add_mode_map.get(settings.get("add_mode", "all"), add_mode_map["all"]))
        add_cb.grid(row=0, column=1, sticky="w", padx=(0, 6))
        ttk.Checkbutton(frm3, text="推送时附带已注释标签 (--follow-tags)", variable=push_tags_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frm3, text="自动打标签：").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(frm3, textvariable=auto_tag_var, width=24).grid(row=2, column=1, sticky="w", padx=(0, 6))
        ttk.Label(frm3, text="留空不打；支持占位符 {date} {time} {branch}", style="Small.TLabel").grid(row=3, column=1, sticky="w")
        ttk.Checkbutton(frm3, text="推送前先拉取并变基 (git pull --rebase)", variable=pull_var).grid(row=4, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frm3, text="推送失败重试次数：").grid(row=5, column=0, sticky="w", pady=3)
        ttk.Entry(frm3, textvariable=retry_var, width=8).grid(row=5, column=1, sticky="w", padx=(0, 6))
        ttk.Label(frm3, text="0 = 不重试", style="Small.TLabel").grid(row=6, column=1, sticky="w")

        # ---- 推送高级补充 ----
        frm_adv = ttk.LabelFrame(content, text="推送高级补充", padding=(12, 8))
        frm_adv.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Label(frm_adv, text="自定义 git 路径（留空=系统 git）：").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(frm_adv, textvariable=git_path_var).grid(row=0, column=1, sticky="ew", padx=(0, 6))
        ttk.Checkbutton(frm_adv, text="强制推送前再弹一次二次确认（防误操作覆盖）", variable=confirm_force_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Checkbutton(frm_adv, text="推送前在日志打印改动概览 (git diff --stat)", variable=diff_preview_var).grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 0))
        ttk.Checkbutton(frm_adv, text="提交前自动整理仓库 (git gc --auto)", variable=auto_gc_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 0))
        frm_adv.columnconfigure(1, weight=1)

        # ---- 网络代理 ----
        frm_net = ttk.LabelFrame(content, text="网络代理", padding=(12, 8))
        frm_net.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Checkbutton(frm_net, text="使用 HTTP/HTTPS 代理（作用于推送 / 拉取与更新检查）", variable=proxy_en_var).pack(anchor="w", pady=2)
        ttk.Label(frm_net, text="代理地址：").pack(anchor="w", pady=(2, 0))
        ttk.Entry(frm_net, textvariable=proxy_url_var).pack(fill="x", pady=(0, 2))
        ttk.Label(frm_net, text="例：http://127.0.0.1:7890", style="Small.TLabel").pack(anchor="w")

        # ---- 日志 ----
        frm_log = ttk.LabelFrame(content, text="日志", padding=(12, 8))
        frm_log.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Checkbutton(frm_log, text="每条日志加时间戳 [HH:MM:SS]", variable=ts_var).pack(anchor="w", pady=2)
        ttk.Label(frm_log, text="日志最大行数（超出自动截断）：").pack(anchor="w", pady=(2, 0))
        ttk.Entry(frm_log, textvariable=maxlines_var, width=10).pack(anchor="w", pady=(0, 2))
        ttk.Checkbutton(frm_log, text="推送日志自动保存到文件", variable=save_log_var).pack(anchor="w", pady=(4, 0))
        ttk.Label(frm_log, text="保存路径（留空=程序同目录 GitPush.log）：").pack(anchor="w", pady=(2, 0))
        ttk.Entry(frm_log, textvariable=logpath_var).pack(fill="x", pady=(0, 2))

        # ---- 隐私与统计 ----
        frm_privacy = ttk.LabelFrame(content, text="隐私与统计", padding=(12, 8))
        frm_privacy.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Checkbutton(frm_privacy, text="允许发送匿名使用统计（默认开启，可随时关闭）", variable=stats_var).pack(anchor="w", pady=2)
        ttk.Label(frm_privacy, text="数据仅含：推送次数 / 更新次数 / 使用时长，不含任何文件、仓库或隐私", style="Small.TLabel").pack(anchor="w")

        # ---- 自动与界面 ----
        frm4 = ttk.LabelFrame(content, text="自动与界面", padding=(12, 8))
        frm4.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Checkbutton(frm4, text="下次启动时自动填入默认设置", variable=auto_fill_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(frm4, text="记住上次选择的本地路径（下次启动自动填入）", variable=remember_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(frm4, text="启动后自动检查更新（仅在发现新版本时提示）", variable=auto_check_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(frm4, text="窗口始终置顶显示", variable=topmost_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(frm4, text="推送前弹出确认框", variable=confirm_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(frm4, text="关闭窗口时确认（防止误关）", variable=confirm_exit_var).pack(anchor="w", pady=2)

        # ---- 通知与外观 ----
        frm_look = ttk.LabelFrame(content, text="通知与外观", padding=(12, 8))
        frm_look.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Checkbutton(frm_look, text="推送结束后弹窗报告成功/失败", variable=desktop_notify_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(frm_look, text="推送结束播放提示音（滴一声）", variable=play_sound_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(frm_look, text="启动时窗口最大化", variable=maximize_var).pack(anchor="w", pady=2)
        ttk.Label(frm_look, text="运行日志字体大小：").pack(anchor="w", pady=(2, 0))
        ttk.Entry(frm_look, textvariable=log_font_var, width=8).pack(anchor="w", pady=(0, 2))

        # ---- 更新 ----
        frm_upd = ttk.LabelFrame(content, text="更新", padding=(12, 8))
        frm_upd.pack(fill="x", padx=14, pady=(4, 4))
        ttk.Label(frm_upd, text="跳过提示的版本号（留空=不跳过）：").pack(anchor="w", pady=(2, 0))
        ttk.Entry(frm_upd, textvariable=skip_ver_var, width=16).pack(anchor="w", pady=(0, 2))
        ttk.Label(frm_upd, text="例：1.3.4 （填后该版本不再弹更新提示）", style="Small.TLabel").pack(anchor="w")

        def _save():
            try:
                retry_n = max(0, int(retry_var.get().strip() or 0))
            except Exception:
                retry_n = 0
            try:
                maxlines_n = max(50, int(maxlines_var.get().strip() or 1000))
            except Exception:
                maxlines_n = 1000
            new_settings = {
                "auto_fill": auto_fill_var.get(),
                "remote_repo": repo_var.get().strip(),
                "branch": branch_var.get().strip() or "main",
                "remote_name": remote_var.get().strip() or "origin",
                "commit_msg": commit_var.get().strip() or "Auto push by Git Push工具",
                "force_push": force_var.get(),
                "last_path": settings.get("last_path", ""),
                "add_mode": add_mode_rev.get(add_cb.get(), "all"),
                "push_tags": push_tags_var.get(),
                "auto_tag": auto_tag_var.get().strip(),
                "commit_template_enabled": tmpl_enabled_var.get(),
                "commit_template": tmpl_var.get().strip() or "Auto push {date} {time}",
                "allow_empty": allow_empty_var.get(),
                "no_verify": no_verify_var.get(),
                "gpg_sign": gpg_sign_var.get(),
                "amend": amend_var.get(),
                "pull_before_push": pull_var.get(),
                "retry_on_fail": retry_n,
                "use_proxy": proxy_en_var.get(),
                "proxy_url": proxy_url_var.get().strip(),
                "log_timestamp": ts_var.get(),
                "log_max_lines": maxlines_n,
                "save_log": save_log_var.get(),
                "log_path": logpath_var.get().strip(),
                "allow_stats": stats_var.get(),
                "auto_check_update": auto_check_var.get(),
                "topmost": topmost_var.get(),
                "confirm_push": confirm_var.get(),
                "remember_path": remember_var.get(),
                "confirm_exit": confirm_exit_var.get(),
                "default_user_name": user_name_var.get().strip(),
                "default_user_email": user_email_var.get().strip(),
                "git_path": git_path_var.get().strip(),
                "confirm_force": confirm_force_var.get(),
                "diff_preview": diff_preview_var.get(),
                "auto_gc": auto_gc_var.get(),
                "desktop_notify": desktop_notify_var.get(),
                "play_sound": play_sound_var.get(),
                "log_font_size": (lambda x: max(7, min(20, int(x) if str(x).strip().isdigit() else 10)))(log_font_var.get()),
                "maximize_on_start": maximize_var.get(),
                "skip_version": skip_ver_var.get().strip(),
            }
            self._save_settings(new_settings)
            # 隐私开关同步到统计配置
            try:
                self.stats["consent"] = bool(stats_var.get())
                self._save_stats()
            except Exception:
                pass
            try:
                self.root.attributes("-topmost", bool(new_settings.get("topmost", False)))
            except Exception:
                pass
            if new_settings["auto_fill"]:
                self._apply_settings()
            win.destroy()
            messagebox.showinfo("设置已保存", "设置已保存")

        btn_frm = ttk.Frame(win)
        btn_frm.pack(side="bottom", fill="x", padx=14, pady=(10, 10))
        ttk.Button(btn_frm, text="保存", command=_save).pack(side="right", padx=(6, 0))
        ttk.Button(btn_frm, text="取消", command=win.destroy).pack(side="right")

    def _report_event(self, event, join=False):
        # 仅在用户同意后才上报；仅发送匿名合法数据，绝不发送隐私
        if not self.stats.get("consent"):
            return
        try:
            if event == "push":
                self.stats["push_count"] = int(self.stats.get("push_count", 0)) + 1
            elif event == "update":
                self.stats["update_count"] = int(self.stats.get("update_count", 0)) + 1
            self.stats["last_run"] = int(time.time())
            self._save_stats()

            payload = {
                "uuid": self.stats.get("uuid", ""),
                "version": APP_VERSION,
                "event": event,
                "push_count": int(self.stats.get("push_count", 0)),
                "update_count": int(self.stats.get("update_count", 0)),
                "started_at": self.started_at,
                "session_ms": int((time.time() - self.started_at) * 1000),
                "ts": int(time.time()),
            }
            data = json.dumps(payload).encode("utf-8")

            def _post():
                try:
                    req = urllib.request.Request(
                        STATS_URL,
                        data=data,
                        headers={"Content-Type": "application/json",
                                 "User-Agent": "GitPush/" + APP_VERSION},
                        method="POST",
                    )
                    with self._urlopen_with_proxy(req, timeout=5) as resp:
                        resp.read()
                except Exception:
                    pass

            t = threading.Thread(target=_post, daemon=True)
            t.start()
            if join:
                t.join(3)
        except Exception:
            pass

    def _show_doc(self, title, text):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("720x560")
        win.transient(self.root)
        txt = scrolledtext.ScrolledText(win, wrap="word",
                                        font=("Microsoft YaHei", 11), padx=10, pady=10)
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", text)
        txt.configure(state="disabled")
        ttk.Button(win, text="关闭", command=win.destroy).pack(pady=8)

    def _open_updater(self):
        Updater(self.root, APP_VERSION).show()


class Updater:
    """从 GitHub 的 version.json 读取最新版本；发现新版本时下载更新压缩包，
    解压覆盖到工具所在目录，并重启程序。按钮按版本状态变灰 / 可点。"""

    def __init__(self, parent, current_version):
        self.parent = parent
        self.current_version = current_version
        self.window = None
        self.info = None
        self.update_url = None
        self.remote_ver_label = None
        self.status_var = None
        self.note_box = None
        self.log_box = None
        self.update_btn = None

    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("检查更新")
        self.window.geometry("520x560")
        self.window.minsize(480, 480)
        self.window.maxsize(720, 700)
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        ttk.Label(self.window, text="Git Push 工具更新",
                  style="Title.TLabel").pack(anchor="w", padx=14, pady=(12, 2))
        ttk.Label(self.window, text="从 GitHub 读取最新版本信息",
                  style="Small.TLabel").pack(anchor="w", padx=14)

        # 版本对比行
        info_frm = ttk.Frame(self.window)
        info_frm.pack(fill="x", padx=14, pady=(8, 6))
        ttk.Label(info_frm, text="当前版本：", font=("Microsoft YaHei", 10)).grid(row=0, column=0, sticky="w")
        ttk.Label(info_frm, text=self.current_version, font=("Microsoft YaHei", 10, "bold")).grid(row=0, column=1, sticky="w", padx=(4, 18))
        ttk.Label(info_frm, text="远程版本：", font=("Microsoft YaHei", 10)).grid(row=0, column=2, sticky="w")
        self.remote_ver_label = ttk.Label(info_frm, text="正在检查…", font=("Microsoft YaHei", 10, "bold"))
        self.remote_ver_label.grid(row=0, column=3, sticky="w")

        # 醒目状态横幅（一眼可见：有新版本 / 已最新 / 失败）
        self.banner = tk.Label(self.window, text="正在连接 GitHub，请稍候…",
                               font=("Microsoft YaHei", 12, "bold"),
                               bg="#FFF4CC", fg="#8a6d00", relief="flat",
                               padx=12, pady=10, anchor="center")
        self.banner.pack(fill="x", padx=14, pady=(2, 8))

        # 更新说明（固定高度，不撑大窗口，保证按钮始终可见）
        note_frm = ttk.LabelFrame(self.window, text="更新说明", padding=(10, 8))
        note_frm.pack(fill="x", padx=14, pady=(0, 8))
        self.note_box = scrolledtext.ScrolledText(note_frm, wrap="word",
                                                  font=("Microsoft YaHei", 11),
                                                  relief="flat", bd=0, padx=6, pady=4,
                                                  height=10)
        self.note_box.pack(fill="both", expand=True)
        self.note_box.configure(state="disabled")

        # 运行日志（默认隐藏，固定高度，不撑大窗口）
        self.log_frm = ttk.LabelFrame(self.window, text="运行日志", padding=(8, 6))
        self.log_box = scrolledtext.ScrolledText(self.log_frm, wrap="word",
                                                 font=("Consolas", 9), height=6)
        self.log_box.pack(fill="both", expand=True)
        self.log_box.configure(state="disabled")
        self.log_visible = False

        # 立即更新按钮（超大、彩色、占满一行，绝对不会看不到）
        self.update_btn = tk.Button(self.window, text="立即更新",
                                     command=self._do_update, state="disabled",
                                     font=("Microsoft YaHei", 13, "bold"),
                                     bg="#d9d9d9", fg="#888888",
                                     activebackground="#2f7a2f", activeforeground="white",
                                     relief="flat", cursor="hand2",
                                     padx=24, pady=12, height=1)
        self.update_btn.pack(fill="x", padx=14, pady=(0, 6))

        # 底部行：运行日志折叠 + 关闭
        bottom_frm = ttk.Frame(self.window)
        bottom_frm.pack(fill="x", padx=14, pady=(0, 12))
        self.toggle_btn = ttk.Button(bottom_frm, text="▼ 显示运行日志",
                                     command=self._toggle_log)
        self.toggle_btn.pack(side="left")
        ttk.Button(bottom_frm, text="关闭", command=self._on_close).pack(side="right")

        self._fetch_info()

    # ---------------------------------------------------------------- UI helpers
    def _safe_call(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except tk.TclError:
            pass
        except Exception:
            pass

    def _log(self, text):
        self.parent.after(0, lambda: self._safe_call(self._append_log, str(text)))

    def _append_log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see(tk.END)

    def _set_status(self, text):
        # 内部状态统一显示在醒目横幅上（原有的 status_var 标签已移除）
        self._set_banner(text, "info")

    def _set_remote_ver(self, text):
        self.parent.after(0, lambda: self._safe_call(self.remote_ver_label.config, {"text": text}))

    def _set_note(self, text):
        def _apply():
            self.note_box.configure(state="normal")
            self.note_box.delete("1.0", tk.END)
            self.note_box.insert(tk.END, text)
            self.note_box.configure(state="disabled")
        self.parent.after(0, lambda: self._safe_call(_apply))

    def _set_btn(self, text, enabled):
        state = "normal" if enabled else "disabled"
        if enabled:
            bg, fg = "#3a8f3a", "white"          # 绿底白字：可点
        else:
            bg, fg = "#d9d9d9", "#888888"        # 灰底灰字：不可点
        self.parent.after(0, lambda: self._safe_call(
            self.update_btn.config, {"text": text, "state": state, "bg": bg, "fg": fg}))

    def _set_banner(self, text, kind="info"):
        """设置醒目横幅文字与配色：info 黄 / update 橙 / ok 绿 / error 红。"""
        palette = {
            "info":   ("#FFF4CC", "#8a6d00"),
            "update": ("#FFE0B2", "#b35900"),
            "ok":     ("#E2F0D9", "#2e6b2e"),
            "error":  ("#F8D7DA", "#a1262b"),
        }
        bg, fg = palette.get(kind, palette["info"])
        self.parent.after(0, lambda: self._safe_call(
            self.banner.config, {"text": text, "bg": bg, "fg": fg}))

    def _toggle_log(self):
        self.log_visible = not self.log_visible
        if self.log_visible:
            # 日志区域固定高度，fill=x 横向撑满，但不 expand，避免把按钮挤出窗口
            self.log_frm.pack(fill="x", padx=14, pady=(0, 8), before=self.update_btn)
            self.toggle_btn.config(text="▲ 隐藏运行日志")
        else:
            self.log_frm.pack_forget()
            self.toggle_btn.config(text="▼ 显示运行日志")

    def _on_close(self):
        try:
            self.window.destroy()
        except Exception:
            pass

    # ---------------------------------------------------------------- version
    @staticmethod
    def _parse_version(v):
        s = re.sub(r"^[vV]", "", str(v))
        parts = []
        for p in s.split("."):
            try:
                parts.append(int(re.sub(r"[^0-9]", "", p) or "0"))
            except Exception:
                parts.append(0)
        return tuple(parts)

    def _compare_version(self, current, remote):
        cur = self._parse_version(current)
        rem = self._parse_version(remote)
        if cur > rem:
            return 1
        if cur < rem:
            return -1
        return 0

    # ---------------------------------------------------------------- fetch version.json
    def _fetch_info(self):
        def fetch():
            try:
                # 加时间戳绕过 raw 的 CDN 缓存，确保拿到最新 version.json
                url = VERSION_JSON_URL + "?t=" + str(int(time.time()))
                self._log(f"正在请求版本信息：{VERSION_JSON_URL}")
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                self.parent.after(0, self._on_info_ready, data)
            except Exception as e:
                self.parent.after(0, self._on_error, f"读取版本信息失败：{e}")
        threading.Thread(target=fetch, daemon=True).start()

    def _on_info_ready(self, data):
        remote_ver = str(data.get("version", "未知"))
        self._set_remote_ver(remote_ver)
        self.info = data
        # 兼容两种字段名：update_url 优先，url 兜底
        self.update_url = data.get("update_url") or data.get("url")

        notes = data.get("notes") or data.get("body") or "作者没有写更新说明"
        self._set_note(notes)

        if not self.update_url:
            self._set_banner("未找到更新包地址，无法自动更新", "error")
            self._log("❌ 远程没有配置更新包地址，无法自动更新")
            self._set_btn("无法更新", False)
            return

        cmp = self._compare_version(self.current_version, remote_ver)
        if cmp < 0:
            self._set_banner(f"🎉 发现新版本 v{remote_ver}，建议立即更新！", "update")
            self._log(f"✅ 发现新版本：{remote_ver}，点击「立即更新」即可下载替换")
            self._set_btn("立即更新", True)
        elif cmp > 0:
            self._set_banner("当前版本比远程还新，无需更新", "ok")
            self._log("💡 当前版本比远程还新，无需更新")
            self._set_btn("无需更新", False)
        else:
            self._set_banner("✅ 已经是最新版本啦", "ok")
            self._log("💡 已经是最新版本，无需更新")
            self._set_btn("无需更新", False)

    def _on_error(self, msg):
        self._set_banner("⚠️ 检查更新失败，请稍后重试", "error")
        self._set_remote_ver("—")
        self._log(f"❌ {msg}")
        self._set_btn("无法更新", False)

    # ---------------------------------------------------------------- download & replace (zip)
    def _do_update(self):
        if not self.update_url:
            messagebox.showerror("无法更新", "没有可用的下载链接")
            return
        self._set_btn("正在更新…", False)
        self._set_status("正在下载更新包…")
        self._log("开始下载更新压缩包，请稍候…")
        threading.Thread(target=self._download, daemon=True).start()

    def _download(self):
        try:
            tmp_dir = tempfile.gettempdir()
            zip_path = os.path.join(tmp_dir, "GitPush_update.zip")
            self._log(f"下载目标：{zip_path}")

            # 给更新包 URL 加时间戳，强制绕过 Worker / 中间缓存，确保每次拿到最新版
            sep = "&" if "?" in self.update_url else "?"
            url = f"{self.update_url}{sep}t={int(time.time())}"
            self._log(f"实际下载地址：{url}")

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 64 * 1024
                with open(zip_path, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = downloaded * 100 // total
                            self._set_status(f"下载进度：{pct}%")
                        else:
                            self._set_status(f"已下载：{downloaded // 1024} KB")

            self._set_status("下载完成，准备替换…")
            self._log("✅ 下载完成，正在准备替换…")
            self.parent.after(0, self._prepare_replace, zip_path)
        except Exception as e:
            self.parent.after(0, self._on_error, f"下载失败：{e}")
            self._set_btn("立即更新", True)

    def _prepare_replace(self, zip_path):
        if not getattr(sys, "frozen", False):
            self._log("⚠️ 当前是脚本运行模式，无法自动替换 exe")
            messagebox.showinfo(
                "开发模式",
                "当前运行的是 Python 脚本，无法自动替换 exe。\n"
                f"更新包已下载到：\n{zip_path}"
            )
            self._set_status("开发模式，未替换")
            self._set_btn("立即更新", True)
            return

        # 工具所在目录（exe 同级）
        install_dir = os.path.dirname(os.path.abspath(sys.executable))
        if not os.path.isdir(install_dir):
            self._log("❌ 找不到安装目录，无法替换")
            self._set_status("找不到安装目录")
            return

        # 生成替换脚本：检测写权限 → 无则提权 → 等旧进程退出 → 备份旧程序 → 解压覆盖 → 校验 → 启动新程序 → 清理
        bat_path = os.path.join(tempfile.gettempdir(), "update_gitpush.bat")
        bat = (
            "@echo off\n"
            "chcp 65001 >nul\n"
            f'set "INSTALL_DIR={install_dir}"\n'
            f'set "ZIP={zip_path}"\n'
            ":: 检测安装目录是否可写，不可写则请求管理员提权\n"
            'echo. > "%INSTALL_DIR%\\__wtest.tmp" 2>nul\n'
            'if exist "%INSTALL_DIR%\\__wtest.tmp" (\n'
            '  del "%INSTALL_DIR%\\__wtest.tmp" >nul 2>&1\n'
            ') else (\n'
            '  echo 需要管理员权限来更新，正在请求提权…\n'
            '  powershell -NoProfile -Command "Start-Process \'%~f0\' -Verb RunAs"\n'
            '  exit /b\n'
            ')\n'
            "echo 正在更新 Git Push 工具，请稍候…\n"
            ":: 等待旧 GitPush.exe 进程完全退出，避免覆盖失败\n"
            'for /L %%i in (1,1,30) do (\n'
            '  tasklist /FI "IMAGENAME eq GitPush.exe" /NH | find /I "GitPush.exe" >nul 2>&1\n'
            '  if errorlevel 1 goto :proc_done\n'
            '  timeout /t 1 /nobreak >nul\n'
            ')\n'
            ":proc_done\n"
            "timeout /t 1 /nobreak >nul\n"
            'if exist "%INSTALL_DIR%\\GitPush.exe" (\n'
            '  echo 正在备份旧程序…\n'
            '  move /Y "%INSTALL_DIR%\\GitPush.exe" "%INSTALL_DIR%\\GitPush.exe.old" >nul 2>&1\n'
            ')\n'
            'powershell -NoProfile -Command "try { Expand-Archive -Path \'%ZIP%\' -DestinationPath \'%INSTALL_DIR%\' -Force } catch { Write-Host \"解压失败: $_\"; exit 1 }"\n'
            "if %errorlevel% neq 0 (\n"
            '  echo 解压失败，请手动用 %ZIP% 覆盖 %INSTALL_DIR%\n'
            "  pause\n"
            "  exit /b 1\n"
            ")\n"
            ":: 校验新程序是否生成且大小合理\n"
            'if not exist "%INSTALL_DIR%\\GitPush.exe" (\n'
            '  echo 更新失败：GitPush.exe 未生成\n'
            '  pause\n'
            '  exit /b 1\n'
            ')\n'
            'for %%F in ("%INSTALL_DIR%\\GitPush.exe") do if %%~zF LSS 1000000 (\n'
            '  echo 更新失败：GitPush.exe 大小异常（%%~zF 字节）\n'
            '  pause\n'
            '  exit /b 1\n'
            ')\n'
            'del "%INSTALL_DIR%\\GitPush.exe.old" >nul 2>&1\n'
            "echo 更新完成，正在启动新版本…\n"
            'start "" "%INSTALL_DIR%\\GitPush.exe"\n'
            'del "%ZIP%" >nul 2>&1\n'
            'del "%~f0" >nul 2>&1\n'
        )
        try:
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat)
        except Exception as e:
            self._log(f"❌ 生成替换脚本失败：{e}")
            self._set_status("生成替换脚本失败")
            return

        self._log(f"已生成替换脚本：{bat_path}")
        self._log("正在启动替换脚本并退出旧程序…")
        # 记录一次「更新成功」事件（仅匿名统计，需用户已同意）
        try:
            self.parent._report_event("update", join=True)
        except Exception:
            pass
        try:
            subprocess.Popen([bat_path], shell=False,
                             creationflags=subprocess.CREATE_NO_WINDOW)
            self.parent.after(500, self._exit_app)
        except Exception as e:
            self._log(f"❌ 启动替换脚本失败：{e}")
            self._set_status("启动替换脚本失败")
            self._set_btn("立即更新", True)

    def _exit_app(self):
        try:
            self.window.destroy()
        except Exception:
            pass
        try:
            self.parent.destroy()
        except Exception:
            pass
        sys.exit(0)


def resource_path(rel):
    """获取资源文件的真实路径：打包后从 _MEIPASS 取，开发模式下从脚本目录取"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def main():
    try:
        root = tk.Tk()
        # 应用专属图标（Git 橙 + 推送箭头）
        try:
            _icon = resource_path("appicon.ico")
            if os.path.exists(_icon):
                root.iconbitmap(_icon)
        except Exception:
            pass
        try:
            # 用安全字体名设置全局默认字体（避免中文字体名被 Tcl 误解析）
            default_font = tkfont.nametofont("TkDefaultFont")
            default_font.configure(family="Segoe UI", size=10)
        except Exception:
            pass
        tool = GitPushTool(root)
        import atexit
        atexit.register(lambda: tool._report_event("session_end", join=True))
        root.mainloop()
    except Exception:
        # 兜底：任何启动期异常都弹窗显示，避免一闪而过看不到原因
        import traceback
        err = traceback.format_exc()
        try:
            r = tk.Tk()
            r.withdraw()
            messagebox.showerror("启动失败", err)
        except Exception:
            print(err)
        try:
            input("按回车键退出...")
        except Exception:
            pass


if __name__ == "__main__":
    main()
