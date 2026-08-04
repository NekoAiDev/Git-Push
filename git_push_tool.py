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

import os
import re
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, font as tkfont

APP_TITLE = "Git Push 工具推送"
APP_VERSION = "1.0"


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
            self.set_status("就绪，请选择文件夹并填写仓库地址喵~")

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

            # 7) git push
            cmd = ["git", "push"]
            if force:
                cmd.append("--force")
            cmd += ["-u", remote, branch]
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


def main():
    try:
        root = tk.Tk()
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
