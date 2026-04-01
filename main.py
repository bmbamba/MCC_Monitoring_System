import sys
import csv
import random
import sqlite3
import os
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QTextEdit, QGroupBox, 
    QFrame, QMessageBox, QFileDialog, QScrollArea, QSpinBox, 
    QDoubleSpinBox, QTabWidget, QDialog, QDialogButtonBox,
    QFormLayout, QLineEdit, QCheckBox, QProgressBar, QSplitter,
    QToolBar, QMenu, QSystemTrayIcon, QStyle, QSplashScreen,
    QGraphicsDropShadowEffect, QGraphicsBlurEffect
)
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, QSize, QRectF, QPointF
from PySide6.QtGui import (
    QFont, QPalette, QColor, QIcon, QAction, QPixmap, QPainter,
    QLinearGradient, QBrush, QPen, QPainterPath
)

# ==================== CUSTOM MOTOR ICON CREATOR ====================
class MotorIconCreator:
    @staticmethod
    def create_motor_icon(size=64, color="#3b82f6"):
        """Create a realistic motor icon"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Main motor body (rounded rectangle)
        body_rect = QRectF(8, 12, size-16, size-24)
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(color).darker(120), 2))
        painter.drawRoundedRect(body_rect, 8, 8)
        
        # Motor shaft (center circle)
        shaft_center = QPointF(size/2, size/2)
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(QPen(QColor("#94a3b8"), 1.5))
        painter.drawEllipse(shaft_center, size*0.12, size*0.12)
        
        # Inner circle (motor rotor)
        painter.setBrush(QBrush(QColor(color).lighter(130)))
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawEllipse(shaft_center, size*0.2, size*0.2)
        
        # Motor winding lines (diagonal stripes)
        painter.setPen(QPen(QColor("#ffffff"), 1.5))
        for i in range(-3, 4):
            x = size/2 + i * 4
            painter.drawLine(x, size/2 - 8, x, size/2 + 8)
        
        # Add bolt heads on corners
        painter.setBrush(QBrush(QColor("#64748b")))
        painter.setPen(QPen(QColor("#475569"), 1))
        bolt_positions = [
            (12, 16), (size-12, 16),
            (12, size-16), (size-12, size-16)
        ]
        for x, y in bolt_positions:
            painter.drawEllipse(x-2, y-2, 4, 4)
        
        # Add ventilation slots (horizontal lines on sides)
        painter.setPen(QPen(QColor("#ffffff"), 1.2))
        for i in range(3):
            y = size/2 - 6 + i * 6
            painter.drawLine(6, y, 12, y)
            painter.drawLine(size-12, y, size-6, y)
        
        # Add "M" for Motor
        painter.setFont(QFont("Segoe UI", int(size*0.2), QFont.Weight.Bold))
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawText(QRectF(0, size-18, size, 12), Qt.AlignCenter, "MOTOR")
        
        painter.end()
        return QIcon(pixmap)
    
    @staticmethod
    def create_small_motor_icon(size=32, color="#60a5fa"):
        """Create a smaller motor icon for cards"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        body_rect = QRectF(4, 6, size-8, size-12)
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(color).darker(120), 1.5))
        painter.drawRoundedRect(body_rect, 4, 4)
        
        center = QPointF(size/2, size/2)
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.drawEllipse(center, size*0.1, size*0.1)
        
        painter.setBrush(QBrush(QColor(color).lighter(130)))
        painter.drawEllipse(center, size*0.16, size*0.16)
        
        painter.setPen(QPen(QColor("#ffffff"), 1))
        for i in range(-2, 3):
            x = size/2 + i * 3
            painter.drawLine(x, size/2 - 5, x, size/2 + 5)
        
        painter.end()
        return QIcon(pixmap)

# ==================== GLASS PANEL EFFECT ====================
class GlassPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 46, 0.7);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, QColor(255, 255, 255, 30))
        gradient.setColorAt(1, QColor(255, 255, 255, 10))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(255, 255, 255, 40), 1))
        painter.drawRoundedRect(rect, 16, 16)
        super().paintEvent(event)

# ==================== GRADIENT PROGRESS BAR ====================
class GradientProgressBar(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setFixedHeight(12)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        bg_rect = self.rect()
        painter.setBrush(QBrush(QColor(30, 30, 40)))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(bg_rect, 6, 6)
        
        value = self.value()
        if value > 0:
            progress_width = int(self.width() * value / 100)
            progress_rect = QRectF(0, 0, progress_width, self.height())
            
            if value >= 75:
                gradient = QLinearGradient(0, 0, progress_width, 0)
                gradient.setColorAt(0, QColor(34, 197, 94))
                gradient.setColorAt(1, QColor(74, 222, 128))
            elif value >= 50:
                gradient = QLinearGradient(0, 0, progress_width, 0)
                gradient.setColorAt(0, QColor(245, 158, 11))
                gradient.setColorAt(1, QColor(251, 191, 36))
            else:
                gradient = QLinearGradient(0, 0, progress_width, 0)
                gradient.setColorAt(0, QColor(239, 68, 68))
                gradient.setColorAt(1, QColor(248, 113, 113))
            
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(progress_rect, 6, 6)
        
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        text = f"{value}%"
        painter.drawText(self.rect(), Qt.AlignCenter, text)

# ==================== TOAST NOTIFICATION ====================
class ToastNotification(QFrame):
    def __init__(self, message, parent=None, duration=3000):
        super().__init__(parent)
        self.setup_ui(message)
        self.duration = duration
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_toast)
        
        self.show_toast()
        
    def setup_ui(self, message):
        self.setStyleSheet("""
            QFrame {
                background-color: #1f2937;
                border-radius: 8px;
                border: 1px solid #374151;
            }
            QLabel {
                color: #e4e4e7;
                padding: 12px 20px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        
        icon = QLabel("🔔")
        layout.addWidget(icon)
        
        text = QLabel(message)
        layout.addWidget(text)
        
        self.setLayout(layout)
        self.adjustSize()
        
    def show_toast(self):
        parent = self.parent()
        if parent:
            x = parent.width() - self.width() - 20
            y = parent.height() - self.height() - 80
            self.move(x, y)
        
        self.show()
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        self.timer.start(self.duration)
        
    def hide_toast(self):
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.close)
        self.animation.start()

# ==================== METRIC CARD ====================
class MetricCard(QFrame):
    def __init__(self, title, value, unit, icon, color="#3b82f6"):
        super().__init__()
        self.title = title
        self.value = value
        self.unit = unit
        self.icon = icon
        self.color = color
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(200, 120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1a26;
                border-radius: 12px;
                border: 1px solid #2a2a38;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Header with icon
        header = QHBoxLayout()
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"color: {self.color}; font-size: 24px;")
        header.addWidget(icon_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Value
        self.value_label = QLabel(str(self.value))
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {self.color};")
        layout.addWidget(self.value_label)
        
        # Title and unit
        bottom = QHBoxLayout()
        bottom.addWidget(QLabel(self.title))
        bottom.addStretch()
        bottom.addWidget(QLabel(self.unit))
        layout.addLayout(bottom)
        
        self.setLayout(layout)
    
    def update_value(self, value):
        self.value = value
        self.value_label.setText(str(value))

# ==================== THEME TOGGLE ====================
class ThemeToggle(QPushButton):
    def __init__(self, parent=None):
        super().__init__("🌙", parent)
        self.setFixedSize(40, 40)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1f2937;
                border-radius: 20px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        """)
        self.clicked.connect(self.toggle_theme)
        self.is_dark = True
        
    def toggle_theme(self):
        app = QApplication.instance()
        if self.is_dark:
            app.setStyleSheet("""
                QMainWindow { background-color: #f9fafb; }
                QLabel { color: #1f2937; }
                QGroupBox { color: #374151; border-color: #e5e7eb; background-color: #ffffff; }
                QPushButton { background-color: #e5e7eb; color: #1f2937; border: 1px solid #d1d5db; }
                QFrame { background-color: #ffffff; }
                QTextEdit { background-color: #f3f4f6; color: #1f2937; }
                QProgressBar { background-color: #e5e7eb; }
            """)
            self.setText("☀️")
            self.is_dark = False
        else:
            app.setStyleSheet("""
                QMainWindow { background-color: #0f0f17; }
                QLabel { color: #e4e4e7; }
                QGroupBox { color: #9ca3af; border-color: #2a2a38; background-color: #1a1a26; }
                QPushButton { background-color: #1f2937; color: #e4e4e7; border: 1px solid #374151; }
                QFrame { background-color: #1a1a26; }
                QTextEdit { background-color: #111118; color: #e4e4e7; }
                QProgressBar { background-color: #2d2d3a; }
            """)
            self.setText("🌙")
            self.is_dark = True

