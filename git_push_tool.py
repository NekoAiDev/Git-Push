#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Push 小工具 
================================
一个带图形界面的小工具：打开后，选择本地文件夹（或单个文件），
填写远程仓库地址，点一下按钮，就能自动完成：
    git init（如果还不是仓库）
    git add
    git commit
    git remote add / set-url
    git push -u <remote> <branch>
并在界面上实时显示每一步的日志

运行方式（主人本机）：
    python git_push_tool.py
需要本机已安装 git 且能在命令行直接调用。
"""

import json
import os
import time
import re
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
import urllib.request
from tkinter import ttk, filedialog, scrolledtext, messagebox, font as tkfont

APP_TITLE = "Git Push 工具推送"
APP_VERSION = "1.2.4"

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
        self.root.geometry("760x680")
        self.root.minsize(640, 560)
        try:
            # 尝试给窗口加个小图标感（无图标文件时忽略）
            pass
        except Exception:
            pass

        self.running = False

        self._build_styles()
        self._build_ui()
        self._build_menu()

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

        # 日志区
        log_frm = ttk.LabelFrame(self.root, text="运行日志", padding=(8, 6))
        log_frm.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        log_frm.rowconfigure(0, weight=1)
        log_frm.columnconfigure(0, weight=1)

        self.log_box = scrolledtext.ScrolledText(log_frm, wrap="word",
                                                  font=("Consolas", 10))
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
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        update_menu = tk.Menu(menubar, tearoff=0)
        update_menu.add_command(label="检查更新", command=self._open_updater)
        menubar.add_cascade(label="更新(U)", menu=update_menu)

        self.root.config(menu=menubar)

    # ---------------------------------------------------------------- 选择
    def _pick_folder(self):
        p = filedialog.askdirectory(title="选择要推送的文件夹")
        if p:
            self.path_var.set(p)

    def _pick_file(self):
        p = filedialog.askopenfilename(title="选择要推送的单个文件")
        if p:
            self.path_var.set(p)

    # ---------------------------------------------------------------- 日志
    def log(self, text):
        self.root.after(0, self._append_log, str(text))

    def _append_log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.configure(state="disabled")
        self.log_box.see(tk.END)

    def set_status(self, text):
        self.root.after(0, self.status_var.set, text)

    # ---------------------------------------------------------------- 运行
    def start_push(self):
        if self.running:
            return
        path = self.path_var.get().strip()
        repo = self.repo_var.get().strip()
        branch = self.branch_var.get().strip() or "main"
        commit = self.commit_var.get().strip() or "Auto push by Git Push工具"
        remote = self.remote_var.get().strip() or "origin"
        force = self.force_var.get()

        if not path:
            messagebox.showerror("出错啦", "请先选择要 Push 的文件夹或文件")
            return
        if not repo:
            messagebox.showerror("出错啦", "请填写要 Push 的远程仓库地址")
            return
        if not os.path.exists(path):
            messagebox.showerror("出错啦", "主人填的路径不存在喵~请检查一下")
            return

        self.running = True
        self.root.after(0, lambda: self.push_btn.config(state="disabled"))
        self.set_status("正在推送中…")
        t = threading.Thread(target=self.do_push,
                             args=(path, repo, branch, commit, remote, force),
                             daemon=True)
        t.start()

    def run(self, cmd, cwd):
        """执行一条 git 命令，把输出实时写进日志，返回 returncode。"""
        self.log("💻 " + " ".join(cmd))
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
            r = subprocess.run(["git"] + args, cwd=cwd,
                               capture_output=True, text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW)
            return r.stdout or ""
        except Exception:
            return ""

    def do_push(self, path, repo, branch, commit, remote, force):
        try:
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
            inside = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=repo_dir, capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if inside.returncode != 0:
                self.log("🔧 还不是 Git 仓库，正在 git init ")
                self.run(["git", "init"], repo_dir)
                self.run(["git", "checkout", "-B", branch], repo_dir)
            else:
                self.log("✅ 已经是 Git 仓库啦~")

            # 2) 检查 user 配置（向上查找全局，缺了 commit 会失败）
            name = self._git_out(["config", "user.name"], repo_dir).strip()
            email = self._git_out(["config", "user.email"], repo_dir).strip()
            if not name or not email:
                self.log("⚠️ 此仓库（及全局）未配置 user.name / user.email，commit 可能失败")
                self.log("   可在命令行先执行：")
                self.log("   git config --global user.name \"你的名字\"")
                self.log("   git config --global user.email \"你的邮箱\"")

            # 3) 认证提示
            if repo.startswith("https://") and "@" not in repo:
                self.log("🔐 提示：HTTPS 地址未带凭证。若本机未缓存 Git 凭证可能会弹窗或失败")
                self.log("   方案 A：用已缓存凭证的系统的凭据管理器；")
                self.log("   方案 B：地址写成 https://<TOKEN>@github.com/用户/仓库.git")

            # 4) git add
            self.log(f"➕ 添加内容：{add_target}")
            self.run(["git", "add", add_target], repo_dir)

            # 5) git commit（仅当有改动）
            status = self._git_out(["status", "--porcelain"], repo_dir).strip()
            if status:
                self.run(["git", "commit", "-m", commit], repo_dir)
            else:
                self.log("💡 没有新的改动，跳过 commit ")

            # 6) git remote
            remotes = self._git_out(["remote"], repo_dir).split()
            if remote in remotes:
                self.run(["git", "remote", "set-url", remote, repo], repo_dir)
            else:
                self.run(["git", "remote", "add", remote, repo], repo_dir)

            # 6.5) 确定要推送的本地 ref —— 修复 issue #2「src refspec main does not match any」
            # 当本地不存在用户填写的分支名时（例如本地当前分支是 master，但默认填了 main），
            # 直接 push <branch> 会失败。这里先探测本地分支，再用正确的 refspec 推送。
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

            # 7) git push
            cmd = ["git", "push"]
            if force:
                cmd.append("--force")
            cmd += ["-u", remote, push_ref]
            rc = self.run(cmd, repo_dir)

            if rc == 0:
                self.log("🎉 推送成功！")
                self.set_status("✅ 推送成功")
            else:
                self.log("⚠️ 推送失败，请查看上方日志找原因（多半是凭证或分支冲突）")
                self.set_status("❌ 推送失败")
        except Exception as e:
            self.log(f"❌ 发生异常：{e}")
            self.set_status("❌ 出错")
        finally:
            self.running = False
            self.root.after(0, lambda: self.push_btn.config(state="normal"))

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
            "5. 日志区会实时显示每一步输出，失败时可据此排查喵~\n\n"
            "注意：本机需已安装 git 并能在命令行直接调用。"
        )
        messagebox.showinfo("使用说明", msg)

    def _show_about(self):
        messagebox.showinfo("关于",
                            f"{APP_TITLE}\n版本 {APP_VERSION}\n\n"
                            "由小红蛋精心编写的Git 推送工具")

    # ---------------------------------------------------------------- 更新
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
        self.log_frm = ttk.LabelFrame(self.window, text="运行日志（调试用）", padding=(8, 6))
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

        notes = data.get("notes") or data.get("body") or "作者没有写更新说明喵~"
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
    """获取资源文件的真实路径：打包后从 _MEIPASS 取，开发模式下从脚本目录取 喵~"""
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
        GitPushTool(root)
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
