import sys
import math
import psutil
import cv2
import pyttsx3
import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QRadialGradient, QFont, QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

# ---------------- VOICE ENGINE ---------------- #
engine = pyttsx3.init()
engine.setProperty("rate", 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()


# ---------------- FRIDAY UI ---------------- #
class FridayUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("FRIDAY AI SYSTEM")
        self.setGeometry(100, 50, 1400, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Animation
        self.outer_angle = 0
        self.inner_angle = 0
        self.pulse = 0
        self.pulse_dir = 1

        # System stats
        self.cpu = 0
        self.ram = 0
        self.disk = 0
        self.security = "SECURE"

        # Camera
        self.cap = cv2.VideoCapture(0)
        self.camera_label = QLabel(self)
        self.camera_label.setGeometry(1000, 150, 350, 250)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system)
        self.timer.start(50)

        speak("Friday system online.")

    # ---------------- UPDATE SYSTEM ---------------- #
    def update_system(self):

        # Animation rotation
        self.outer_angle += 1
        self.inner_angle -= 2

        # Pulse animation
        self.pulse += self.pulse_dir * 2
        if self.pulse > 30 or self.pulse < 0:
            self.pulse_dir *= -1

        # System monitoring
        self.cpu = psutil.cpu_percent()
        self.ram = psutil.virtual_memory().percent
        self.disk = psutil.disk_usage('/').percent

        # Security logic
        if self.cpu > 80:
            self.security = "CRITICAL"
        elif self.cpu > 50:
            self.security = "WARNING"
        else:
            self.security = "SECURE"

        self.update_camera()
        self.update()

    # ---------------- CAMERA ---------------- #
    def update_camera(self):

        ret, frame = self.cap.read()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            image = QImage(
                frame.data,
                frame.shape[1],
                frame.shape[0],
                frame.strides[0],
                QImage.Format.Format_RGB888
            )

            pix = QPixmap.fromImage(image)
            self.camera_label.setPixmap(pix)

    # ---------------- DRAW UI ---------------- #
    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        center = QPointF(self.width()/2, self.height()/2)

        # ---------- OUTER ROTATING RING ----------
        painter.save()
        painter.translate(center)
        painter.rotate(self.outer_angle)

        painter.setPen(QPen(QColor(255,255,255), 3))
        painter.drawEllipse(QPointF(0,0), 280, 280)

        painter.restore()

        # ---------- INNER ROTATING ARCS ----------
        painter.save()
        painter.translate(center)
        painter.rotate(self.inner_angle)

        painter.setPen(QPen(QColor(0,150,255), 10))

        rect = QRectF(-200, -200, 400, 400)

        painter.drawArc(rect, 0, 60*16)
        painter.drawArc(rect, 120*16, 60*16)
        painter.drawArc(rect, 240*16, 60*16)

        painter.restore()

        # ---------- CENTER ENERGY CORE ----------
        glow = 120 + self.pulse

        gradient = QRadialGradient(center, glow)
        gradient.setColorAt(0, QColor(0,150,255,220))
        gradient.setColorAt(0.5, QColor(255,255,255,120))
        gradient.setColorAt(1, QColor(0,0,0,0))

        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, glow, glow)

        painter.setBrush(QColor(255,255,255))
        painter.drawEllipse(center, 20, 20)

        # ---------- TEXT PANEL ----------
        painter.setPen(QPen(QColor(255,255,255)))

        painter.setFont(QFont("Orbitron", 32))
        painter.drawText(60,80,"FRIDAY")

        painter.setFont(QFont("Orbitron", 16))
        painter.drawText(100,250,f"CPU USAGE : {self.cpu}%")
        painter.drawText(100,300,f"RAM USAGE : {self.ram}%")
        painter.drawText(100,350,f"DISK USAGE : {self.disk}%")
        painter.drawText(100,400,f"SECURITY LEVEL : {self.security}")

    # ---------------- CLOSE CAMERA ---------------- #
    def closeEvent(self, event):

        self.cap.release()
        event.accept()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Escape:
            self.close()


# ---------------- RUN APP ---------------- #

app = QApplication(sys.argv)

window = FridayUI()
window.show()

sys.exit(app.exec())