# ==================== DATA SIMULATOR CLASSES ====================
class MotorData:
    def __init__(self, name, motor_type):
        self.name = name
        self.type = motor_type
        self.status = "RUNNING"
        self.current = 0.0
        self.temperature = 0.0
        self.vibration = 0.0
        self.runtime = 0.0
        self.fault_code = 0
        self.efficiency = 92.5
        self.power_consumption = 0.0
        self.ranges = {"current": (40, 80), "temperature": (50, 75), "vibration": (2.0, 4.5)}
        self.thresholds = {
            "current_high": 90,
            "temp_high": 90,
            "vibration_high": 7.0
        }
        self.HISTORY_SIZE = 30
        self.current_history = []
        self.temp_history = []
        self.vibe_history = []
        self.health_score = 100.0
        self.current_trend = "stable"
        self.temp_trend = "stable"
        self.vibe_trend = "stable"
        self.dominant_freq_hz = 0.0
        self.fft_alarm = False

    def update_history(self):
        for buf, val in [(self.current_history, self.current),
                         (self.temp_history, self.temperature),
                         (self.vibe_history, self.vibration)]:
            buf.append(val)
            if len(buf) > self.HISTORY_SIZE:
                buf.pop(0)

    def compute_trend(self, buf, threshold=0.05):
        import numpy as np
        if len(buf) < 6:
            return "stable"
        x = np.arange(len(buf), dtype=float)
        slope = np.polyfit(x, buf, 1)[0]
        mean = np.mean(buf) if np.mean(buf) != 0 else 1.0
        if abs(slope) / abs(mean) < threshold:
            return "stable"
        return "rising" if slope > 0 else "falling"

    def compute_health(self):
        if self.status == "FAULT":
            self.health_score = 0.0
            return
        if self.status == "STOPPED":
            self.health_score = 50.0
            return

        def param_score(val, lo, hi, weight=33.0):
            if val <= lo:
                return weight
            if val >= hi:
                return 0.0
            return weight * (1.0 - (val - lo) / (hi - lo))

        score = (param_score(self.current, 50, self.thresholds["current_high"]) +
                 param_score(self.temperature, 60, self.thresholds["temp_high"]) +
                 param_score(self.vibration, 3.0, self.thresholds["vibration_high"], 34.0))
        if self.current_trend == "rising":
            score -= 5
        if self.vibe_trend == "rising":
            score -= 8
        if self.fft_alarm:
            score -= 10
        self.health_score = round(max(0.0, min(100.0, score)), 1)

    def run_fft(self, sample_rate_hz=0.5):
        import numpy as np
        if len(self.vibe_history) < 16:
            return
        signal = np.array(self.vibe_history) - np.mean(self.vibe_history)
        fft_vals = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(len(signal), d=1.0 / sample_rate_hz)
        peak_idx = np.argmax(fft_vals[1:]) + 1
        self.dominant_freq_hz = round(float(freqs[peak_idx]), 4)
        mean_amp = np.mean(fft_vals[1:])
        self.fft_alarm = bool(fft_vals[peak_idx] > 3.0 * mean_amp)

