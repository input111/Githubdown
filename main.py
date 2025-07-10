import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import sys
import threading

class GitHubUploader:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub代码上传工具")
        self.root.geometry("600x600")  # 增加窗口高度
        self.root.resizable(True, True)
        
        # 设置中文字体支持
        self.style = ttk.Style()
        if sys.platform.startswith('win'):
            self.default_font = ('Microsoft YaHei UI', 10)
        elif sys.platform.startswith('darwin'):
            self.default_font = ('Heiti TC', 10)
        else:
            self.default_font = ('SimHei', 10)
            
        self.style.configure('TLabel', font=self.default_font)
        self.style.configure('TButton', font=self.default_font)
        self.style.configure('TEntry', font=self.default_font)
        self.style.configure('TText', font=self.default_font)
        self.style.configure('TCombobox', font=self.default_font)
        
        # 变量
        self.repo_path = tk.StringVar()
        self.github_username = tk.StringVar()
        self.repo_name = tk.StringVar()
        self.commit_message = tk.StringVar(value="Initial commit")
        self.github_token = tk.StringVar()
        self.upload_status = tk.StringVar(value="就绪")
        self.branch_name = tk.StringVar(value="main")
        self.git_status = tk.StringVar(value="未检查")
        self.git_path = tk.StringVar()  # 新增：Git路径变量
        
        # 创建界面
        self._create_widgets()
        
    def _create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 项目路径选择
        ttk.Label(main_frame, text="项目路径:").grid(row=0, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        ttk.Entry(path_frame, textvariable=self.repo_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(path_frame, text="浏览...", command=self._browse_repo).pack(side=tk.LEFT, padx=5)
        
        # GitHub信息
        ttk.Label(main_frame, text="GitHub用户名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.github_username, width=40).grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="仓库名称:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.repo_name, width=40).grid(row=2, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="分支名称:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.branch_name, width=40).grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="提交信息:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        ttk.Entry(main_frame, textvariable=self.commit_message, width=40).grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(main_frame, text="GitHub Token:").grid(row=5, column=0, sticky=tk.W, pady=5)
        token_frame = ttk.Frame(main_frame)
        token_frame.grid(row=5, column=1, sticky=tk.EW, pady=5)
        
        self.token_entry = ttk.Entry(token_frame, textvariable=self.github_token, width=40, show='*')
        self.token_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.show_token_var = tk.BooleanVar()
        ttk.Checkbutton(token_frame, text="显示Token", variable=self.show_token_var,
                      command=self._toggle_token_visibility).pack(side=tk.LEFT, padx=5)
        
        # Git路径配置
        ttk.Label(main_frame, text="Git路径:").grid(row=6, column=0, sticky=tk.NW, pady=5)
        git_frame = ttk.Frame(main_frame)
        git_frame.grid(row=6, column=1, sticky=tk.EW, pady=5)
        
        ttk.Entry(git_frame, textvariable=self.git_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(git_frame, text="浏览...", command=self._browse_git).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="如果无法检测到Git环境变量\n或不想配置环境变量，请将Git的bin目录添加到这里",
                 font=(self.default_font[0], 9), foreground='gray').grid(row=7, column=1, sticky=tk.W, pady=2)
        
        # Git环境检查
        ttk.Label(main_frame, text="Git环境状态:").grid(row=8, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, textvariable=self.git_status, foreground="blue").grid(row=8, column=1, sticky=tk.W, pady=5)
        
        check_frame = ttk.Frame(main_frame)
        check_frame.grid(row=9, column=0, columnspan=2, pady=5)
        
        ttk.Button(check_frame, text="检查本地Git环境", command=self._check_git_environment).pack(side=tk.LEFT, padx=10)
        
        # 状态和输出
        ttk.Label(main_frame, text="上传状态:").grid(row=10, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, textvariable=self.upload_status).grid(row=10, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="输出:").grid(row=11, column=0, sticky=tk.NW, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=11, column=1, sticky=tk.NSEW, pady=5)
        
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, width=50, height=10)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=12, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="上传到GitHub", command=self._upload_to_github).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="清除输出", command=self._clear_output).pack(side=tk.LEFT, padx=10)
        
        # 设置行和列的权重，使界面可缩放
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(11, weight=1)
        
    def _browse_repo(self):
        """浏览并选择项目路径"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.repo_path.set(folder_selected)
            # 尝试自动获取仓库名称
            if not self.repo_name.get():
                self.repo_name.set(os.path.basename(folder_selected))
    
    def _browse_git(self):
        """浏览并选择Git路径"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.git_path.set(folder_selected)
    
    def _toggle_token_visibility(self):
        """切换Token显示/隐藏状态"""
        if self.show_token_var.get():
            self.token_entry.config(show='')
        else:
            self.token_entry.config(show='*')
    
    def _clear_output(self):
        """清除输出文本框内容"""
        self.output_text.delete(1.0, tk.END)
    
    def _log_output(self, message):
        """在输出文本框中添加日志"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def _get_git_command(self, command):
        """获取完整的Git命令（带路径或不带）"""
        git_path = self.git_path.get().strip()
        if git_path:
            # 检查路径是否包含git.exe (Windows)或git (Linux/macOS)
            if sys.platform.startswith('win'):
                git_exe = os.path.join(git_path, "git.exe")
            else:
                git_exe = os.path.join(git_path, "git")
            
            # 如果指定的路径不存在，使用原始命令让系统自己找
            if os.path.exists(git_exe):
                return f'"{git_exe}" {command}'
        
        # 如果未指定Git路径或路径无效，直接使用系统命令
        return f'git {command}'
    
    def _check_git_environment(self):
        """检查本地Git环境"""
        self._clear_output()
        self.git_status.set("检查中...")
        
        threading.Thread(target=self._execute_git_checks, daemon=True).start()
    
    def _execute_git_checks(self):
        """执行Git环境检查"""
        try:
            self._log_output("开始检查本地Git环境...")
            
            # 检查Git是否安装
            git_installed = self._check_git_installed()
            if not git_installed:
                self.git_status.set("未找到Git，请安装Git并配置环境变量或手动指定Git路径")
                return
            
            # 检查项目路径
            if not self.repo_path.get() or not os.path.isdir(self.repo_path.get()):
                self.git_status.set("请选择有效的项目路径")
                self._log_output("错误: 项目路径不存在或无效")
                return
            
            # 获取并保存当前目录，避免在异常情况下使用未定义变量
            original_dir = os.getcwd()
            
            # 切换到项目目录
            os.chdir(self.repo_path.get())
            self._log_output(f"已切换到目录: {self.repo_path.get()}")
            
            # 检查是否是Git仓库
            is_git_repo = self._check_is_git_repo()
            if not is_git_repo:
                self.git_status.set("不是Git仓库")
                self._log_output("提示: 此目录不是Git仓库，上传时将自动初始化")
            else:
                self._log_output("✔ 此目录是Git仓库")
                
                # 检查是否已关联远程仓库
                has_remote = self._check_remote_repo()
                if has_remote:
                    self._log_output("✔ 已关联远程仓库")
                    remote_url = self._get_remote_url()
                    self._log_output(f"远程仓库URL: {remote_url}")
                else:
                    self._log_output("提示: 未关联远程仓库，上传时将设置远程仓库")
            
            self.git_status.set("Git环境检查通过")
            messagebox.showinfo("成功", "本地Git环境检查通过!")
            
        except Exception as e:
            self._log_output(f"错误: {str(e)}")
            self.git_status.set(f"检查失败: {str(e)}")
        finally:
            # 确保在所有情况下都尝试切换回原目录
            if 'original_dir' in locals():
                os.chdir(original_dir)
    
    def _check_git_installed(self):
        """检查Git是否安装"""
        try:
            result = subprocess.run(
                self._get_git_command("--version"),
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                git_version = result.stdout.strip()
                self._log_output(f"✔ {git_version}")
                return True
            else:
                self._log_output(f"错误: {result.stderr}")
                return False
        except Exception as e:
            self._log_output(f"检测Git时出错: {str(e)}")
            return False
    
    def _check_is_git_repo(self):
        """检查当前目录是否是Git仓库"""
        try:
            result = subprocess.run(
                self._get_git_command("rev-parse --is-inside-work-tree"),
                shell=True,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_remote_repo(self):
        """检查是否已关联远程仓库"""
        try:
            result = subprocess.run(
                self._get_git_command("remote -v"),
                shell=True,
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and "origin" in result.stdout
        except Exception:
            return False
    
    def _get_remote_url(self):
        """获取远程仓库URL"""
        try:
            result = subprocess.run(
                self._get_git_command("config --get remote.origin.url"),
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "未知"
        except Exception:
            return "未知"
    
    def _upload_to_github(self):
        """上传代码到GitHub的主函数"""
        # 检查Git环境
        if self.git_status.get() != "Git环境检查通过":
            if messagebox.askyesno("确认", "未进行Git环境检查或检查未通过，是否继续上传?"):
                pass
            else:
                return
        
        # 检查必要信息
        if not self.repo_path.get() or not os.path.isdir(self.repo_path.get()):
            messagebox.showerror("错误", "请选择有效的项目路径")
            return
        
        if not self.github_username.get():
            messagebox.showerror("错误", "请输入GitHub用户名")
            return
        
        if not self.repo_name.get():
            messagebox.showerror("错误", "请输入仓库名称")
            return
        
        if not self.github_token.get():
            messagebox.showerror("错误", "请输入GitHub Token")
            return
        
        # 在新线程中执行Git操作，避免UI卡顿
        self.upload_status.set("上传中...")
        threading.Thread(target=self._execute_git_commands, daemon=True).start()
    
    def _execute_git_commands(self):
        """执行Git命令上传代码到GitHub"""
        try:
            self._log_output("开始上传代码到GitHub...")
            
            # 切换到项目目录
            original_dir = os.getcwd()
            os.chdir(self.repo_path.get())
            self._log_output(f"已切换到目录: {self.repo_path.get()}")
            
            # 初始化Git仓库(如果不是)
            if not self._check_is_git_repo():
                self._run_command("init")
            
            # 添加所有文件
            self._run_command("add .")
            
            # 提交文件（如果有修改）
            commit_msg = self.commit_message.get() or "Initial commit"
            try:
                self._run_command(f'commit -m "{commit_msg}"')
            except:
                self._log_output("没有新的修改需要提交，跳过commit步骤")
            
            # 设置远程仓库
            remote_url = f"https://{self.github_username.get()}:{self.github_token.get()}@github.com/{self.github_username.get()}/{self.repo_name.get()}.git"
            
            # 检查是否已设置远程仓库
            if self._check_remote_repo():
                current_remote = self._get_remote_url()
                if current_remote != remote_url:
                    self._log_output(f"更新远程仓库URL: {current_remote} → {remote_url}")
                    self._run_command(f"remote set-url origin {remote_url}")
                else:
                    self._log_output(f"使用现有远程仓库: {current_remote}")
            else:
                self._run_command(f"remote add origin {remote_url}")
            
            # 推送代码（核心优化部分）
            branch = self.branch_name.get() or "main"
            self._log_output(f"准备推送分支: {branch}")
            
            # 检查本地是否存在该分支，若不存在则创建
            try:
                # 验证本地是否有该分支
                self._run_command(f"rev-parse --verify {branch}")
                self._log_output(f"本地存在 {branch} 分支，直接推送")
            except:
                # 本地无该分支，基于当前提交创建并切换
                self._log_output(f"本地不存在 {branch} 分支，创建新分支...")
                self._run_command(f"checkout -b {branch}")
            
            # 执行推送
            self._run_command(f"push -u origin {branch}")
            
            self._log_output("代码已成功上传到GitHub!")
            self.upload_status.set("上传成功")
            messagebox.showinfo("成功", "代码已成功上传到GitHub!")
            
        except Exception as e:
            self._log_output(f"错误: {str(e)}")
            self.upload_status.set("上传失败")
            messagebox.showerror("错误", f"上传失败: {str(e)}")
        finally:
            if 'original_dir' in locals():
                os.chdir(original_dir)
    
    def _run_command(self, command):
        """执行系统命令并记录输出"""
        full_command = self._get_git_command(command)
        self._log_output(f"执行: {full_command}")
        result = subprocess.run(full_command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            self._log_output(f"标准输出:\n{result.stdout}")
        
        if result.stderr:
            self._log_output(f"错误输出:\n{result.stderr}")
        
        result.check_returncode()  # 检查命令执行状态

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUploader(root)
    root.mainloop()    