class MotorSimulator:
    def __init__(self):
        self.motors = [
            MotorData("Conveyor Belt CV-01", "Conveyor"),
            MotorData("Slurry Pump PM-01", "Pump"),
            MotorData("Jaw Crusher CR-01", "Crusher"),
            MotorData("Ventilation Fan VF-01", "Fan"),
            MotorData("Thickener Drive TH-01", "Drive"),
            MotorData("Air Compressor AC-01", "Compressor")
        ]
        
        self.motors[0].ranges = {"current": (45, 70), "temperature": (55, 75), "vibration": (2.5, 4.5)}
        self.motors[1].ranges = {"current": (35, 60), "temperature": (50, 70), "vibration": (2.0, 4.0)}
        self.motors[2].ranges = {"current": (75, 110), "temperature": (60, 85), "vibration": (3.0, 5.5)}
        self.motors[3].ranges = {"current": (25, 45), "temperature": (45, 65), "vibration": (1.5, 3.5)}
        self.motors[4].ranges = {"current": (30, 55), "temperature": (50, 70), "vibration": (2.0, 4.0)}
        self.motors[5].ranges = {"current": (55, 80), "temperature": (55, 75), "vibration": (2.5, 4.5)}
        
        self.initialize_motors()
    
    def initialize_motors(self):
        for motor in self.motors:
            motor.status = "RUNNING"
            motor.fault_code = 0
            motor.runtime = random.uniform(500, 8000)
            self.update_motor_readings(motor)
    
    def update_motor_readings(self, motor):
        if motor.status == "RUNNING":
            ranges = motor.ranges
            motor.current = round(random.uniform(ranges["current"][0], ranges["current"][1]), 1)
            motor.temperature = round(random.uniform(ranges["temperature"][0], ranges["temperature"][1]), 1)
            motor.vibration = round(random.uniform(ranges["vibration"][0], ranges["vibration"][1]), 2)
            motor.power_consumption = round(motor.current * 415 * 1.732 / 1000, 1)
            motor.runtime += 0.1
            motor.efficiency = round(92.5 + random.uniform(-3, 2), 1)
        elif motor.status == "STOPPED":
            motor.current = 0
            motor.temperature = round(random.uniform(30, 45), 1)
            motor.vibration = 0
            motor.power_consumption = 0
        elif motor.status == "FAULT":
            motor.current = round(random.uniform(motor.ranges["current"][1] * 1.2, motor.ranges["current"][1] * 1.8), 1)
            motor.temperature = round(random.uniform(motor.ranges["temperature"][1] * 1.1, motor.ranges["temperature"][1] * 1.4), 1)
            motor.vibration = round(random.uniform(motor.ranges["vibration"][1] * 1.2, motor.ranges["vibration"][1] * 1.6), 2)
            motor.power_consumption = round(motor.current * 415 * 1.732 / 1000, 1)
            motor.efficiency = round(65 + random.uniform(0, 15), 1)
    
    def check_alerts(self, motor):
        alerts = []
        if motor.status == "FAULT":
            alerts.append(f"CRITICAL: {motor.name} - Fault Code {motor.fault_code}")
        if motor.status == "RUNNING":
            if motor.current > motor.thresholds["current_high"]:
                alerts.append(f"WARNING: {motor.name} - High Current ({motor.current}A)")
            if motor.temperature > motor.thresholds["temp_high"]:
                alerts.append(f"WARNING: {motor.name} - High Temperature ({motor.temperature}°C)")
            if motor.vibration > motor.thresholds["vibration_high"]:
                alerts.append(f"ALERT: {motor.name} - Excessive Vibration ({motor.vibration}mm/s)")
            if motor.efficiency < 85:
                alerts.append(f"INFO: {motor.name} - Low Efficiency ({motor.efficiency}%)")
        return alerts
    
    def update_all(self):
        all_alerts = []
        for motor in self.motors:
            self.update_motor_readings(motor)
            motor.update_history()
            motor.current_trend = motor.compute_trend(motor.current_history)
            motor.temp_trend = motor.compute_trend(motor.temp_history)
            motor.vibe_trend = motor.compute_trend(motor.vibe_history)
            motor.run_fft()
            motor.compute_health()
            alerts = self.check_alerts(motor)
            if motor.status == "RUNNING":
                if motor.current_trend == "rising":
                    alerts.append(f"TREND: {motor.name} - Current rising steadily ({motor.current}A)")
                if motor.vibe_trend == "rising":
                    alerts.append(f"TREND: {motor.name} - Vibration rising steadily ({motor.vibration}mm/s)")
                if motor.fft_alarm:
                    alerts.append(f"FFT ALARM: {motor.name} - Abnormal vibration frequency ({motor.dominant_freq_hz}Hz)")
                if motor.health_score < 50:
                    alerts.append(f"HEALTH: {motor.name} - Health score low ({motor.health_score}%)")
            all_alerts.extend(alerts)
        return all_alerts
    
    def reset_all(self):
        for motor in self.motors:
            motor.status = "RUNNING"
            motor.fault_code = 0
            self.update_motor_readings(motor)
    
    def random_fault(self):
        motor = random.choice(self.motors)
        motor.status = "FAULT"
        motor.fault_code = random.randint(1, 5)
        return motor.name, motor.fault_code
    
    def start_motor(self, motor_name):
        for motor in self.motors:
            if motor.name == motor_name and motor.status == "STOPPED":
                motor.status = "RUNNING"
                return True
        return False
    
    def stop_motor(self, motor_name):
        for motor in self.motors:
            if motor.name == motor_name and motor.status == "RUNNING":
                motor.status = "STOPPED"
                return True
        return False

# ==================== DATABASE MANAGER ====================
class DatabaseManager:
    def __init__(self, db_path="motor_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS motor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                motor_name TEXT,
                timestamp TEXT,
                status TEXT,
                current REAL,
                temperature REAL,
                vibration REAL,
                runtime REAL,
                power REAL,
                efficiency REAL,
                fault_code INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                alert_level TEXT,
                motor_name TEXT,
                message TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_reading(self, motor):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO motor_readings (motor_name, timestamp, status, current, temperature, vibration, runtime, power, efficiency, fault_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (motor.name, datetime.now().isoformat(), motor.status, motor.current, 
              motor.temperature, motor.vibration, motor.runtime, motor.power_consumption, 
              motor.efficiency, motor.fault_code))
        conn.commit()
        conn.close()
    
    def save_alert(self, alert_level, motor_name, message):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (timestamp, alert_level, motor_name, message)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), alert_level, motor_name, message))
        conn.commit()
        conn.close()
    
    def get_history(self, motor_name, limit=100):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, current, temperature, vibration, status, power, efficiency
            FROM motor_readings
            WHERE motor_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (motor_name, limit))
        rows = cursor.fetchall()
        conn.close()
        return list(reversed(rows))
    
    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE timestamp > datetime('now', '-24 hours')")
        stats['alerts_24h'] = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(current), AVG(temperature) FROM motor_readings WHERE timestamp > datetime('now', '-1 hour')")
        row = cursor.fetchone()
        stats['avg_current'] = round(row[0], 1) if row[0] else 0
        stats['avg_temp'] = round(row[1], 1) if row[1] else 0
        conn.close()
        return stats

# ==================== ICON MANAGER ====================
class IconManager:
    @staticmethod
    def get_icon(icon_name, color="#60a5fa", size=20):
        if icon_name == "motor":
            return MotorIconCreator.create_small_motor_icon(size, color)
        
        icon_map = {
            "start": QStyle.SP_MediaPlay,
            "stop": QStyle.SP_MediaStop,
            "details": QStyle.SP_FileDialogInfoView,
            "settings": QStyle.SP_FileDialogDetailedView,
            "export": QStyle.SP_DialogSaveButton,
            "reset": QStyle.SP_BrowserReload,
            "fault": QStyle.SP_MessageBoxCritical,
            "running": QStyle.SP_DriveCDIcon,
            "stopped": QStyle.SP_MediaStop,
            "fault_icon": QStyle.SP_MessageBoxCritical,
        }
        if icon_name in icon_map:
            return QApplication.style().standardIcon(icon_map[icon_name])
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(color)))
        painter.setPen(QPen(QColor(color), 2))
        painter.drawEllipse(2, 2, size-4, size-4)
        painter.end()
        return QIcon(pixmap)

# ==================== ENHANCED MOTOR CARD ====================
class EnhancedMotorCard(QFrame):
    def __init__(self, motor_data, parent=None):
        super().__init__(parent)
        self.motor = motor_data
        self.parent_dashboard = parent
        self.setMinimumSize(280, 260)
        self.setCursor(Qt.PointingHandCursor)
        self.setup_ui()
        self.update_display()
        
        # Add glow effect on hover
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(0)
        self.glow.setColor(QColor(59, 130, 246))
        self.setGraphicsEffect(self.glow)
        
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def setup_ui(self):
        AF = "Segoe UI"
        self.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a26, stop:1 #14141f);
                border-radius: 12px;
                border: 1px solid #2a2a38;
            }
            QFrame:hover {
                border: 1px solid #3b82f6;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e30, stop:1 #161622);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(16, 14, 16, 12)
        
        header_layout = QHBoxLayout()
        self.motor_icon = QLabel()
        self.motor_icon.setPixmap(MotorIconCreator.create_small_motor_icon(32, "#60a5fa").pixmap(32, 32))
        header_layout.addWidget(self.motor_icon)
        
        name = QLabel(self.motor.name)
        name.setFont(QFont(AF, 11, QFont.Weight.Bold))
        name.setStyleSheet("color: #f3f4f6;")
        name.setWordWrap(True)
        header_layout.addWidget(name, 1)
        
        # LED status indicator
        self.led = QLabel()
        self.led.setFixedSize(12, 12)
        self.led.setStyleSheet("background-color: #4ade80; border-radius: 6px;")
        header_layout.addWidget(self.led)
        
        layout.addLayout(header_layout)
        
        info_row = QHBoxLayout()
        type_label = QLabel(f"📌 {self.motor.type}")
        type_label.setFont(QFont(AF, 9))
        type_label.setStyleSheet("color: #6b7280;")
        info_row.addWidget(type_label)
        info_row.addStretch()
        self.runtime_label = QLabel()
        self.runtime_label.setFont(QFont(AF, 9))
        self.runtime_label.setStyleSheet("color: #6b7280;")
        info_row.addWidget(self.runtime_label)
        layout.addLayout(info_row)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #2a2a38; max-height: 1px;")
        layout.addWidget(sep)
        
        readings = QGridLayout()
        readings.setSpacing(6)
        
        current_icon = QLabel("⚡")
        current_icon.setStyleSheet("color: #f59e0b; font-size: 14px;")
        readings.addWidget(current_icon, 0, 0)
        self.current_label = QLabel()
        readings.addWidget(self.current_label, 0, 1)
        
        temp_icon = QLabel("🌡️")
        temp_icon.setStyleSheet("color: #ef4444; font-size: 14px;")
        readings.addWidget(temp_icon, 1, 0)
        self.temp_label = QLabel()
        readings.addWidget(self.temp_label, 1, 1)
        
        vibe_icon = QLabel("📳")
        vibe_icon.setStyleSheet("color: #8b5cf6; font-size: 14px;")
        readings.addWidget(vibe_icon, 2, 0)
        self.vibe_label = QLabel()
        readings.addWidget(self.vibe_label, 2, 1)
        
        power_icon = QLabel("🔌")
        power_icon.setStyleSheet("color: #10b981; font-size: 14px;")
        readings.addWidget(power_icon, 3, 0)
        self.power_label = QLabel()
        readings.addWidget(self.power_label, 3, 1)
        
        layout.addLayout(readings)
        
        health_layout = QHBoxLayout()
        health_icon = QLabel("❤️")
        health_icon.setStyleSheet("color: #ef4444; font-size: 12px;")
        health_layout.addWidget(health_icon)
        
        hl = QLabel("Health")
        hl.setFont(QFont(AF, 9))
        hl.setStyleSheet("color: #6b7280;")
        health_layout.addWidget(hl)
        
        self.health_bar = GradientProgressBar()
        health_layout.addWidget(self.health_bar, 1)
        
        self.health_pct = QLabel("100%")
        self.health_pct.setFont(QFont(AF, 9, QFont.Weight.Bold))
        health_layout.addWidget(self.health_pct)
        layout.addLayout(health_layout)
        
        trend_layout = QHBoxLayout()
        self.trend_icons = []
        for i in range(3):
            icon = QLabel()
            icon.setFixedSize(20, 20)
            trend_layout.addWidget(icon)
            if i < 2:
                trend_layout.addSpacing(8)
            self.trend_icons.append(icon)
        trend_layout.addStretch()
        self.fft_indicator = QLabel()
        trend_layout.addWidget(self.fft_indicator)
        layout.addLayout(trend_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.start_btn = QPushButton(" Start")
        self.start_btn.setIcon(IconManager.get_icon("start", "#86efac"))
        self.start_btn.clicked.connect(self.start_motor)
        
        self.stop_btn = QPushButton(" Stop")
        self.stop_btn.setIcon(IconManager.get_icon("stop", "#fca5a5"))
        self.stop_btn.clicked.connect(self.stop_motor)
        
        self.detail_btn = QPushButton(" Details")
        self.detail_btn.setIcon(IconManager.get_icon("details", "#93c5fd"))
        self.detail_btn.clicked.connect(self.show_details)
        
        for btn in [self.start_btn, self.stop_btn, self.detail_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1f2937;
                    color: #d1d5db;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    padding: 6px 8px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #273344;
                }
            """)
            btn_layout.addWidget(btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def start_motor(self):
        if self.parent_dashboard.simulator.start_motor(self.motor.name):
            self.parent_dashboard.show_toast(f"✅ {self.motor.name} started")
    
    def stop_motor(self):
        if self.parent_dashboard.simulator.stop_motor(self.motor.name):
            self.parent_dashboard.show_toast(f"⏹️ {self.motor.name} stopped")
    
    def show_details(self):
        history = self.parent_dashboard.db_manager.get_history(self.motor.name, 50)
        self.detail_window = MotorDetailWindow(self.motor, history, self.parent_dashboard)
        self.detail_window.show()
    
    def update_display(self):
        BRIGHT = "color: #d1d5db; font-size: 10px;"
        WARN = "color: #fb923c; font-weight: bold; font-size: 10px;"
        MUTED = "color: #4b5563; font-size: 10px;"
        RED = "color: #f87171; font-weight: bold; font-size: 10px;"
        
        self.runtime_label.setText(f"⏱️ {self.motor.runtime:.0f}h")
        
        if self.motor.status == "RUNNING":
            self.led.setStyleSheet("background-color: #4ade80; border-radius: 6px;")
            self.current_label.setText(f"{self.motor.current} A")
            self.temp_label.setText(f"{self.motor.temperature}°C")
            self.vibe_label.setText(f"{self.motor.vibration} mm/s")
            self.power_label.setText(f"{self.motor.power_consumption} kW")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        elif self.motor.status == "STOPPED":
            self.led.setStyleSheet("background-color: #f59e0b; border-radius: 6px;")
            self.current_label.setText("0 A")
            self.temp_label.setText(f"{self.motor.temperature}°C")
            self.vibe_label.setText("0 mm/s")
            self.power_label.setText("0 kW")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        else:
            self.led.setStyleSheet("background-color: #ef4444; border-radius: 6px;")
            self.current_label.setText(f"{self.motor.current} A")
            self.temp_label.setText(f"{self.motor.temperature}°C")
            self.vibe_label.setText(f"{self.motor.vibration} mm/s")
            self.power_label.setText(f"{self.motor.power_consumption} kW")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        
        h = int(self.motor.health_score)
        self.health_bar.setValue(h)
        self.health_pct.setText(f"{h}%")
        
        trend_symbols = {"rising": "▲", "falling": "▼", "stable": "●"}
        trend_colors = {"rising": "#f97316", "falling": "#60a5fa", "stable": "#22c55e"}
        for icon, param in zip(self.trend_icons, ["current_trend", "temp_trend", "vibe_trend"]):
            trend = getattr(self.motor, param, "stable")
            icon.setText(trend_symbols.get(trend, "●"))
            icon.setStyleSheet(f"color: {trend_colors.get(trend, '#6b7280')}; font-size: 12px;")
        
        if self.motor.fft_alarm:
            self.fft_indicator.setText("⚠️ FFT!")
            self.fft_indicator.setStyleSheet("color: #ef4444; font-size: 10px;")
        else:
            self.fft_indicator.setText("")
    
    def enterEvent(self, event):
        self.glow.setBlurRadius(15)
        self.animation.setStartValue(self.minimumHeight())
        self.animation.setEndValue(self.minimumHeight() + 5)
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.glow.setBlurRadius(0)
        self.animation.setStartValue(self.minimumHeight() + 5)
        self.animation.setEndValue(self.minimumHeight())
        self.animation.start()
        super().leaveEvent(event)

# ==================== MOTOR DETAIL WINDOW ====================
class MotorDetailWindow(QDialog):
    def __init__(self, motor, history_data, parent=None):
        super().__init__(parent)
        self.motor = motor
        self.history_data = history_data
        self.setup_ui()
        self.setWindowTitle(f"🔧 Motor Details - {motor.name}")
        self.setGeometry(200, 100, 800, 900)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; }
            QLabel { color: #e4e4e7; }
            QGroupBox { border: 1px solid #3d3d4a; border-radius: 10px; margin-top: 10px; padding-top: 14px; color: #60a5fa; background-color: #1e1e2e; }
            QPushButton { background-color: #3d3d4a; color: #e4e4e7; border: none; padding: 8px 16px; border-radius: 6px; }
            QPushButton:hover { background-color: #4d4d5a; }
            QTextEdit { background-color: #2d2d3a; color: #e4e4e7; border: 1px solid #3d3d4a; border-radius: 8px; font-family: monospace; }
            QTabWidget::pane { background-color: #1e1e2e; border: 1px solid #3d3d4a; border-radius: 8px; }
            QTabBar::tab { background-color: #2d2d3a; color: #9ca3af; padding: 8px 16px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #3b82f6; color: white; }
        """)
    
    def setup_ui(self):
        outer = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Header with icon
        header_layout = QHBoxLayout()
        motor_icon = QLabel()
        motor_icon.setPixmap(MotorIconCreator.create_small_motor_icon(48, "#60a5fa").pixmap(48, 48))
        header_layout.addWidget(motor_icon)
        
        header_text = QLabel(self.motor.name)
        header_text.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header_text.setStyleSheet("color: #60a5fa;")
        header_layout.addWidget(header_text)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        info = QLabel(f"Type: {self.motor.type} | Runtime: {self.motor.runtime:.0f} hours")
        info.setStyleSheet("color: #9ca3af;")
        layout.addWidget(info)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Tab 1: Current Readings
        current_tab = self.create_current_tab()
        tabs.addTab(current_tab, "📊 Current Readings")
        
        # Tab 2: Trends
        trends_tab = self.create_trends_tab()
        tabs.addTab(trends_tab, "📈 Trends")
        
        # Tab 3: FFT Analysis
        fft_tab = self.create_fft_tab()
        tabs.addTab(fft_tab, "🎵 FFT Analysis")
        
        # Tab 4: History
        history_tab = self.create_history_tab()
        tabs.addTab(history_tab, "📜 History")
        
        layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.update_display)
        export_btn = QPushButton("💾 Export")
        export_btn.clicked.connect(self.export_history)
        close_btn = QPushButton("✖️ Close")
        close_btn.clicked.connect(self.close)
        
        for btn in [refresh_btn, export_btn, close_btn]:
            btn_layout.addWidget(btn)
        
        layout.addLayout(btn_layout)
        
        scroll.setWidget(content)
        outer.addWidget(scroll)
        self.setLayout(outer)
        self.update_display()
    
    def create_current_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Readings
        readings = QGroupBox("Live Readings")
        rl = QGridLayout()
        self.current_lbl = QLabel()
        self.temp_lbl = QLabel()
        self.vibe_lbl = QLabel()
        self.power_lbl = QLabel()
        self.eff_lbl = QLabel()
        
        rl.addWidget(QLabel("⚡ Current:"), 0, 0)
        rl.addWidget(self.current_lbl, 0, 1)
        rl.addWidget(QLabel("🌡️ Temperature:"), 1, 0)
        rl.addWidget(self.temp_lbl, 1, 1)
        rl.addWidget(QLabel("📳 Vibration:"), 2, 0)
        rl.addWidget(self.vibe_lbl, 2, 1)
        rl.addWidget(QLabel("🔌 Power:"), 3, 0)
        rl.addWidget(self.power_lbl, 3, 1)
        rl.addWidget(QLabel("📈 Efficiency:"), 4, 0)
        rl.addWidget(self.eff_lbl, 4, 1)
        
        readings.setLayout(rl)
        layout.addWidget(readings)
        
        # Health
        health_group = QGroupBox("❤️ Health Score")
        hl = QHBoxLayout()
        self.health_bar = GradientProgressBar()
        self.health_bar.setFixedHeight(20)
        self.health_lbl = QLabel()
        self.health_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        hl.addWidget(self.health_bar)
        hl.addWidget(self.health_lbl)
        health_group.setLayout(hl)
        layout.addWidget(health_group)
        
        # Trends
        trends = QGroupBox("📊 Trends")
        tl = QGridLayout()
        self.current_trend_lbl = QLabel()
        self.temp_trend_lbl = QLabel()
        self.vibe_trend_lbl = QLabel()
        
        tl.addWidget(QLabel("Current trend:"), 0, 0)
        tl.addWidget(self.current_trend_lbl, 0, 1)
        tl.addWidget(QLabel("Temperature trend:"), 1, 0)
        tl.addWidget(self.temp_trend_lbl, 1, 1)
        tl.addWidget(QLabel("Vibration trend:"), 2, 0)
        tl.addWidget(self.vibe_trend_lbl, 2, 1)
        trends.setLayout(tl)
        layout.addWidget(trends)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_trends_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Simple trend display using QTextEdit for now
        trend_text = QTextEdit()
        trend_text.setReadOnly(True)
        self.trend_display = trend_text
        layout.addWidget(trend_text)
        
        widget.setLayout(layout)
        return widget
    
    def create_fft_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        fft_group = QGroupBox("Frequency Analysis")
        fl = QVBoxLayout()
        self.fft_freq_lbl = QLabel()
        self.fft_freq_lbl.setFont(QFont("Segoe UI", 12))
        self.fft_alarm_lbl = QLabel()
        self.fft_alarm_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        fl.addWidget(self.fft_freq_lbl)
        fl.addWidget(self.fft_alarm_lbl)
        fft_group.setLayout(fl)
        layout.addWidget(fft_group)
        
        # Vibration data
        vibe_group = QGroupBox("Recent Vibration Data")
        self.vibe_text = QTextEdit()
        self.vibe_text.setReadOnly(True)
        self.vibe_text.setMaximumHeight(200)
        vibe_layout = QVBoxLayout()
        vibe_layout.addWidget(self.vibe_text)
        vibe_group.setLayout(vibe_layout)
        layout.addWidget(vibe_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        layout.addWidget(self.history_text)
        
        widget.setLayout(layout)
        return widget
    
    def update_display(self):
        # Update current readings
        self.current_lbl.setText(f"{self.motor.current} A")
        self.temp_lbl.setText(f"{self.motor.temperature} °C")
        self.vibe_lbl.setText(f"{self.motor.vibration} mm/s")
        self.power_lbl.setText(f"{self.motor.power_consumption} kW")
        self.eff_lbl.setText(f"{self.motor.efficiency}%")
        
        # Update health
        self.health_bar.setValue(int(self.motor.health_score))
        self.health_lbl.setText(f"{self.motor.health_score}%")
        
        # Update trends
        trend_symbols = {"rising": "📈 Rising", "falling": "📉 Falling", "stable": "➡️ Stable"}
        trend_colors = {"rising": "#f97316", "falling": "#60a5fa", "stable": "#22c55e"}
        
        self.current_trend_lbl.setText(trend_symbols.get(self.motor.current_trend, "Stable"))
        self.current_trend_lbl.setStyleSheet(f"color: {trend_colors.get(self.motor.current_trend, '#e4e4e7')};")
        self.temp_trend_lbl.setText(trend_symbols.get(self.motor.temp_trend, "Stable"))
        self.temp_trend_lbl.setStyleSheet(f"color: {trend_colors.get(self.motor.temp_trend, '#e4e4e7')};")
        self.vibe_trend_lbl.setText(trend_symbols.get(self.motor.vibe_trend, "Stable"))
        self.vibe_trend_lbl.setStyleSheet(f"color: {trend_colors.get(self.motor.vibe_trend, '#e4e4e7')};")
        
        # Update trend display
        trend_text = "Recent Values:\n\n"
        trend_text += "Sample\tCurrent\tTemp\tVibe\n"
        trend_text += "-" * 40 + "\n"
        for i in range(min(20, len(self.motor.current_history))):
            trend_text += f"{i+1}\t{self.motor.current_history[i]:.1f}\t{self.motor.temp_history[i]:.1f}\t{self.motor.vibe_history[i]:.2f}\n"
        self.trend_display.setText(trend_text)
        
        # Update FFT
        self.fft_freq_lbl.setText(f"🎵 Dominant Frequency: {self.motor.dominant_freq_hz} Hz")
        if self.motor.fft_alarm:
            self.fft_alarm_lbl.setText("⚠️ ABNORMAL FREQUENCY DETECTED!")
            self.fft_alarm_lbl.setStyleSheet("color: #ef4444;")
        else:
            self.fft_alarm_lbl.setText("✅ Normal Vibration Pattern")
            self.fft_alarm_lbl.setStyleSheet("color: #22c55e;")
        
        # Update vibration data
        vibe_text = "Last 10 vibration readings (mm/s):\n\n"
        for i, val in enumerate(self.motor.vibe_history[-10:]):
            vibe_text += f"Reading {i+1}: {val:.2f} mm/s\n"
        self.vibe_text.setText(vibe_text)
        
        # Update history
        text = "Time\t\tStatus\tCurrent\tTemp\tVibe\tPower\n"
        text += "-" * 70 + "\n"
        for row in self.history_data[-15:]:
            timestamp = row[0][11:19] if len(row[0]) > 11 else row[0]
            status = row[4][:8]
            current = row[1]
            temp = row[2]
            vibe = row[3]
            power = row[5] if len(row) > 5 else 0
            text += f"{timestamp}\t{status}\t{current:.1f}\t{temp:.1f}\t{vibe:.2f}\t{power:.1f}\n"
        self.history_text.setText(text)
    
    def export_history(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export History", f"{self.motor.name}_history.csv", "CSV (*.csv)")
        if filename:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Status", "Current", "Temperature", "Vibration", "Power", "Efficiency"])
                for row in self.history_data:
                    writer.writerow([row[0], row[4], row[1], row[2], row[3], row[5] if len(row) > 5 else "", row[6] if len(row) > 6 else ""])
            self.parent().show_toast(f"✅ History exported to {filename}")

# ==================== SETTINGS DIALOG ====================
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("⚙️ Settings")
        self.setGeometry(300, 300, 550, 450)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e2e; }
            QLabel { color: #e4e4e7; }
            QTabWidget::pane { background-color: #2d2d3a; border-radius: 8px; }
            QDoubleSpinBox, QSpinBox { background-color: #2d2d3a; color: #e4e4e7; padding: 6px; border: 1px solid #3d3d4a; border-radius: 5px; }
            QPushButton { background-color: #3d3d4a; color: #e4e4e7; border: none; padding: 8px 16px; border-radius: 6px; }
            QPushButton:hover { background-color: #4d4d5a; }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("⚙️ System Configuration")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #60a5fa;")
        layout.addWidget(title)
        
        tabs = QTabWidget()
        
        # Thresholds Tab
        thresh_tab = QWidget()
        thresh_layout = QFormLayout()
        thresh_layout.setSpacing(20)
        thresh_layout.setContentsMargins(20, 20, 20, 20)
        
        self.current_thresh = QDoubleSpinBox()
        self.current_thresh.setRange(50, 200)
        self.current_thresh.setValue(self.parent.simulator.motors[0].thresholds["current_high"])
        self.temp_thresh = QDoubleSpinBox()
        self.temp_thresh.setRange(60, 120)
        self.temp_thresh.setValue(self.parent.simulator.motors[0].thresholds["temp_high"])
        self.vibe_thresh = QDoubleSpinBox()
        self.vibe_thresh.setRange(3, 15)
        self.vibe_thresh.setValue(self.parent.simulator.motors[0].thresholds["vibration_high"])
        
        thresh_layout.addRow("⚡ Current High Alert (A):", self.current_thresh)
        thresh_layout.addRow("🌡️ Temperature High Alert (°C):", self.temp_thresh)
        thresh_layout.addRow("📳 Vibration High Alert (mm/s):", self.vibe_thresh)
        thresh_tab.setLayout(thresh_layout)
        
        # Database Tab
        db_tab = QWidget()
        db_layout = QVBoxLayout()
        db_layout.setContentsMargins(20, 20, 20, 20)
        self.db_info = QLabel()
        self.db_info.setWordWrap(True)
        self.db_info.setStyleSheet("background-color: #111118; padding: 15px; border-radius: 8px; font-family: monospace;")
        db_layout.addWidget(self.db_info)
        
        clear_btn = QPushButton("🗑️ Clear Alert History")
        clear_btn.clicked.connect(self.clear_alerts)
        db_layout.addWidget(clear_btn)
        db_tab.setLayout(db_layout)
        
        tabs.addTab(thresh_tab, "⚠️ Alert Thresholds")
        tabs.addTab(db_tab, "💾 Database")
        layout.addWidget(tabs)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.update_db_info()
    
    def update_db_info(self):
        stats = self.parent.db_manager.get_statistics()
        self.db_info.setText(f"📊 Database Statistics:\n\n"
                            f"• 🚨 Alerts in last 24 hours: {stats['alerts_24h']}\n"
                            f"• ⚡ Average Current (1h): {stats['avg_current']} A\n"
                            f"• 🌡️ Average Temperature (1h): {stats['avg_temp']} °C")
    
    def clear_alerts(self):
        reply = QMessageBox.question(self, "⚠️ Confirm", "Clear all alert history?\n\nThis action cannot be undone.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(self.parent.db_manager.db_path)
            conn.execute("DELETE FROM alerts")
            conn.commit()
            conn.close()
            QMessageBox.information(self, "✅ Success", "Alert history cleared!")
            self.update_db_info()
    
    def save_settings(self):
        for motor in self.parent.simulator.motors:
            motor.thresholds["current_high"] = self.current_thresh.value()
            motor.thresholds["temp_high"] = self.temp_thresh.value()
            motor.thresholds["vibration_high"] = self.vibe_thresh.value()
        self.accept()
        self.parent.show_toast("✅ Settings saved successfully!")

# ==================== MAIN DASHBOARD ====================
class MonitoringDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.simulator = MotorSimulator()
        self.db_manager = DatabaseManager()
        self.motor_cards = []
        self.alerts_history = []
        self.setup_ui()
        self.setup_timer()
        self.show_toast("🚀 System ready! Monitoring active.")
    
    def setup_ui(self):
        self.setWindowTitle("🏭 MCC Condition Monitoring System")
        self.setGeometry(100, 60, 1400, 900)
        
        # Set app icon
        app_icon = MotorIconCreator.create_motor_icon(64, "#3b82f6")
        self.setWindowIcon(app_icon)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with gradient
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-bottom: 2px solid #3b82f6;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        # Logo and title
        title_layout = QHBoxLayout()
        motor_icon_label = QLabel()
        motor_icon_label.setPixmap(MotorIconCreator.create_small_motor_icon(40, "#60a5fa").pixmap(40, 40))
        title_layout.addWidget(motor_icon_label)
        
        title = QLabel("MCC Condition Monitoring System")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #f9fafb;")
        title_layout.addWidget(title)
        header_layout.addLayout(title_layout)
        
        header_layout.addStretch()
        
        # Metrics row
        self.metrics_layout = QHBoxLayout()
        self.metrics_layout.setSpacing(15)
        
        self.running_metric = MetricCard("Running", "0/6", "motors", "🟢", "#4ade80")
        self.fault_metric = MetricCard("Faults", "0", "active", "🔴", "#ef4444")
        self.alerts_metric = MetricCard("Alerts", "0", "24h", "⚠️", "#f59e0b")
        self.efficiency_metric = MetricCard("Efficiency", "92.5", "%", "📈", "#60a5fa")
        
        self.metrics_layout.addWidget(self.running_metric)
        self.metrics_layout.addWidget(self.fault_metric)
        self.metrics_layout.addWidget(self.alerts_metric)
        self.metrics_layout.addWidget(self.efficiency_metric)
        header_layout.addLayout(self.metrics_layout)
        
        # Theme toggle
        self.theme_toggle = ThemeToggle()
        header_layout.addWidget(self.theme_toggle)
        
        # Time label
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #6b7280; background-color: #1f2937; padding: 8px 16px; border-radius: 20px;")
        header_layout.addWidget(self.time_label)
        
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(6)
        
        # Motor grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(400)
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(24, 24, 24, 24)
        
        positions = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]
        for i, (row, col) in enumerate(positions):
            if i < len(self.simulator.motors):
                card = EnhancedMotorCard(self.simulator.motors[i], self)
                grid_layout.addWidget(card, row, col)
                self.motor_cards.append(card)
        
        for r in range(2):
            grid_layout.setRowStretch(r, 1)
        for c in range(3):
            grid_layout.setColumnStretch(c, 1)
        
        scroll.setWidget(grid_widget)
        splitter.addWidget(scroll)
        
        # Bottom panel
        bottom = QWidget()
        bottom.setMinimumHeight(220)
        bottom.setMaximumHeight(380)
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(24, 16, 24, 20)
        
        # Alerts
        alerts_group = QGroupBox("🚨 Alerts & Events")
        alerts_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #2a2a38;
                border-radius: 12px;
                padding-top: 12px;
            }
        """)
        alerts_layout = QVBoxLayout()
        self.alerts_text = QTextEdit()
        self.alerts_text.setReadOnly(True)
        self.alerts_text.setMinimumHeight(150)
        alerts_layout.addWidget(self.alerts_text)
        alerts_group.setLayout(alerts_layout)
        bottom_layout.addWidget(alerts_group, 3)
        
        # Controls
        controls_group = QGroupBox("🎮 Control Panel")
        controls_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #2a2a38;
                border-radius: 12px;
                padding-top: 12px;
            }
        """)
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(12)
        
        self.stats_label = QLabel("📊 System Status")
        self.stats_label.setStyleSheet("color: #93c5fd; font-weight: bold; font-size: 12px; padding: 8px; background-color: #111118; border-radius: 8px;")
        controls_layout.addWidget(self.stats_label)
        
        self.db_stats_label = QLabel("💾 Database: Loading...")
        self.db_stats_label.setStyleSheet("color: #6b7280; padding: 4px;")
        controls_layout.addWidget(self.db_stats_label)
        
        controls_layout.addSpacing(8)
        
        # Buttons with icons
        self.export_btn = QPushButton("💾 Export Report")
        self.reset_btn = QPushButton("🔄 Reset All")
        self.fault_btn = QPushButton("⚠️ Random Fault")
        self.settings_btn = QPushButton("⚙️ Settings")
        
        self.export_btn.clicked.connect(self.export_report)
        self.reset_btn.clicked.connect(self.reset_simulation)
        self.fault_btn.clicked.connect(self.random_fault)
        self.settings_btn.clicked.connect(self.open_settings)
        
        for btn in [self.export_btn, self.reset_btn, self.fault_btn, self.settings_btn]:
            btn.setMinimumHeight(38)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1f2937;
                    color: #e4e4e7;
                    border: 1px solid #374151;
                    border-radius: 8px;
                    padding: 8px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #273344;
                    border-color: #4b5563;
                }
            """)
            controls_layout.addWidget(btn)
        
        controls_layout.addStretch()
        controls_group.setLayout(controls_layout)
        bottom_layout.addWidget(controls_group, 1)
        
        splitter.addWidget(bottom)
        splitter.setSizes([700, 260])
        layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #111118, stop:1 #0a0a12);
                border-top: 1px solid #1f1f2e;
                color: #6b7280;
                padding: 4px 16px;
            }
        """)
        self.status_label = QLabel("🟢 System ready • Monitoring active")
        self.statusBar().addWidget(self.status_label)
        
        self.perf_indicator = QLabel("📊 All systems normal")
        self.perf_indicator.setStyleSheet("color: #22c55e;")
        self.statusBar().addPermanentWidget(self.perf_indicator)
        
        self.update_dashboard()
    
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(2000)
    
    def show_toast(self, message):
        toast = ToastNotification(message, self)
        toast.show()
    
    def add_alert(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if "CRITICAL" in message or "FAULT" in message:
            icon = "🔴"
        elif "WARNING" in message or "ALERT" in message:
            icon = "🟡"
        elif "TREND" in message or "FFT" in message:
            icon = "📊"
        else:
            icon = "ℹ️"
        
        self.alerts_text.append(f"[{timestamp}] {icon} {message}")
        self.alerts_history.append([timestamp, "INFO", "System", message])
        
        scrollbar = self.alerts_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Show toast for important alerts
        if "CRITICAL" in message or "FAULT" in message:
            self.show_toast(message[:50])
    
    def update_dashboard(self):
        self.time_label.setText(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        alerts = self.simulator.update_all()
        
        running = sum(1 for c in self.motor_cards if c.motor.status == "RUNNING")
        fault = sum(1 for c in self.motor_cards if c.motor.status == "FAULT")
        stopped = sum(1 for c in self.motor_cards if c.motor.status == "STOPPED")
        
        # Update metrics
        self.running_metric.update_value(f"{running}/6")
        self.fault_metric.update_value(str(fault))
        
        # Calculate average efficiency
        avg_efficiency = sum(m.efficiency for m in self.simulator.motors if m.status == "RUNNING") / max(running, 1)
        self.efficiency_metric.update_value(f"{avg_efficiency:.1f}")
        
        self.stats_label.setText(f"📊 Running: {running} | Faults: {fault} | Stopped: {stopped}")
        
        for card in self.motor_cards:
            card.update_display()
            self.db_manager.save_reading(card.motor)
        
        stats = self.db_manager.get_statistics()
        self.alerts_metric.update_value(str(stats['alerts_24h']))
        self.db_stats_label.setText(f"💾 Alerts (24h): {stats['alerts_24h']} | ⚡ Avg Current: {stats['avg_current']} A | 🌡️ Avg Temp: {stats['avg_temp']} °C")
        
        if fault > 0:
            self.perf_indicator.setText("⚠️ FAULTS DETECTED")
            self.perf_indicator.setStyleSheet("color: #ef4444;")
        elif running == 6:
            self.perf_indicator.setText("✅ All systems optimal")
            self.perf_indicator.setStyleSheet("color: #22c55e;")
        else:
            self.perf_indicator.setText("📊 Normal operation")
            self.perf_indicator.setStyleSheet("color: #60a5fa;")
        
        if alerts:
            for alert in alerts:
                self.add_alert(alert)
                level = "CRITICAL" if "CRITICAL" in alert else "WARNING" if "WARNING" in alert else "INFO"
                motor = alert.split(":")[1].split("-")[0].strip() if ":" in alert else "System"
                self.db_manager.save_alert(level, motor, alert)
            self.status_label.setText(f"⚠️ ALERT: {alerts[0][:80]}")
        else:
            self.status_label.setText("🟢 All systems normal — Monitoring active")
    
    def export_report(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Report", f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "CSV (*.csv)")
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["=" * 70])
                    writer.writerow(["🏭 MCC CONDITION MONITORING SYSTEM - FULL REPORT"])
                    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                    writer.writerow(["=" * 70])
                    writer.writerow([])
                    writer.writerow(["📊 MOTOR STATUS SUMMARY"])
                    writer.writerow(["Motor Name", "Type", "Status", "Current (A)", 
                                    "Temperature (°C)", "Vibration (mm/s)", 
                                    "Power (kW)", "Efficiency (%)", "Runtime (hrs)", "Health Score (%)"])
                    
                    for motor in self.simulator.motors:
                        writer.writerow([
                            motor.name, motor.type, motor.status,
                            motor.current if motor.status == "RUNNING" else 0,
                            motor.temperature,
                            motor.vibration if motor.status == "RUNNING" else 0,
                            motor.power_consumption if motor.status == "RUNNING" else 0,
                            motor.efficiency if motor.status == "RUNNING" else "--",
                            f"{motor.runtime:.0f}",
                            motor.health_score
                        ])
                    
                    writer.writerow([])
                    writer.writerow(["🚨 ALERTS HISTORY (Last 50)"])
                    writer.writerow(["Timestamp", "Level", "Motor", "Message"])
                    for alert in self.alerts_history[-50:]:
                        writer.writerow(alert)
                
                self.show_toast(f"✅ Report saved to {filename}")
                QMessageBox.information(self, "✅ Success", f"Full report saved!\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "❌ Error", f"Failed: {str(e)}")
    
    def reset_simulation(self):
        self.simulator.reset_all()
        self.add_alert("🔄 SYSTEM: All motors reset to RUNNING state")
        self.show_toast("All motors reset successfully!")
    
    def random_fault(self):
        name, code = self.simulator.random_fault()
        self.add_alert(f"⚠️ SIMULATED FAULT: {name} - Code {code}")
        self.show_toast(f"⚠️ Fault simulated on {name}")
    
    def open_settings(self):
        settings = SettingsDialog(self)
        settings.exec()

# ==================== MAIN ====================
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Create splash screen
    splash = QSplashScreen()
    splash.setPixmap(QPixmap(400, 300))
    splash.show()
    splash.showMessage("Loading MCC Monitoring System...", Qt.AlignCenter, QColor(96, 165, 250))
    
    # Process events to show splash
    app.processEvents()
    
    # Create main window
    window = MonitoringDashboard()
    
    # Show splash for 2 seconds
    QTimer.singleShot(2000, splash.close)
    QTimer.singleShot(2000, window.show)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()