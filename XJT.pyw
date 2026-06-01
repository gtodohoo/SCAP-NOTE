import sys
import math
import traceback
import time
import os

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QButtonGroup, QLabel, QFrame, QTextEdit, 
                             QMessageBox, QSlider, QSpinBox, QFileDialog, QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QPainter, QPen, QColor, QImage, QPainterPath, QBrush, 
                         QRegion, QFont, QPixmap, QIcon, QPdfWriter, QTransform, QPainterPathStroker,
                         QPageLayout)
from PyQt5.QtCore import Qt, QPoint, QPointF, QRect, QEvent, QSize, QRectF, QTimer, QByteArray, QBuffer, QIODevice

def global_exception_handler(exctype, value, tb):
    for widget in QApplication.topLevelWidgets():
        try: 
            widget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            widget.hide()
        except: pass
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("App Crashed")
    msg.setText("The application crashed, but the invisible screen shield has been safely dropped.")
    msg.setDetailedText("".join(traceback.format_exception(exctype, value, tb)))
    msg.exec_()

sys.excepthook = global_exception_handler
if hasattr(Qt, 'AA_EnableHighDpiScaling'): 
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'): 
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

def _x(p): return p.x() if callable(getattr(p, 'x', None)) else p.x
def _y(p): return p.y() if callable(getattr(p, 'y', None)) else p.y

def point_to_seg_dist(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0: 
        return math.hypot(px - x1, py - y1)
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

def create_tool_icon(type):
    pm = QPixmap(64, 64)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    file_map = {"select":"select.png","pen":"pen.png","highlight":"highlighter.png","eraser":"eraser.png","arrow":"arrow01.png","flex_arrow":"arrow02.png","rect":"rectangular.png","circle":"circle.png","text":"text.png","exit":"exit.png"}
    png_filename = file_map.get(type, f"{type}.png")
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, png_filename)
        img = QPixmap(icon_path)
    except: 
        img = QPixmap(png_filename)
        
    if not img.isNull():
        scaled = img.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        p.drawPixmap(int((64-scaled.width())/2), int((64-scaled.height())/2), scaled)
        p.end()
        return QIcon(pm)
        
    color = QColor("#0038ff")
    p.setPen(QPen(color, 4.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    
    if type == "select": 
        path = QPainterPath(); path.moveTo(18, 14); path.lineTo(18, 46); path.lineTo(26, 38); path.lineTo(34, 52); path.lineTo(42, 48); path.lineTo(34, 34); path.lineTo(46, 34); path.closeSubpath(); p.drawPath(path)
    elif type == "pen": 
        p.translate(32, 32); p.rotate(45); p.translate(-32, -32); p.drawRoundedRect(22, 10, 16, 26, 6, 6); p.drawLine(22, 36, 30, 48); p.drawLine(38, 36, 30, 48); p.drawLine(22, 36, 38, 36); p.drawLine(42, 16, 42, 28); p.resetTransform()
    elif type == "highlight": 
        p.translate(32, 32); p.rotate(45); p.translate(-32, -32); p.drawRoundedRect(18, 12, 24, 24, 4, 4); p.drawLine(22, 36, 38, 36); p.drawLine(22, 36, 22, 42); p.drawLine(38, 36, 30, 50); p.drawLine(22, 42, 30, 50); p.resetTransform()
    elif type == "eraser": 
        p.translate(32, 24); p.rotate(45); p.translate(-32, -24); p.drawRoundedRect(16, 6, 28, 36, 6, 6); p.drawLine(16, 28, 44, 28); p.resetTransform(); p.drawLine(16, 52, 48, 52)
    elif type == "arrow": 
        p.drawLine(14, 32, 50, 32); p.drawLine(50, 32, 38, 20); p.drawLine(50, 32, 38, 44)
    elif type == "flex_arrow": 
        p.drawLine(14, 42, 32, 42); p.drawLine(32, 42, 48, 22); p.drawLine(48, 22, 36, 22); p.drawLine(48, 22, 48, 34); p.setPen(Qt.NoPen); p.setBrush(color); p.drawEllipse(QPointF(14, 42), 4, 4); p.drawEllipse(QPointF(32, 42), 4, 4)
    elif type == "rect": 
        p.setPen(QPen(color, 4.5, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)); p.drawRect(14, 20, 36, 24)
    elif type == "circle": 
        p.drawEllipse(14, 14, 36, 36)
    elif type == "text": 
        p.setPen(QPen(color, 3.0, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)); p.drawRect(16, 16, 32, 32); p.setPen(Qt.NoPen); p.setBrush(color); p.drawRect(12, 12, 8, 8); p.drawRect(44, 12, 8, 8); p.drawRect(12, 44, 8, 8); p.drawRect(44, 44, 8, 8); p.setPen(QPen(color, 4.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)); p.drawLine(26, 24, 38, 24); p.drawLine(32, 24, 32, 40); p.drawLine(28, 40, 36, 40); p.drawLine(26, 24, 26, 28); p.drawLine(38, 24, 38, 28)
    elif type == "exit": 
        p.drawLine(20, 20, 44, 44); p.drawLine(44, 20, 20, 44)
        
    p.end()
    return QIcon(pm)

def create_screencap_top_icon():
    pm = QPixmap(60, 26)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(140, 150, 170), 1.2))
    p.drawRoundedRect(1, 1, 58, 24, 5, 5)
    icon_color = QColor(60, 70, 90)
    p.setPen(QPen(icon_color, 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawRoundedRect(35, 7, 18, 13, 2, 2)
    p.fillRect(39, 5, 4, 3, icon_color)
    p.setBrush(QBrush(Qt.transparent))
    p.drawEllipse(41, 10, 6, 6)
    p.setPen(QPen(QColor(0, 120, 215)))
    p.setFont(QFont("Arial", 8, QFont.Bold))
    p.drawText(QRect(2, 1, 32, 24), Qt.AlignCenter, "CAP")
    p.end()
    return QIcon(pm)

def create_stroke_erase_icon():
    filename = "stroke erase.png"
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img = QPixmap(os.path.join(script_dir, filename))
    except: 
        img = QPixmap(filename)
    if not img.isNull():
        pm = QPixmap(32, 32)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        scaled_img = img.scaled(28, 28, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        p.drawPixmap(int((32-scaled_img.width())/2), int((32-scaled_img.height())/2), scaled_img)
        p.end()
        return QIcon(pm)
    pm = QPixmap(32,32)
    pm.fill(Qt.transparent)
    return QIcon(pm)

def create_clear_icon():
    filename = "Clear.png"
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img = QPixmap(os.path.join(script_dir, filename))
    except: 
        img = QPixmap(filename)
    if not img.isNull():
        pm = QPixmap(32, 32)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        scaled_img = img.scaled(26, 26, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        p.drawPixmap(int((32-scaled_img.width())/2), int((32-scaled_img.height())/2), scaled_img)
        p.end()
        return QIcon(pm)
    pm = QPixmap(32,32)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(100,100,100),1.5))
    p.drawLine(10,10,22,22)
    p.drawLine(22,10,10,22)
    p.end()
    return QIcon(pm)

def create_undo_icon_png():
    filename = "undo.png"
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img = QPixmap(os.path.join(script_dir, filename))
    except: 
        img = QPixmap(filename)
    if not img.isNull():
        pm = QPixmap(32, 32)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        scaled_img = img.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        p.drawPixmap(int((32-scaled_img.width())/2), int((32-scaled_img.height())/2), scaled_img)
        p.end()
        return QIcon(pm)
    pm = QPixmap(32,32)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(50,50,50),2.5,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
    path = QPainterPath(); path.moveTo(22,22); path.quadTo(10,22,10,12); path.quadTo(10,6,16,6)
    p.drawPath(path)
    p.end()
    return QIcon(pm)

def create_redo_icon_png():
    filename = "redo.png"
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img = QPixmap(os.path.join(script_dir, filename))
    except: 
        img = QPixmap(filename)
    if not img.isNull():
        pm = QPixmap(32, 32)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        scaled_img = img.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        p.drawPixmap(int((32-scaled_img.width())/2), int((32-scaled_img.height())/2), scaled_img)
        p.end()
        return QIcon(pm)
    pm = QPixmap(32,32)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(50,50,50),2.5,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
    path = QPainterPath(); path.moveTo(10,22); path.quadTo(22,22,22,12); path.quadTo(22,6,16,6)
    p.drawPath(path)
    p.end()
    return QIcon(pm)

def create_dot_icon(size): 
    pm=QPixmap(32,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(Qt.black); p.setPen(Qt.NoPen); p.drawEllipse(16-size//2,16-size//2,size,size); p.end(); return QIcon(pm)
def create_wave_icon(): 
    pm=QPixmap(64,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    pen=QPen(Qt.black,3); pen.setCapStyle(Qt.RoundCap); pen.setJoinStyle(Qt.RoundJoin); p.setPen(pen)
    path=QPainterPath(); path.moveTo(6,22); path.cubicTo(18,4,30,28,42,22); path.cubicTo(50,16,56,28,60,20); p.drawPath(path); p.end(); return QIcon(pm)
def create_plus_icon(): 
    pm=QPixmap(32,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(100,100,100),1.5)); p.drawLine(16,8,16,24); p.drawLine(8,16,24,16); p.end(); return QIcon(pm)
def create_minus_icon(): 
    pm=QPixmap(32,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(100,100,100),1.5)); p.drawLine(8,16,24,16); p.end(); return QIcon(pm)
def create_dots_icon(): 
    pm=QPixmap(32,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(100,100,100)); p.setPen(Qt.NoPen); p.drawEllipse(6,14,3,3); p.drawEllipse(14,14,3,3); p.drawEllipse(22,14,3,3); p.end(); return QIcon(pm)
def create_cross_icon(): 
    pm=QPixmap(32,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(100,100,100),1.5)); p.drawLine(10,10,22,22); p.drawLine(22,10,10,22); p.end(); return QIcon(pm)
def create_undo_icon(): 
    pm=QPixmap(32,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(50,50,50),2.5,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
    path=QPainterPath(); path.moveTo(22,22); path.quadTo(10,22,10,12); path.quadTo(10,6,16,6); p.drawPath(path); p.end(); return QIcon(pm)
def create_redo_icon(): 
    pm=QPixmap(32,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(50,50,50),2.5,Qt.SolidLine,Qt.RoundCap,Qt.RoundJoin))
    path=QPainterPath(); path.moveTo(10,22); path.quadTo(22,22,22,12); path.quadTo(22,6,16,6); p.drawPath(path); p.end(); return QIcon(pm)
def create_grid_icon(): 
    pm=QPixmap(32,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(100,100,100),1.5)); p.drawRect(6,6,20,20); p.drawLine(16,6,16,26); p.drawLine(6,16,26,16); p.end(); return QIcon(pm)
def create_insert_icon(): 
    pm=QPixmap(32,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(100,100,100),1.5)); p.drawRect(4,6,24,20); p.drawEllipse(10,10,4,4)
    path=QPainterPath(); path.moveTo(4,26); path.lineTo(12,16); path.lineTo(18,22); path.lineTo(22,18); path.lineTo(28,26); p.drawPath(path); p.end(); return QIcon(pm)
def create_folder_icon(): 
    pm=QPixmap(24,24); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(80,80,80),1.5))
    path=QPainterPath(); path.moveTo(2,20); path.lineTo(2,6); path.lineTo(8,6); path.lineTo(10,8); path.lineTo(22,8); path.lineTo(22,20); path.lineTo(2,20); p.drawPath(path); p.end(); return QIcon(pm)
def create_capture_icon(): 
    pm=QPixmap(24,24); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(80,80,80),1.5)); p.drawRect(6,6,12,12); p.drawLine(4,6,6,6); p.drawLine(18,18,20,18); p.drawLine(6,4,6,6); p.drawLine(18,18,18,20); p.end(); return QIcon(pm)
def create_export_icon(): 
    pm=QPixmap(24,24); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(80,80,80),1.5)); p.drawLine(12,14,12,4); p.drawLine(12,4,8,8); p.drawLine(12,4,16,8); p.drawLine(4,14,4,20); p.drawLine(4,20,20,20); p.drawLine(20,20,20,14); p.end(); return QIcon(pm)
def create_camera_icon(): 
    pm=QPixmap(32,32); pm.fill(Qt.transparent); p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor(80,80,80),1.5)); p.drawRect(4,10,24,16); p.drawRect(10,6,12,4); p.drawEllipse(11,13,10,10); p.drawEllipse(14,16,4,4); p.end(); return QIcon(pm)

def create_template_icon(template_type):
    pm=QPixmap(48,48)
    pm.fill(Qt.transparent)
    p=QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    
    if template_type in ["square", "dots", "rules", "none"]:
        p.setPen(QPen(QColor(120,120,120),1.5))
        p.drawEllipse(6,6,36,36)
        p.setClipRegion(QRegion(6,6,36,36,QRegion.Ellipse))
        p.setPen(QPen(QColor(170,170,170),1.5))
        
        if template_type == "rules": 
            p.setPen(QPen(QColor(140,190,220),1.5))
            for y in range(14,48,10): p.drawLine(0,y,48,y)
        elif template_type == "square": 
            for y in range(12,48,8): p.drawLine(0,y,48,y)
            for x in range(12,48,8): p.drawLine(x,0,x,48)
        elif template_type == "dots": 
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(170,170,170)))
            for y in range(12,48,10):
                for x in range(12,48,10): 
                    p.drawEllipse(x-1,y-1,3,3)
    else:
        p.setPen(QPen(QColor(120,120,120),1.5))
        if template_type == "a4_portrait": 
            p.drawRect(14,8,20,32)
            p.setPen(QPen(QColor(150,150,150),1.5,Qt.DashLine))
            p.drawLine(10,24,38,24)
        elif template_type == "a4_landscape": 
            p.drawRect(8,14,32,20)
            p.setPen(QPen(QColor(150,150,150),1.5,Qt.DashLine))
            p.drawLine(24,10,24,38)
        elif template_type == "infinite": 
            p.drawRect(14,8,20,32)
            p.drawLine(24,12,24,36)
            p.drawLine(24,12,20,16)
            p.drawLine(24,12,28,16)
            p.drawLine(24,36,20,32)
            p.drawLine(24,36,28,32)
            
    p.end()
    return QIcon(pm)

def qvariant_to_image(var): 
    return var if isinstance(var, QImage) else (var.toImage() if hasattr(var, 'toImage') else QImage())

class SnippingWidget(QWidget):
    def __init__(self, toolbar, note_box=None):
        super().__init__()
        self.toolbar = toolbar
        self.note_box = note_box
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setCursor(Qt.CrossCursor)
        
        screen = QApplication.primaryScreen()
        if screen: 
            self.desktop_pixmap = screen.grabWindow(0)
            self.setGeometry(screen.geometry())
        else: 
            self.desktop_pixmap = QPixmap()
            
        self.begin_pos = None
        self.end_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        if hasattr(self, 'desktop_pixmap') and not self.desktop_pixmap.isNull(): 
            painter.drawPixmap(0, 0, self.desktop_pixmap)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        if getattr(self, 'begin_pos', None) and getattr(self, 'end_pos', None):
            rect = QRect(self.begin_pos, self.end_pos).normalized()
            if hasattr(self, 'desktop_pixmap') and not self.desktop_pixmap.isNull(): 
                painter.drawPixmap(rect, self.desktop_pixmap, rect)
            painter.setPen(QPen(QColor(0, 120, 215), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: 
            self.begin_pos = event.pos()
            self.end_pos = self.begin_pos
            self.update()

    def mouseMoveEvent(self, event):
        if getattr(self, 'begin_pos', None): 
            self.end_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and getattr(self, 'begin_pos', None):
            rect = QRect(self.begin_pos, self.end_pos).normalized()
            if rect.width() > 5 and rect.height() > 5 and hasattr(self, 'desktop_pixmap') and not self.desktop_pixmap.isNull():
                cropped = self.desktop_pixmap.copy(rect)
                QApplication.clipboard().setPixmap(cropped)
                img = cropped.toImage()
                if getattr(self, 'note_box', None) and not img.isNull(): 
                    self.note_box.add_image_entity(img)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape: 
            self.close()

    def closeEvent(self, event):
        if hasattr(self, 'toolbar') and self.toolbar:
            for nb in self.toolbar.note_boxes: 
                nb.show()
        super().closeEvent(event)


class StrokeButton(QPushButton):
    def __init__(self, size_val, toolbar, parent=None):
        super().__init__(parent)
        self.size_val = size_val
        self.toolbar = toolbar
        self.setIcon(create_dot_icon(size_val))
        self.setIconSize(QSize(32,32))
        self.setFixedSize(32,32)
        self.setCheckable(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("QPushButton { border: none; border-radius: 16px; background: transparent; } QPushButton:checked { background-color: rgba(0,0,0,0.1); }")
        self.hold_timer = QTimer(self)
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self.show_slider)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: 
            self.hold_timer.start(500)
            self.toolbar.change_thickness(self.size_val)
            self.setChecked(True)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton: 
            self.hold_timer.stop()
        super().mouseReleaseEvent(event)

    def show_slider(self): 
        self.toolbar.show_stroke_slider(self)


class StrokeSliderPopup(QWidget):
    def __init__(self, toolbar):
        super().__init__(toolbar, Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        self.toolbar = toolbar
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet("QFrame { background: white; border-radius: 8px; border: none; }")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.main_frame.setGraphicsEffect(shadow)
        
        f_layout = QHBoxLayout(self.main_frame)
        f_layout.setContentsMargins(8,8,8,8)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1,50)
        self.slider.setValue(self.toolbar.base_size)
        self.slider.setFixedWidth(150)
        self.slider.setStyleSheet("QSlider::handle:horizontal { background: #55aaff; border-radius: 6px; width: 12px; } QSlider::groove:horizontal { background: #e0e0e0; height: 6px; border-radius: 3px; }")
        self.slider.valueChanged.connect(self.update_size)
        
        self.lbl_val = QLabel(f"{self.toolbar.base_size}px")
        self.lbl_val.setFixedWidth(35)
        self.lbl_val.setStyleSheet("font-weight: bold; color: #333;")
        
        f_layout.addWidget(self.slider)
        f_layout.addWidget(self.lbl_val)
        layout.addWidget(self.main_frame)

    def update_size(self, val):
        self.lbl_val.setText(f"{val}px")
        self.toolbar.base_size = val
        if not self.toolbar.use_pressure:
            checked_btn = self.toolbar.stroke_group.checkedButton()
            if checked_btn and hasattr(checked_btn, 'size_val'): 
                checked_btn.setIcon(create_dot_icon(val))


class InsertPopup(QWidget):
    def __init__(self, note_box):
        super().__init__(note_box, Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        self.note_box = note_box
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet("QFrame { background: white; border-radius: 8px; border: none; }")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.main_frame.setGraphicsEffect(shadow)
        
        f_layout = QVBoxLayout(self.main_frame)
        f_layout.setContentsMargins(4,4,4,4)
        f_layout.setSpacing(2)
        
        btn_style = "QPushButton { text-align: left; padding: 6px; font-weight: bold; color: #444; border: none; border-radius: 4px; background: transparent; } QPushButton:hover { background: rgba(0,120,215,0.1); color: #000; }"
        
        btn_file = QPushButton(" Load File")
        btn_file.setIcon(create_folder_icon())
        btn_file.setIconSize(QSize(18,18))
        btn_file.setStyleSheet(btn_style)
        btn_file.clicked.connect(self.load_file)
        
        btn_capture = QPushButton(" Screen Capture")
        btn_capture.setIcon(create_capture_icon())
        btn_capture.setIconSize(QSize(18,18))
        btn_capture.setStyleSheet(btn_style)
        btn_capture.clicked.connect(self.screen_capture)
        
        f_layout.addWidget(btn_file)
        f_layout.addWidget(btn_capture)
        layout.addWidget(self.main_frame)

    def load_file(self):
        self.hide()
        file_path, _ = QFileDialog.getOpenFileName(self.note_box, "Insert Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            img = QImage(file_path)
            if not img.isNull(): 
                self.note_box.add_image_entity(img)
        self.deleteLater()

    def screen_capture(self):
        self.hide()
        toolbar = self.note_box.toolbar
        for nb in toolbar.note_boxes: 
            nb.hide()
        QApplication.processEvents()
        time.sleep(0.15)
        try: 
            toolbar.snipping_widget = SnippingWidget(toolbar, self.note_box)
            toolbar.snipping_widget.showFullScreen()
        except Exception as e:
            for nb in toolbar.note_boxes: 
                nb.show()
            print("Capture Error:", e)
        self.deleteLater()


class TemplatePopup(QWidget):
    def __init__(self, note_box):
        super().__init__(note_box, Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        self.note_box = note_box
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet("QFrame { background: white; border-radius: 8px; border: none; }")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.main_frame.setGraphicsEffect(shadow)
        
        f_layout = QVBoxLayout(self.main_frame)
        f_layout.setContentsMargins(6,6,6,6)
        
        row1 = QHBoxLayout()
        for t_type in ["square", "dots", "rules", "none"]:
            btn = QPushButton()
            btn.setIcon(create_template_icon(t_type))
            btn.setIconSize(QSize(40,40))
            btn.setFixedSize(48,48)
            btn.setFocusPolicy(Qt.NoFocus)
            bg = "rgba(0,120,215,0.1)" if self.note_box.bg_pattern == t_type else "transparent"
            border = "border: 2px solid #55aaff;" if self.note_box.bg_pattern == t_type else "border: 1px solid transparent;"
            btn.setStyleSheet(f"QPushButton {{ background: {bg}; border-radius: 8px; {border} }} QPushButton:hover {{ background: rgba(0,0,0,0.05); border: 1px solid #ccc; }}")
            btn.clicked.connect(lambda checked, t=t_type: self.select_pattern(t))
            row1.addWidget(btn)
            
        f_layout.addLayout(row1)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #ddd;")
        f_layout.addWidget(sep)
        
        row2 = QHBoxLayout()
        for s_type in ["infinite", "a4_portrait", "a4_landscape"]:
            btn = QPushButton()
            btn.setIcon(create_template_icon(s_type))
            btn.setIconSize(QSize(40,40))
            btn.setFixedSize(48,48)
            btn.setFocusPolicy(Qt.NoFocus)
            bg = "rgba(0,120,215,0.1)" if self.note_box.bg_size == s_type else "transparent"
            border = "border: 2px solid #55aaff;" if self.note_box.bg_size == s_type else "border: 1px solid transparent;"
            btn.setStyleSheet(f"QPushButton {{ background: {bg}; border-radius: 8px; {border} }} QPushButton:hover {{ background: rgba(0,0,0,0.05); border: 1px solid #ccc; }}")
            btn.clicked.connect(lambda checked, s=s_type: self.select_size(s))
            row2.addWidget(btn)
            
        row2.addStretch()
        f_layout.addLayout(row2)
        layout.addWidget(self.main_frame)

    def select_pattern(self, p_type): 
        self.note_box.bg_pattern = p_type
        self.note_box.update()
        self.close()
        
    def select_size(self, s_type): 
        self.note_box.bg_size = s_type
        self.note_box.update()
        self.close()


class ColorPopup(QWidget):
    def __init__(self, note_box):
        super().__init__(note_box, Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        self.note_box = note_box
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet("QFrame { background: white; border-radius: 6px; border: none; }")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.main_frame.setGraphicsEffect(shadow)
        
        f_layout = QHBoxLayout(self.main_frame)
        f_layout.setContentsMargins(2,2,2,2)
        
        for color_pair in self.note_box.bg_colors:
            btn = QPushButton()
            btn.setFixedSize(36,36)
            if color_pair == self.note_box.current_bg_color: 
                btn.setText("✓")
            btn.setStyleSheet(f"QPushButton {{ background-color: {color_pair[0]}; border: none; color: #333; font-size: 16px; }} QPushButton:hover {{ opacity: 0.8; }}")
            btn.clicked.connect(lambda checked, c=color_pair: self.select_color(c))
            f_layout.addWidget(btn)
            
        layout.addWidget(self.main_frame)

    def select_color(self, color_pair): 
        self.note_box.set_bg_color(color_pair)
        self.close()


class SmartTextBox(QTextEdit):
    def __init__(self, parent, toolbar, font_size, color, is_bold=False):
        super().__init__(parent)
        self.toolbar = toolbar
        self.setViewportMargins(0,0,0,0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        
        font = QFont("Arial", font_size)
        if is_bold: 
            font.setBold(True)
        self.setFont(font)
        self.setTextColor(color)
        self.setStyleSheet("QTextEdit { background: transparent; border: none; }")
        
        self.btn_delete = QPushButton("×", self)
        self.btn_delete.setFixedSize(16,16)
        self.btn_delete.setFocusPolicy(Qt.NoFocus)
        self.btn_delete.setStyleSheet("QPushButton { background: #ffcccc; color: darkred; border-radius: 8px; font-weight: bold; border: none; } QPushButton:hover { background: red; color: white; }")
        self.btn_delete.clicked.connect(self.delete_self)
        self.btn_delete.hide()
        
        self.textChanged.connect(self.fit_content)
        self.cursorPositionChanged.connect(self.sync_toolbar)

    def wheelEvent(self, e): 
        e.ignore()

    def sync_toolbar(self):
        try:
            fmt = self.currentCharFormat()
            self.toolbar.btn_bold.setChecked(fmt.fontWeight() == QFont.Bold)
            size = fmt.fontPointSize()
            if size > 0: 
                self.toolbar.size_spinbox.blockSignals(True)
                self.toolbar.size_spinbox.setValue(int(size))
                self.toolbar.size_spinbox.blockSignals(False)
        except: 
            pass

    def fit_content(self): 
        doc = self.document()
        doc.setTextWidth(self.width())
        ideal_height = int(doc.size().height()) + 10
        if self.height() < ideal_height: 
            self.resize(self.width(), ideal_height)

    def resizeEvent(self, e): 
        super().resizeEvent(e)
        self.fit_content()
        self.btn_delete.move(self.width()-16, 0)

    def focusOutEvent(self, e): 
        super().focusOutEvent(e)
        self.btn_delete.hide()
        QTimer.singleShot(0, self.commit_self)

    def commit_self(self):
        if not self.parent(): return
        text = self.toPlainText().strip()
        p = self.parent()
        if text:
            if hasattr(p, 'commit_text'): 
                p.commit_text(self)
        else: 
            self.delete_self()

    def delete_self(self):
        if getattr(self.toolbar, 'active_text_box', None) == self: 
            self.toolbar.active_text_box = None
        p = self.parent()
        if hasattr(p, 'text_boxes') and self in p.text_boxes: 
            p.text_boxes.remove(self)
        self.setParent(None)
        self.deleteLater()
        if p: p.update()

    def focusInEvent(self, e): 
        super().focusInEvent(e)
        self.toolbar.active_text_box = self
        self.setStyleSheet("QTextEdit { background: transparent; border: 1px dashed #888; }")
        self.btn_delete.show()
        self.sync_toolbar()


class FloatingNoteBox(QFrame):
    def __init__(self, toolbar):
        super().__init__()
        self.toolbar = toolbar
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TabletTracking)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        
        self.scroll_x = 0
        self.scroll_y = 0
        self.max_scroll_x = 10000
        self.max_scroll_y = 10000
        self.m_panning = False
        self.pan_start_pos = QPoint()
        
        self.undo_stack = []
        self.redo_stack = []
        self.strokes = []
        self.text_boxes = []
        self.selected_strokes = []
        self.stroke_start_positions = {}
        
        self.captured_pages = []
        self.is_tablet = False
        self.action = ""
        self.drag_start_pos = QPointF()
        self.drag_start_global = QPoint()
        self.temp_text_rect = QRect()
        self.start_geometry = QRect()
        self.last_pos = QPointF()
        self.current_pressure = 1.0
        self.last_pressure = 1.0
        self.shape_start = QPointF()
        self.shape_end = QPointF()
        self.shape_ctrl = QPointF()
        self.current_stroke_points = []
        self.draw_state = 0
        
        self.bg_pattern = "none"
        self.bg_size = "infinite"
        self.bg_colors = [("#fcfcfc","#ffffff"), ("#e6e6e6","#f4f4f4"), ("#faeca3","#fef6ca"), ("#ffacd6","#ffcce5"), ("#cbb3f5","#e2d6fb"), ("#93d9f8","#c4ecfb")]
        self.current_bg_color = self.bg_colors[0]
        self.note_bg_alpha = 255
        self.is_minimized = False
        
        self.init_ui()
        self.setGeometry(100, 100, 400, 500)

    def create_btn(self, parent, icon, callback):
        btn = QPushButton(parent)
        btn.setIcon(icon)
        btn.setFixedSize(26, 26)
        btn.setFocusPolicy(Qt.NoFocus)
        btn.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background: rgba(0,0,0,0.1); border-radius: 4px; }")
        btn.clicked.connect(callback)
        return btn

    def init_ui(self):
        self.header = QFrame(self)
        self.header.setObjectName("HeaderFrame")
        self.header.setStyleSheet("background: transparent; border: none;")
        self.header.setMouseTracking(True)
        self.header.installEventFilter(self)
        
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 0, 10, 0)
        
        self.btn_add = self.create_btn(self.header, create_plus_icon(), self.toolbar.add_note_box)
        self.btn_minimize = self.create_btn(self.header, create_minus_icon(), self.toggle_minimize)
        
        self.btn_top_screencap = QPushButton("", self.header)
        self.btn_top_screencap.setFixedSize(60, 26)
        self.btn_top_screencap.setFocusPolicy(Qt.NoFocus)
        self.btn_top_screencap.setIcon(create_screencap_top_icon())
        self.btn_top_screencap.setIconSize(QSize(60, 26))
        self.btn_top_screencap.setStyleSheet("QPushButton { background: transparent; border: none; padding: 0px; margin: 0px; }")
        self.btn_top_screencap.clicked.connect(self.snapshot_action)
        self.btn_top_screencap.setToolTip("Capture Page & Clear (Screen Capture)")
        
        self.opacity_slider = QSlider(Qt.Horizontal, self.header)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setFixedWidth(80)
        self.opacity_slider.setStyleSheet("QSlider::handle:horizontal { background: #55aaff; border-radius: 6px; width: 12px; } QSlider::groove:horizontal { background: #ccc; height: 6px; border-radius: 3px; }")
        self.opacity_slider.valueChanged.connect(self.change_note_opacity)
        
        self.btn_insert = self.create_btn(self.header, create_insert_icon(), self.open_insert_menu)
        self.btn_template = self.create_btn(self.header, create_grid_icon(), self.open_template_menu)
        self.btn_menu = self.create_btn(self.header, create_dots_icon(), self.open_color_menu)
        self.btn_close = self.create_btn(self.header, create_cross_icon(), lambda: self.toolbar.remove_note_box(self))
        
        header_layout.addWidget(self.btn_add)
        header_layout.addWidget(self.btn_minimize)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_top_screencap)
        header_layout.addWidget(self.opacity_slider)
        header_layout.addWidget(self.btn_insert)
        header_layout.addWidget(self.btn_template)
        header_layout.addWidget(self.btn_menu)
        header_layout.addWidget(self.btn_close)
        
        self.footer = QFrame(self)
        self.footer.setObjectName("FooterFrame")
        self.footer.setStyleSheet("background: transparent; border: none;")
        self.footer.setMouseTracking(True)
        self.footer.installEventFilter(self)
        
        footer_layout = QHBoxLayout(self.footer)
        footer_layout.setContentsMargins(10, 0, 10, 0)
        
        self.lbl_page_count = QLabel("Pages: 0", self.footer)
        self.lbl_page_count.setStyleSheet("color: #666; font-weight: bold; margin-right: 10px;")
        
        self.btn_export = self.create_btn(self.footer, create_export_icon(), self.export_action)
        self.btn_export.setToolTip("Export All Pages to PDF")
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.lbl_page_count)
        footer_layout.addWidget(self.btn_export)

    def get_desktop_pixmap_without_ui(self):
        self.hide()
        if self.toolbar: 
            self.toolbar.hide()
        
        end_time = time.time() + 0.3
        while time.time() < end_time: 
            QApplication.processEvents()
            time.sleep(0.02)
            
        screen = QApplication.primaryScreen()
        global_pos = self.mapToGlobal(QPoint(0, 0))
        pix = screen.grabWindow(0, global_pos.x(), global_pos.y(), self.width(), self.height())
        
        self.show()
        if self.toolbar: 
            self.toolbar.show()
        QApplication.processEvents()
        
        return pix

    def snapshot_action(self):
        if self.text_boxes:
            for tb in list(self.text_boxes): 
                if hasattr(tb, 'commit_self'): 
                    tb.commit_self()
                    
        raw_pixmap = self.get_desktop_pixmap_without_ui()
        final_image = QImage(self.width(), self.height(), QImage.Format_ARGB32_Premultiplied)
        final_image.fill(Qt.transparent)
        
        painter = QPainter(final_image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not raw_pixmap.isNull(): 
            painter.drawPixmap(0, 0, raw_pixmap)
            
        alpha = int((self.opacity_slider.value() / 100.0) * 255)
        bg_c = QColor(self.current_bg_color[1])
        bg_c.setAlpha(alpha)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width()-1, self.height()-1, 12, 12)
        painter.fillPath(path, bg_c)
        painter.setClipPath(path)
        
        h_height = self.header.height() if self.header else 0
        f_height = self.footer.height() if self.footer else 0
        painter.setClipRect(QRect(0, h_height, self.width(), self.height()-h_height-f_height))
        painter.translate(-self.scroll_x, -self.scroll_y)
        
        self.draw_template(painter, self.scroll_x, self.scroll_y, self.scroll_x + self.width(), self.scroll_y + self.height(), self.scroll_y)
        self.render_content(painter, 0, is_export=True)
        painter.end()
        
        self.captured_pages.append(QPixmap.fromImage(final_image))
        self.lbl_page_count.setText(f"Pages: {len(self.captured_pages)}")
        self.show_toast(f"Page {len(self.captured_pages)} Captured!")
        QApplication.beep()

    def show_toast(self, msg):
        lbl = QLabel(msg, self)
        lbl.setStyleSheet("background: rgba(0,120,215,0.9); color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold; font-size: 16px;")
        lbl.adjustSize()
        lbl.move(self.width()//2 - lbl.width()//2, self.height()//2 - lbl.height()//2)
        lbl.show()
        QTimer.singleShot(1500, lbl.deleteLater)

    def toggle_minimize(self):
        if not self.is_minimized: 
            self.normal_geometry = self.geometry()
            self.is_minimized = True
            self.footer.hide()
            for tb in self.text_boxes: 
                tb.hide()
            self.resize(self.width(), self.header.height())
        else: 
            self.is_minimized = False
            self.setGeometry(self.normal_geometry)
            self.footer.show()
            for tb in self.text_boxes: 
                tb.show()
        self.update()

    def open_insert_menu(self): 
        self.insert_popup = InsertPopup(self)
        self.insert_popup.move(self.btn_insert.mapToGlobal(QPoint(self.btn_insert.width()//2-60, self.btn_insert.height()+5)))
        self.insert_popup.show()
        
    def open_template_menu(self): 
        self.template_popup = TemplatePopup(self)
        self.template_popup.move(self.btn_template.mapToGlobal(QPoint(self.btn_template.width()//2-120, self.btn_template.height()+5)))
        self.template_popup.show()
        
    def open_color_menu(self): 
        self.color_popup = ColorPopup(self)
        self.color_popup.move(self.btn_menu.mapToGlobal(QPoint(0, self.btn_menu.height())))
        self.color_popup.show()
        
    def change_note_opacity(self, val): 
        alpha = int((val / 100.0) * 255)
        self.note_bg_alpha = max(1, alpha)
        self.update()
        
    def set_bg_color(self, color_pair): 
        self.current_bg_color = color_pair
        self.update()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonDblClick and obj == self.header:
            if event.button() == Qt.LeftButton: 
                self.toggle_minimize()
                return True
        if event.type() == QEvent.MouseMove and event.buttons() == Qt.NoButton:
            if obj == self.header or obj == self.footer:
                d = self.get_resize_dir(obj.mapTo(self, event.pos()))
                if d in ["bottomright", "topleft"]: obj.setCursor(Qt.SizeFDiagCursor)
                elif d in ["bottomleft", "topright"]: obj.setCursor(Qt.SizeBDiagCursor)
                elif d in ["left", "right"]: obj.setCursor(Qt.SizeHorCursor)
                elif d in ["top", "bottom"]: obj.setCursor(Qt.SizeVerCursor)
                else: obj.setCursor(Qt.ArrowCursor)
        return super().eventFilter(obj, event)

    def resizeEvent(self, event): 
        super().resizeEvent(event)
        self.header.setGeometry(0, 0, self.width(), 34)
        self.footer.setGeometry(0, self.height()-34, self.width(), 34)

    def wheelEvent(self, event):
        if self.is_minimized: return
        dy = event.angleDelta().y() // 2
        if dy == 0: return
        if self.bg_size == "a4_landscape":
            new_x = max(0, min(self.scroll_x - dy, self.max_scroll_x))
            actual_dx = new_x - self.scroll_x
            if actual_dx == 0: return
            self.scroll_x = new_x
            for box in self.text_boxes: 
                box.move(box.x() - actual_dx, box.y())
        else:
            new_y = max(0, min(self.scroll_y - dy, self.max_scroll_y))
            actual_dy = new_y - self.scroll_y
            if actual_dy == 0: return
            self.scroll_y = new_y
            for box in self.text_boxes: 
                box.move(box.x(), box.y() - actual_dy)
        self.header.raise_()
        self.footer.raise_()
        self.update()

    def get_resize_dir(self, pos):
        if self.is_minimized: return ""
        x, y = _x(pos), _y(pos)
        w, h = self.width(), self.height()
        m = 12
        res = ""
        if y < m: res += "top"
        elif y > h - m: res += "bottom"
        if x < m: res += "left"
        elif x > w - m: res += "right"
        return res

    def add_image_entity(self, img, pos=None):
        if img.isNull(): return None
        max_w = self.width() * 0.8
        max_h = self.height() * 0.8
        s = min(1.0, max_w / img.width() if img.width() > 0 else 1.0, max_h / img.height() if img.height() > 0 else 1.0)
        w = img.width() * s
        h = img.height() * s
        if pos: 
            cx, cy = _x(pos), _y(pos)
        else: 
            header_h = self.header.height() if self.header else 0
            cx = self.width() / 2 + self.scroll_x
            cy = self.height() / 2 + self.scroll_y + header_h / 2
            
        r = QRectF(cx - w/2, cy - h/2, w, h)
        st = {'type': 'image', 'img': img, 'rect': r, 'angle': 0.0}
        self.strokes.append(st)
        
        if self.toolbar.current_tool == "select": 
            self.stamp_selection()
            self.selected_strokes = [st]
        self.update()
        return st

    def stamp_selection(self):
        for tb in list(self.text_boxes):
            if hasattr(tb, 'commit_self'): 
                tb.commit_self()
        self.selected_strokes.clear()
        self.update()

    def clone_stroke(self, s):
        ns = {}
        for k, v in s.items():
            if k == 'path': ns[k] = QPainterPath(v)
            elif k in ['p1', 'p2', 'p_ctrl']: ns[k] = QPointF(_x(v), _y(v))
            elif k == 'rect': ns[k] = QRectF(v)
            elif k == 'points': ns[k] = [(QPointF(_x(pt), _y(pt)), pr) for pt, pr in v]
            elif k == 'img': ns[k] = v.copy() if hasattr(v, 'copy') else v
            else: ns[k] = v
        return ns

    def commit_text(self, editor):
        if editor not in self.text_boxes: return
        self.text_boxes.remove(editor)
        text = editor.toPlainText().strip()
        if text:
            r = QRectF(editor.geometry()).translated(self.scroll_x, self.scroll_y)
            st = {'type': 'text', 'text': text, 'rect': r, 'color': editor.textColor(), 'font_size': int(editor.font().pointSize()), 'is_bold': editor.font().bold(), 'angle': 0.0}
            self.strokes.append(st)
            self.selected_strokes = [st]
        editor.deleteLater()
        if getattr(self.toolbar, 'active_text_box', None) == editor: 
            self.toolbar.active_text_box = None
        self.update()

    def save_state(self):
        if len(self.undo_stack) > 15: self.undo_stack.pop(0)
        self.undo_stack.append([self.clone_stroke(s) for s in self.strokes])
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack: 
            self.redo_stack.append([self.clone_stroke(s) for s in self.strokes])
            self.strokes = [self.clone_stroke(s) for s in self.undo_stack.pop()]
            self.selected_strokes.clear()
            self.update()

    def redo(self):
        if self.redo_stack: 
            self.undo_stack.append([self.clone_stroke(s) for s in self.strokes])
            self.strokes = [self.clone_stroke(s) for s in self.redo_stack.pop()]
            self.selected_strokes.clear()
            self.update()

    def clear_canvas(self):
        self.save_state()
        self.strokes = []
        for tb in list(self.text_boxes):
            if getattr(self.toolbar, 'active_text_box', None) == tb: 
                self.toolbar.active_text_box = None
            tb.setParent(None)
            tb.deleteLater()
        self.text_boxes.clear()
        self.selected_strokes.clear()
        self.update()

    def get_local_coords(self, r, angle, pos):
        cx, cy = r.center().x(), r.center().y()
        px = _x(pos) - cx
        py = _y(pos) - cy
        rad = math.radians(-angle)
        lx = px * math.cos(rad) - py * math.sin(rad)
        ly = px * math.sin(rad) + py * math.cos(rad)
        return QPointF(lx + cx, ly + cy)

    def erase_at(self, pos):
        hit_stroke = None
        for stroke in reversed(self.strokes):
            r = stroke['rect']
            angle = stroke.get('angle', 0.0)
            local_pos = self.get_local_coords(r, angle, pos)
            
            if not r.adjusted(-25,-25,25,25).contains(local_pos): continue
            if stroke['type'] == 'image': continue 
            
            if stroke['type'] in ['pen', 'highlight']:
                pts = stroke.get('points', [])
                if not pts: continue
                p = QPainterPath()
                p.moveTo(pts[0][0])
                for pt, pr in pts[1:]: p.lineTo(pt)
                strk = QPainterPathStroker()
                strk.setWidth(max(15, stroke.get('base_size', 4) * 2))
                if strk.createStroke(p).contains(local_pos): 
                    hit_stroke = stroke
                    break
            elif stroke['type'] == 'flex_arrow':
                t = max(15, stroke['thickness'] + 10)
                if point_to_seg_dist(_x(local_pos), _y(local_pos), _x(stroke['p1']), _y(stroke['p1']), _x(stroke['p_ctrl']), _y(stroke['p_ctrl'])) <= t or point_to_seg_dist(_x(local_pos), _y(local_pos), _x(stroke['p_ctrl']), _y(stroke['p_ctrl']), _x(stroke['p2']), _y(stroke['p2'])) <= t: 
                    hit_stroke = stroke
                    break
            elif stroke['type'] == 'text':
                if stroke['rect'].contains(local_pos): 
                    hit_stroke = stroke
                    break
            else:
                p = QPainterPath()
                if stroke['type'] == 'rect': 
                    p.addRect(QRectF(stroke['p1'], stroke['p2']).normalized())
                elif stroke['type'] == 'circle': 
                    pad = stroke.get('thickness', 1.0) + 1
                    p.addEllipse(stroke['rect'].adjusted(pad, pad, -pad, -pad).normalized())
                elif stroke['type'] == 'arrow': 
                    p.moveTo(stroke['p1'])
                    p.lineTo(stroke['p2'])
                strk = QPainterPathStroker()
                strk.setWidth(max(15, stroke['thickness'] + 10))
                if strk.createStroke(p).contains(local_pos): 
                    hit_stroke = stroke
                    break
                    
        if hit_stroke: 
            self.strokes.remove(hit_stroke)
            self.update()

    def hit_test_all(self, pos):
        for stroke in reversed(self.strokes):
            r = stroke['rect']
            angle = stroke.get('angle', 0.0)
            local_pos = self.get_local_coords(r, angle, pos)
            
            if not r.adjusted(-25,-25,25,25).contains(local_pos): continue
            
            if stroke['type'] == 'image':
                lx = _x(local_pos) - r.x()
                ly = _y(local_pos) - r.y()
                ix = int(lx * stroke['img'].width() / r.width())
                iy = int(ly * stroke['img'].height() / r.height())
                if 0 <= ix < stroke['img'].width() and 0 <= iy < stroke['img'].height() and stroke['img'].pixelColor(ix, iy).alpha() > 10: 
                    return stroke, "stroke"
                continue
                
            if stroke['type'] in ['pen', 'highlight']:
                pts = stroke.get('points', [])
                if not pts: continue
                p = QPainterPath()
                p.moveTo(pts[0][0])
                for pt, pr in pts[1:]: p.lineTo(pt)
                strk = QPainterPathStroker()
                strk.setWidth(max(15, stroke.get('base_size', 4) * 2))
                if strk.createStroke(p).contains(local_pos): return stroke, "stroke"
            elif stroke['type'] == 'flex_arrow':
                t = max(15, stroke['thickness'] + 10)
                if point_to_seg_dist(_x(local_pos), _y(local_pos), _x(stroke['p1']), _y(stroke['p1']), _x(stroke['p_ctrl']), _y(stroke['p_ctrl'])) <= t or point_to_seg_dist(_x(local_pos), _y(local_pos), _x(stroke['p_ctrl']), _y(stroke['p_ctrl']), _x(stroke['p2']), _y(stroke['p2'])) <= t: 
                    return stroke, "stroke"
            elif stroke['type'] == 'text':
                if stroke['rect'].contains(local_pos): return stroke, "stroke"
            else:
                p = QPainterPath()
                if stroke['type'] == 'rect': 
                    p.addRect(QRectF(stroke['p1'], stroke['p2']).normalized())
                elif stroke['type'] == 'circle': 
                    pad = stroke.get('thickness', 1.0) + 1
                    p.addEllipse(stroke['rect'].adjusted(pad, pad, -pad, -pad).normalized())
                elif stroke['type'] == 'arrow': 
                    p.moveTo(stroke['p1']); p.lineTo(stroke['p2'])
                strk = QPainterPathStroker()
                strk.setWidth(max(15, stroke['thickness'] + 10))
                if strk.createStroke(p).contains(local_pos): return stroke, "stroke"
        return None, None

    def hit_test_handles(self, pos):
        hw = 16
        pos = QPointF(pos)
        for st in self.selected_strokes:
            r = st['rect']
            angle = st.get('angle', 0.0)
            local_pos = self.get_local_coords(r, angle, pos)
            
            if st['type'] == 'flex_arrow':
                if QRectF(st['p_ctrl'].x()-hw/2, st['p_ctrl'].y()-hw/2, hw, hw).contains(local_pos): 
                    return st, "resize_pc"
                    
            handles = [('tl',r.topLeft()), ('tc',QPointF(r.center().x(), r.top())), ('tr',r.topRight()), ('ml',QPointF(r.left(), r.center().y())), ('mr',QPointF(r.right(), r.center().y())), ('bl',r.bottomLeft()), ('bc',QPointF(r.center().x(), r.bottom())), ('br',r.bottomRight()), ('ro',QPointF(r.center().x(), r.top() - 25))]
            for h_name, h_pos in handles:
                if QRectF(h_pos.x()-hw/2, h_pos.y()-hw/2, hw, hw).contains(local_pos): 
                    return st, "resize_"+h_name
        return None, None

    def get_local_pos(self, global_pos): 
        l = self.mapFromGlobal(global_pos)
        return QPointF(_x(l) + self.scroll_x, _y(l) + self.scroll_y)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.action == "draw_click": 
                self.action = ""
                self.draw_state = 0
                self.update()
                event.accept()
                return
                
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ControlModifier:
            if event.key() == Qt.Key_C:
                if self.selected_strokes: 
                    self.toolbar.clipboard = [self.clone_stroke(s) for s in self.selected_strokes]
                event.accept()
                return
            elif event.key() == Qt.Key_V:
                mime_data = QApplication.clipboard().mimeData()
                if mime_data.hasImage():
                    img = qvariant_to_image(mime_data.imageData())
                    if img and not img.isNull(): self.add_image_entity(img)
                    event.accept()
                    return
                if hasattr(self.toolbar, 'clipboard') and self.toolbar.clipboard:
                    self.stamp_selection()
                    self.save_state()
                    new_sel = []
                    for s in self.toolbar.clipboard:
                        ns = self.clone_stroke(s)
                        if ns['type'] in ['pen', 'highlight']: 
                            ns['points'] = [(p + QPointF(20,20), pr) for p,pr in ns['points']]
                        elif ns['type'] == 'flex_arrow': 
                            ns['p1'] += QPointF(20,20); ns['p2'] += QPointF(20,20); ns['p_ctrl'] += QPointF(20,20)
                        elif ns['type'] in ['arrow', 'rect', 'circle']: 
                            ns['p1'] += QPointF(20,20); ns['p2'] += QPointF(20,20)
                        ns['rect'].translate(20, 20)
                        self.strokes.append(ns)
                        new_sel.append(ns)
                    self.selected_strokes = new_sel
                    self.update()
                event.accept()
                return
                
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            deleted = False
            if self.selected_strokes: 
                self.save_state()
                deleted = True
                for st in self.selected_strokes:
                    if st in self.strokes: self.strokes.remove(st)
                self.selected_strokes.clear()
                self.update()
            if deleted: 
                event.accept()
                return
        super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = self.get_local_pos(event.globalPos())
            hit_obj, htype = self.hit_test_all(pos)
            if hit_obj and hit_obj.get('type') == 'text':
                self.strokes.remove(hit_obj)
                if hit_obj in self.selected_strokes: 
                    self.selected_strokes.remove(hit_obj)
                    
                tb = SmartTextBox(self, self.toolbar, hit_obj['font_size'], hit_obj['color'], hit_obj['is_bold'])
                r = hit_obj['rect'].translated(-self.scroll_x, -self.scroll_y)
                tb.setGeometry(r.toRect())
                
                font = QFont("Arial", hit_obj['font_size'])
                font.setBold(hit_obj['is_bold'])
                tb.setFont(font)
                tb.setTextColor(hit_obj['color'])
                tb.setText(hit_obj['text'])
                tb.show()
                tb.raise_()
                tb.setFocus()
                
                self.text_boxes.append(tb)
                self.toolbar.active_text_box = tb
                
                self.toolbar.size_spinbox.blockSignals(True)
                self.toolbar.size_spinbox.setValue(hit_obj['font_size'])
                self.toolbar.size_spinbox.blockSignals(False)
                self.toolbar.btn_bold.setChecked(hit_obj['is_bold'])
                
                self.update()
                return
        super().mouseDoubleClickEvent(event)

    def tabletEvent(self, event):
        self.last_tablet_time = time.time()
        self.is_tablet = True
        self.last_pressure = getattr(self, 'current_pressure', 1.0)
        self.current_pressure = event.pressure()
        event.accept()
        pos = self.get_local_pos(event.globalPos())
        if event.type() == QEvent.TabletPress: 
            self.process_press(pos, event.globalPos())
        elif event.type() == QEvent.TabletRelease: 
            self.process_release(pos, event.globalPos())
        elif event.type() == QEvent.TabletMove: 
            self.process_move(pos, event.globalPos())

    def mousePressEvent(self, event):
        self.setFocus()
        self.toolbar.raise_()
        self.toolbar.active_note_box = None
        self.toolbar.hide_stroke_slider()
        self.is_tablet = False
        
        if event.button() == Qt.MiddleButton:
            self.m_panning = True
            self.pan_start_pos = event.globalPos()
            self.pan_start_scroll_x = self.scroll_x
            self.pan_start_scroll_y = self.scroll_y
            self.setCursor(Qt.ClosedHandCursor)
            return
            
        if event.button() == Qt.LeftButton:
            global_pos = event.globalPos()
            local_pos = self.mapFromGlobal(global_pos)
            canvas_pos = self.get_local_pos(global_pos)
            d = self.get_resize_dir(local_pos)
            in_header = self.header.geometry().contains(local_pos) if self.header else False
            in_footer = self.footer.geometry().contains(local_pos) if self.footer else False
            
            if d: 
                self.action = "resize_win_" + d
                self.drag_start_global = global_pos
                self.start_geometry = self.geometry()
                return
            elif in_header or (in_footer and not self.is_minimized) or self.is_minimized: 
                self.stamp_selection()
                self.action = "drag_win"
                self.drag_start_global = global_pos
                self.start_geometry = self.geometry()
                return
                
            self.process_press(canvas_pos, global_pos)

    def process_press(self, pos, global_pos):
        modifiers = QApplication.keyboardModifiers()
        is_shift = bool(modifiers & Qt.ShiftModifier)
        
        if self.toolbar.current_tool == "eraser": 
            self.save_state()
            self.action = "erase"
            self.erase_at(pos)
            self.update()
            return
            
        if self.toolbar.current_tool in ["select", "text"]:
            hit_st, handle = self.hit_test_handles(pos)
            if self.toolbar.current_tool == "text" and hit_st and hit_st.get('type') != 'text': 
                hit_st = None
                
            if hit_st: 
                self.action = handle
                self.drag_start_pos = pos
                self.stroke_start_positions = {id(s): self.clone_stroke(s) for s in self.selected_strokes}
                return
                
            hit_obj, htype = self.hit_test_all(pos)
            if self.toolbar.current_tool == "text" and hit_obj and hit_obj.get('type') != 'text': 
                hit_obj = None
                
            if hit_obj:
                if is_shift:
                    if hit_obj in self.selected_strokes: 
                        self.selected_strokes.remove(hit_obj)
                    else: 
                        self.selected_strokes.append(hit_obj)
                else:
                    if hit_obj not in self.selected_strokes: 
                        self.stamp_selection()
                        self.selected_strokes = [hit_obj]
                        
                self.action = "drag_st"
                self.drag_start_pos = pos
                self.stroke_start_positions = {id(s): self.clone_stroke(s) for s in self.selected_strokes}
                self.update()
                return
                
            if self.toolbar.current_tool == "text": 
                self.stamp_selection()
                self.action = "draw_text"
                self.drag_start_pos = pos
                self.temp_text_rect = QRect(pos.toPoint(), pos.toPoint())
                self.update()
                return
                
        if not is_shift: 
            self.stamp_selection()
            
        if self.toolbar.current_tool == "arrow":
            if self.draw_state == 0: 
                self.save_state()
                self.shape_start = pos
                self.shape_end = pos
                self.draw_state = 1
                self.action = "draw_click"
            elif self.draw_state == 1: 
                self.shape_end = pos
                th = max(1.0, self.toolbar.base_size)
                p1, p2 = self.shape_start, self.shape_end
                angle = math.atan2(_y(p2) - _y(p1), _x(p2) - _x(p1))
                p3 = p2 - QPointF(math.cos(angle - math.pi/4) * 15, math.sin(angle - math.pi/4) * 15)
                p4 = p2 - QPointF(math.cos(angle + math.pi/4) * 15, math.sin(angle + math.pi/4) * 15)
                pts = [p1, p2, p3, p4]
                r = QRectF(min(_x(p) for p in pts), min(_y(p) for p in pts), max(_x(p) for p in pts)-min(_x(p) for p in pts), max(_y(p) for p in pts)-min(_y(p) for p in pts))
                pad = max(th * 2.0, 4.0)
                self.strokes.append({'type': 'arrow', 'p1': QPointF(p1), 'p2': QPointF(p2), 'color': QColor(self.toolbar.current_color), 'thickness': th, 'rect': r.adjusted(-pad,-pad,pad,pad), 'angle': 0.0})
                self.draw_state = 0
                self.action = ""
            self.update()
            return
            
        elif self.toolbar.current_tool == "flex_arrow":
            if self.draw_state == 0: 
                self.save_state()
                self.shape_start = pos
                self.shape_ctrl = pos
                self.shape_end = pos
                self.draw_state = 1
                self.action = "draw_click"
            elif self.draw_state == 1: 
                self.shape_ctrl = pos
                self.shape_end = pos
                self.draw_state = 2
            elif self.draw_state == 2: 
                self.shape_end = pos
                th = max(1.0, self.toolbar.base_size)
                xs = [_x(self.shape_start), _x(self.shape_ctrl), _x(self.shape_end)]
                ys = [_y(self.shape_start), _y(self.shape_ctrl), _y(self.shape_end)]
                r = QRectF(min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys))
                pad = max(th * 2.0, 15.0)
                self.strokes.append({'type': 'flex_arrow', 'p1': QPointF(self.shape_start), 'p_ctrl': QPointF(self.shape_ctrl), 'p2': QPointF(self.shape_end), 'color': QColor(self.toolbar.current_color), 'thickness': th, 'rect': r.adjusted(-pad,-pad,pad,pad), 'angle': 0.0})
                self.draw_state = 0
                self.action = ""
            self.update()
            return
            
        elif self.toolbar.current_tool in ["pen", "highlight", "rect", "circle"]: 
            self.save_state()
            self.action = "draw_shape"
            self.drag_start_pos = pos
            self.last_pos = pos
            if self.toolbar.current_tool in ["pen", "highlight"]: 
                self.current_stroke_points = [(pos, getattr(self, 'current_pressure', 1.0))]
            elif self.toolbar.current_tool in ["rect", "circle"]: 
                self.shape_start = pos
                self.shape_end = pos
        self.update()

    def mouseMoveEvent(self, event):
        global_pos = event.globalPos()
        local_pos = self.mapFromGlobal(global_pos)
        canvas_pos = self.get_local_pos(global_pos)
        
        if getattr(self, 'm_panning', False):
            delta = global_pos - self.pan_start_pos
            new_x = self.scroll_x
            new_y = self.scroll_y
            if self.bg_size in ["infinite", "a4_landscape"]: 
                new_x = max(0, min(self.pan_start_scroll_x - _x(delta), self.max_scroll_x))
            if self.bg_size in ["infinite", "a4_portrait"]: 
                new_y = max(0, min(self.pan_start_scroll_y - _y(delta), self.max_scroll_y))
                
            actual_dx = new_x - self.scroll_x
            actual_dy = new_y - self.scroll_y
            if actual_dx != 0 or actual_dy != 0:
                self.scroll_x = new_x
                self.scroll_y = new_y
                for box in self.text_boxes: 
                    box.move(box.x() - actual_dx, box.y() - actual_dy)
                if self.header: self.header.raise_()
                if self.footer: self.footer.raise_()
                self.update()
            return
            
        if event.buttons() == Qt.NoButton:
            if self.action == "draw_click":
                if self.toolbar.current_tool == "arrow" and self.draw_state == 1: 
                    self.shape_end = canvas_pos
                elif self.toolbar.current_tool == "flex_arrow":
                    if self.draw_state == 1: 
                        self.shape_ctrl = canvas_pos
                        self.shape_end = canvas_pos
                    elif self.draw_state == 2: 
                        self.shape_end = canvas_pos
                self.update()
                return
                
            d = self.get_resize_dir(local_pos)
            if d in ["bottomright", "topleft"]: self.setCursor(Qt.SizeFDiagCursor)
            elif d in ["bottomleft", "topright"]: self.setCursor(Qt.SizeBDiagCursor)
            elif d in ["left", "right"]: self.setCursor(Qt.SizeHorCursor)
            elif d in ["top", "bottom"]: self.setCursor(Qt.SizeVerCursor)
            elif self.toolbar.current_tool in ["select", "text"]:
                hit_st, handle = self.hit_test_handles(canvas_pos)
                if self.toolbar.current_tool == "text" and hit_st and hit_st.get('type') != 'text': 
                    hit_st = None
                    handle = None
                if handle == "resize_ro": 
                    self.setCursor(Qt.CrossCursor)
                elif handle == "resize_pc": 
                    self.setCursor(Qt.CrossCursor)
                elif handle: 
                    self.setCursor(Qt.SizeFDiagCursor)
                elif self.hit_test_all(canvas_pos)[0] and (self.toolbar.current_tool == "select" or self.hit_test_all(canvas_pos)[0].get('type')=='text'): 
                    self.setCursor(Qt.SizeAllCursor)
                else: 
                    self.setCursor(Qt.ArrowCursor if self.toolbar.current_tool == "select" else Qt.CrossCursor)
            else: 
                self.setCursor(Qt.CrossCursor)
            return
            
        if self.action.startswith("resize_win_"):
            d = self.action.split("_")[2]
            dx = _x(global_pos) - _x(self.drag_start_global)
            dy = _y(global_pos) - _y(self.drag_start_global)
            new_geom = QRect(self.start_geometry)
            if "bottom" in d: new_geom.setBottom(new_geom.bottom() + dy)
            if "top" in d: new_geom.setTop(new_geom.top() + dy)
            if "right" in d: new_geom.setRight(new_geom.right() + dx)
            if "left" in d: new_geom.setLeft(new_geom.left() + dx)
            if new_geom.width() < 250: 
                new_geom.setLeft(new_geom.right() - 250) if "left" in d else new_geom.setRight(new_geom.left() + 250)
            if new_geom.height() < 200: 
                new_geom.setTop(new_geom.bottom() - 200) if "top" in d else new_geom.setBottom(new_geom.top() + 200)
            self.setGeometry(new_geom)
        elif self.action == "drag_win": 
            delta = global_pos - self.drag_start_global
            self.move(self.start_geometry.topLeft() + delta)
        elif self.action == "erase": 
            self.erase_at(canvas_pos)
            self.last_pos = canvas_pos
        else:
            if not self.is_tablet:
                if self.toolbar.use_pressure:
                    d = math.hypot(_x(canvas_pos) - _x(self.last_pos), _y(canvas_pos) - _y(self.last_pos))
                    self.last_pressure = self.current_pressure
                    self.current_pressure = self.last_pressure * 0.8 + min(2.5, max(0.1, d / 12.0)) * 0.2
                else: 
                    self.last_pressure = 1.0
                    self.current_pressure = 1.0
            self.process_move(canvas_pos, global_pos)

    def process_move(self, pos, global_pos):
        if self.action == "resize_ro":
            for st in self.selected_strokes:
                orig = self.stroke_start_positions[id(st)]
                cx = orig['rect'].center().x()
                cy = orig['rect'].center().y()
                dx = _x(pos) - cx
                dy = _y(pos) - cy
                angle = math.degrees(math.atan2(dy, dx)) + 90
                angle = round(angle / 5.0) * 5.0
                st['angle'] = angle
            self.update()
            return
            
        if self.action == "resize_pc":
            for st in self.selected_strokes:
                if st['type'] == 'flex_arrow':
                    orig = self.stroke_start_positions[id(st)]
                    angle = orig.get('angle', 0.0)
                    local_pos = self.get_local_coords(orig['rect'], angle, pos)
                    local_drag_start = self.get_local_coords(orig['rect'], angle, self.drag_start_pos)
                    dx = _x(local_pos) - _x(local_drag_start)
                    dy = _y(local_pos) - _y(local_drag_start)
                    st['p_ctrl'] = orig['p_ctrl'] + QPointF(dx, dy)
                    xs = [_x(st['p1']), _x(st['p2']), _x(st['p_ctrl'])]
                    ys = [_y(st['p1']), _y(st['p2']), _y(st['p_ctrl'])]
                    st['rect'] = QRectF(min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys)).adjusted(-20,-20,20,20)
            self.update()
            return
            
        if self.action.startswith("resize_"):
            h = self.action.split("_")[1]
            for st in self.selected_strokes:
                orig = self.stroke_start_positions[id(st)]
                orig_rect = orig['rect']
                angle = orig.get('angle', 0.0)
                local_pos = self.get_local_coords(orig_rect, angle, pos)
                local_drag_start = self.get_local_coords(orig_rect, angle, self.drag_start_pos)
                dx = _x(local_pos) - _x(local_drag_start)
                dy = _y(local_pos) - _y(local_drag_start)
                nw = orig_rect.width()
                nh = orig_rect.height()
                
                if 'l' in h: nw -= dx
                if 'r' in h: nw += dx
                if 't' in h: nh -= dy
                if 'b' in h: nh += dy
                nw = max(10, nw)
                nh = max(10, nh)
                
                if len(h) == 2 and h not in ['tc', 'bc', 'ml', 'mr']: 
                    scale = max(nw / orig_rect.width() if orig_rect.width() > 0 else 1.0, nh / orig_rect.height() if orig_rect.height() > 0 else 1.0)
                    sx = scale
                    sy = scale
                else: 
                    sx = nw / orig_rect.width() if orig_rect.width() > 0 else 1.0
                    sy = nh / orig_rect.height() if orig_rect.height() > 0 else 1.0
                    
                ox = orig_rect.right() if 'l' in h else orig_rect.left()
                oy = orig_rect.bottom() if 't' in h else orig_rect.top()
                t = QTransform()
                t.translate(ox, oy)
                t.scale(sx, sy)
                t.translate(-ox, -oy)
                
                if st['type'] in ['pen', 'highlight']: 
                    st['points'] = [(t.map(p), pr) for p, pr in orig.get('points', [])]
                    st['base_size'] = orig['base_size'] * max(sx, sy)
                elif st['type'] == 'flex_arrow': 
                    st['p1'] = t.map(orig['p1'])
                    st['p2'] = t.map(orig['p2'])
                    st['p_ctrl'] = t.map(orig['p_ctrl'])
                    st['thickness'] = orig['thickness'] * max(sx, sy)
                elif st['type'] in ['arrow', 'rect', 'circle']: 
                    st['p1'] = t.map(orig['p1'])
                    st['p2'] = t.map(orig['p2'])
                    st['thickness'] = orig['thickness'] * max(sx, sy)
                elif st['type'] == 'image': 
                    st['rect'] = t.mapRect(orig['rect'])
                    continue
                st['rect'] = t.mapRect(orig['rect'])
            self.update()
            return
            
        if self.action == "drag_st":
            dx = _x(pos) - _x(self.drag_start_pos)
            dy = _y(pos) - _y(self.drag_start_pos)
            for st in self.selected_strokes:
                orig = self.stroke_start_positions[id(st)]
                if st['type'] in ['pen', 'highlight']: 
                    st['points'] = [(p + QPointF(dx, dy), pr) for p, pr in orig.get('points', [])]
                elif st['type'] == 'flex_arrow': 
                    st['p1'] = orig['p1'] + QPointF(dx, dy)
                    st['p2'] = orig['p2'] + QPointF(dx, dy)
                    st['p_ctrl'] = orig['p_ctrl'] + QPointF(dx, dy)
                elif st['type'] in ['arrow', 'rect', 'circle']: 
                    st['p1'] = orig['p1'] + QPointF(dx, dy)
                    st['p2'] = orig['p2'] + QPointF(dx, dy)
                st['rect'] = orig['rect'].translated(dx, dy)
            self.update()
            return
            
        if self.action == "draw_text": 
            self.temp_text_rect = QRect(self.drag_start_pos.toPoint(), pos.toPoint()).normalized()
            self.update()
            return
            
        if self.action == "draw_shape":
            if self.toolbar.current_tool in ["pen", "highlight"]: 
                self.current_stroke_points.append((pos, getattr(self, 'current_pressure', 1.0)))
            elif self.toolbar.current_tool in ["rect", "circle"]: 
                self.shape_end = pos
            self.last_pos = pos
            self.update()

    def mouseReleaseEvent(self, event):
        if self.m_panning: 
            self.m_panning = False
            self.setCursor(Qt.ArrowCursor)
            
        if event.button() == Qt.MouseButton.LeftButton:
            if self.action not in ["draw_click"]: 
                self.action = "" if self.action.startswith("resize_win_") or self.action == "drag_win" else self.action
            self.process_release(self.get_local_pos(event.globalPos()), event.globalPos())
        super().mouseReleaseEvent(event)

    def process_release(self, pos, global_pos):
        if self.action == "draw_text":
            if self.temp_text_rect.width() > 15 and self.temp_text_rect.height() > 15:
                for tb in list(self.text_boxes): 
                    if hasattr(tb, 'commit_self'): tb.commit_self()
                tb = SmartTextBox(self, self.toolbar, self.toolbar.size_spinbox.value(), self.toolbar.current_color, self.toolbar.btn_bold.isChecked())
                tb.setGeometry(self.temp_text_rect.translated(-self.scroll_x, -self.scroll_y))
                tb.show()
                tb.raise_()
                tb.setFocus()
                self.text_boxes.append(tb)
            self.temp_text_rect = QRect()
            self.update()
            
        elif self.action == "draw_shape":
            if self.toolbar.current_tool in ["pen", "highlight"]:
                if len(self.current_stroke_points) > 0:
                    xs = [_x(p) for p, pr in self.current_stroke_points]
                    ys = [_y(p) for p, pr in self.current_stroke_points]
                    min_x, max_x = min(xs), max(xs)
                    min_y, max_y = min(ys), max(ys)
                    r = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
                    b = self.toolbar.base_size * 2
                    r = r.adjusted(-b,-b,b,b)
                    if r.width() >= 0 and r.height() >= 0: 
                        self.strokes.append({'type': 'pen' if self.toolbar.current_tool == "pen" else 'highlight', 'points': list(self.current_stroke_points), 'color': self.toolbar.current_color, 'base_size': self.toolbar.base_size, 'use_pressure': self.toolbar.use_pressure, 'rect': r, 'angle': 0.0})
            elif self.toolbar.current_tool in ["rect", "circle"]:
                r = QRectF(self.shape_start, self.shape_end).normalized()
                if self.toolbar.current_tool == "circle": 
                    rad = math.hypot(_x(self.shape_end)-_x(self.shape_start), _y(self.shape_end)-_y(self.shape_start))
                    r = QRectF(_x(self.shape_start)-rad, _y(self.shape_start)-rad, 2*rad, 2*rad)
                th = max(1.0, self.toolbar.base_size)
                r = r.adjusted(-th-1, -th-1, th+1, th+1)
                if r.width() >= 0 and r.height() >= 0: 
                    self.strokes.append({'type': self.toolbar.current_tool, 'p1': QPointF(self.shape_start), 'p2': QPointF(self.shape_end), 'color': QColor(self.toolbar.current_color), 'thickness': th, 'rect': r, 'angle': 0.0})
            self.action = ""
            self.update()

    def export_action(self):
        self.setFocus()
        self.toolbar.active_text_box = None
        QApplication.processEvents()
        
        msg = QMessageBox(self)
        msg.setText("Select Orientation")
        btn_portrait = msg.addButton("Portrait", QMessageBox.YesRole)
        btn_portrait.setIcon(create_template_icon("a4_portrait"))
        btn_portrait.setIconSize(QSize(48, 48))
        btn_landscape = msg.addButton("Landscape", QMessageBox.YesRole)
        btn_landscape.setIcon(create_template_icon("a4_landscape"))
        btn_landscape.setIconSize(QSize(48, 48))
        btn_cancel = msg.addButton("Cancel", QMessageBox.RejectRole)
        msg.exec_()
        
        if msg.clickedButton() == btn_portrait: 
            orientation_mode = QPageLayout.Portrait
        elif msg.clickedButton() == btn_landscape: 
            orientation_mode = QPageLayout.Landscape
        else: 
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF Document (*.pdf);;PNG Image (*.png)")
        if not file_path: return
        
        pages_to_export = getattr(self, 'captured_pages', []).copy()
        if self.text_boxes:
            for tb in list(self.text_boxes): 
                if hasattr(tb, 'commit_self'): tb.commit_self()
                
        if not pages_to_export:
            max_y = 0
            if self.strokes:
                for s in self.strokes:
                    if s['rect'].bottom() > max_y: max_y = s['rect'].bottom()
            if self.text_boxes:
                header_h = self.header.height() if self.header else 0
                for tb in self.text_boxes:
                    abs_y = tb.y() - header_h + self.scroll_y + tb.height()
                    if abs_y > max_y: max_y = abs_y
                    
            page_w = self.width()
            page_h = int(page_w * 1.4142) if orientation_mode == QPageLayout.Portrait else int(page_w / 1.4142)
            bg_c = QColor(self.current_bg_color[1])
            bg_c.setAlpha(255)
            y_pos = 0
            
            while y_pos <= max_y or y_pos == 0:
                final_image = QImage(page_w, page_h, QImage.Format_ARGB32_Premultiplied)
                final_image.fill(bg_c)
                painter = QPainter(final_image)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.save()
                painter.translate(0, -y_pos)
                self.draw_template(painter, 0, y_pos, page_w, y_pos + page_h, y_pos)
                painter.restore()
                self.render_content(painter, y_pos, is_export=True)
                painter.end()
                pages_to_export.append(QPixmap.fromImage(final_image))
                y_pos += page_h

        try:
            if file_path.endswith('.pdf'):
                writer = QPdfWriter(file_path)
                writer.setPageOrientation(orientation_mode)
                writer.setResolution(300)
                painter = QPainter(writer)
                for i, pixmap in enumerate(pages_to_export):
                    if i > 0: writer.newPage()
                    rect = painter.viewport()
                    img_size = pixmap.size()
                    img_size.scale(rect.size(), Qt.KeepAspectRatio)
                    x = (rect.width() - img_size.width()) // 2
                    y = (rect.height() - img_size.height()) // 2
                    draw_rect = QRect(x, y, img_size.width(), img_size.height())
                    painter.drawPixmap(draw_rect, pixmap)
                painter.end()
            elif file_path.endswith('.png'): 
                pages_to_export[-1].save(file_path)
        except Exception as e: 
            pass

    def draw_template(self, painter, start_x, start_y, end_x, end_y, scroll_y_offset=0):
        spacing = 25
        sy = int(start_y - (start_y % spacing))
        sx = int(start_x - (start_x % spacing))
        if self.bg_pattern == "rules":
            painter.setPen(QPen(QColor(173,216,230,200),1))
            for y in range(sy, int(end_y), spacing): 
                painter.drawLine(sx, y, int(end_x), y)
        elif self.bg_pattern == "square":
            painter.setPen(QPen(QColor(0,0,0,20),1))
            for y in range(sy, int(end_y), spacing): 
                painter.drawLine(sx, y, int(end_x), y)
            for x in range(sx, int(end_x), spacing): 
                painter.drawLine(x, int(scroll_y_offset), x, int(end_y))
        elif self.bg_pattern == "dots":
            painter.setBrush(QBrush(QColor(0,0,0,30)))
            painter.setPen(Qt.NoPen)
            for y in range(sy, int(end_y), spacing):
                for x in range(sx, int(end_x), spacing): 
                    painter.drawEllipse(x-1, y-1, 2, 2)

    def draw_vector_stroke(self, painter, s):
        if s['type'] == 'image': 
            painter.drawImage(s['rect'], s['img'])
            return
        elif s['type'] == 'text':
            painter.setPen(QPen(QColor(s['color'])))
            font = QFont("Arial", s.get('font_size', 18))
            font.setBold(s.get('is_bold', False))
            painter.setFont(font)
            painter.drawText(s['rect'], Qt.AlignLeft | Qt.TextWordWrap, s['text'])
            return
            
        color = QColor(s['color'])
        if s['type'] in ['highlight', 'pen']:
            if s['type'] == 'highlight': 
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                color.setAlpha(80)
            else: 
                painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                
            painter.setBrush(Qt.NoBrush)
            pts = s.get('points', [])
            if len(pts) == 1:
                p, pr = pts[0]
                th = s['base_size'] * (pr * 2.0 if s.get('use_pressure', False) else 1.0)
                painter.setPen(QPen(color, max(1.0, th), Qt.SolidLine, Qt.FlatCap if s['type']=='highlight' else Qt.RoundCap, Qt.RoundJoin))
                painter.drawPoint(p)
            for i in range(len(pts)-1):
                p1, pr1 = pts[i]
                p2, pr2 = pts[i+1]
                th = s['base_size'] * (pr2 * 2.0 if s.get('use_pressure', False) else 1.0)
                painter.setPen(QPen(color, max(1.0, th), Qt.SolidLine, Qt.FlatCap if s['type']=='highlight' else Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(p1, p2)
            return
            
        if s['type'] == "highlight": 
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            color.setAlpha(80)
        else: 
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
        painter.setBrush(Qt.NoBrush)
        if s['type'] == 'flex_arrow':
            painter.setPen(QPen(color, s['thickness'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(s['p1'], s['p_ctrl'])
            painter.drawLine(s['p_ctrl'], s['p2'])
            a_head = math.atan2(_y(s['p2']) - _y(s['p_ctrl']), _x(s['p2']) - _x(s['p_ctrl']))
            p3 = s['p2'] - QPointF(math.cos(a_head - math.pi/4) * 15, math.sin(a_head - math.pi/4) * 15)
            p4 = s['p2'] - QPointF(math.cos(a_head + math.pi/4) * 15, math.sin(a_head + math.pi/4) * 15)
            painter.setPen(QPen(color, s['thickness'] * 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(s['p2'], p3)
            painter.drawLine(s['p2'], p4)
        elif s['type'] == 'rect': 
            painter.setPen(QPen(color, s['thickness'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawRect(QRectF(s['p1'], s['p2']).normalized())
        elif s['type'] == 'circle': 
            painter.setPen(QPen(color, s['thickness'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            pad = s.get('thickness', 1.0) + 1
            painter.drawEllipse(s['rect'].adjusted(pad, pad, -pad, -pad).normalized())
        elif s['type'] == 'arrow':
            painter.setPen(QPen(color, s['thickness'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(s['p1'], s['p2'])
            angle = math.atan2(_y(s['p2']) - _y(s['p1']), _x(s['p2']) - _x(s['p1']))
            p3 = s['p2'] - QPointF(math.cos(angle - math.pi/4) * 15, math.sin(angle - math.pi/4) * 15)
            p4 = s['p2'] - QPointF(math.cos(angle + math.pi/4) * 15, math.sin(angle + math.pi/4) * 15)
            painter.setPen(QPen(color, s['thickness'] * 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(s['p2'], p3)
            painter.drawLine(s['p2'], p4)

    def draw_live_preview(self, painter):
        if self.action != "draw_shape" and self.action != "draw_click": return
        color = QColor(self.toolbar.current_color)
        if self.toolbar.current_tool in ["pen", "highlight"]:
            if self.toolbar.current_tool == "highlight": color.setAlpha(80)
            painter.setBrush(Qt.NoBrush)
            for i in range(len(self.current_stroke_points)-1):
                p1, pr1 = self.current_stroke_points[i]
                p2, pr2 = self.current_stroke_points[i+1]
                th = self.toolbar.base_size * (pr2 * 2.0 if self.toolbar.use_pressure else 1.0)
                painter.setPen(QPen(color, max(1.0, th), Qt.SolidLine, Qt.FlatCap if self.toolbar.current_tool=="highlight" else Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(p1, p2)
        elif self.toolbar.current_tool in ["arrow", "flex_arrow", "rect", "circle"]:
            painter.setBrush(Qt.NoBrush)
            if self.toolbar.current_tool == "rect": 
                painter.setPen(QPen(color, max(1.0, self.toolbar.base_size), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawRect(QRectF(self.shape_start, self.shape_end).normalized())
            elif self.toolbar.current_tool == "circle": 
                painter.setPen(QPen(color, max(1.0, self.toolbar.base_size), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawEllipse(QRectF(self.shape_start, self.shape_end).normalized())
            elif self.toolbar.current_tool == "arrow" and self.draw_state > 0: 
                painter.setPen(QPen(color, max(1.0, self.toolbar.base_size), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.shape_start, self.shape_end)
                angle = math.atan2(_y(self.shape_end) - _y(self.shape_start), _x(self.shape_end) - _x(self.shape_start))
                p3 = self.shape_end - QPointF(math.cos(angle - math.pi/4) * 15, math.sin(angle - math.pi/4) * 15)
                p4 = self.shape_end - QPointF(math.cos(angle + math.pi/4) * 15, math.sin(angle + math.pi/4) * 15)
                painter.setPen(QPen(color, max(1.0, self.toolbar.base_size * 2), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.shape_end, p3)
                painter.drawLine(self.shape_end, p4)
            elif self.toolbar.current_tool == "flex_arrow" and self.draw_state > 0:
                painter.setPen(QPen(color, max(1.0, self.toolbar.base_size), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                if self.draw_state == 1: 
                    painter.drawLine(self.shape_start, self.shape_end)
                elif self.draw_state == 2: 
                    painter.drawLine(self.shape_start, self.shape_ctrl)
                    painter.drawLine(self.shape_ctrl, self.shape_end)
                    a_head = math.atan2(_y(self.shape_end) - _y(self.shape_ctrl), _x(self.shape_end) - _x(self.shape_ctrl))
                    p3 = self.shape_end - QPointF(math.cos(a_head - math.pi/4) * 15, math.sin(a_head - math.pi/4) * 15)
                    p4 = self.shape_end - QPointF(math.cos(a_head + math.pi/4) * 15, math.sin(a_head + math.pi/4) * 15)
                    painter.setPen(QPen(color, max(1.0, self.toolbar.base_size * 2), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                    painter.drawLine(self.shape_end, p3)
                    painter.drawLine(self.shape_end, p4)

    def render_content(self, painter, vy=0, is_export=False):
        for s in self.strokes:
            painter.save()
            if is_export: 
                painter.translate(0, -vy)
            r = s['rect']
            painter.translate(r.center().x(), r.center().y())
            painter.rotate(s.get('angle', 0.0))
            painter.translate(-r.center().x(), -r.center().y())
            self.draw_vector_stroke(painter, s)
            painter.restore()
            
        if is_export:
            header_h = self.header.height() if self.header else 0
            for tb in self.text_boxes:
                vx = tb.x() + self.scroll_x
                vy_tb = tb.y() - header_h + self.scroll_y
                painter.save()
                painter.translate(vx, vy_tb - vy)
                tb.document().drawContents(painter)
                painter.restore()

    def paintEvent(self, event):
        if not hasattr(self, 'current_bg_color'): return
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width()-1, self.height()-1, 12, 12)
        
        bg_c = QColor(self.current_bg_color[1])
        bg_c.setAlpha(self.note_bg_alpha)
        painter.fillPath(path, bg_c)
        
        painter.save()
        painter.setClipPath(path)
        
        h_height = self.header.height() if (self.header and self.header.isVisible()) else 0
        f_height = self.footer.height() if (self.footer and self.footer.isVisible()) else 0
        
        hc = QColor(self.current_bg_color[0])
        hc.setAlpha(255)
        
        if h_height > 0: 
            painter.fillRect(0, 0, self.width(), h_height, hc)
        if f_height > 0 and not self.is_minimized: 
            painter.fillRect(0, self.height()-f_height, self.width(), f_height, hc)
        painter.restore()
        
        if self.is_minimized: 
            painter.setPen(QPen(QColor(0,0,0,40),1))
            painter.drawPath(path)
            return
            
        painter.save()
        clip_region = QRegion(self.rect())
        if self.toolbar.isVisible(): 
            clip_region = clip_region.subtracted(QRegion(QRect(self.mapFromGlobal(self.toolbar.geometry().topLeft()), self.toolbar.geometry().size())))
            
        painter.setClipPath(path)
        painter.setClipRegion(clip_region, Qt.IntersectClip)
        painter.setClipRect(QRect(0, h_height, self.width(), self.height()-h_height-f_height))
        painter.translate(-self.scroll_x, -self.scroll_y)
        
        self.draw_template(painter, self.scroll_x, self.scroll_y, self.scroll_x + self.width(), self.scroll_y + self.height(), self.scroll_y)
        self.render_content(painter, 0, is_export=False)
        self.draw_live_preview(painter)
        
        # Draw infinite canvas page break markers
        page_h = int(self.width() * 1.4142)
        start_page = int(self.scroll_y // page_h)
        end_page = int((self.scroll_y + self.height()) // page_h) + 1
        for p in range(start_page + 1, end_page + 1):
            y_break = p * page_h
            painter.fillRect(self.scroll_x, y_break - 2, self.width(), 4, QColor(0, 0, 0, 40))
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.drawLine(self.scroll_x, y_break, self.scroll_x + self.width(), y_break)
            
        if self.action == "draw_text": 
            painter.setPen(QPen(QColor(100, 100, 100), 1, Qt.DashLine))
            painter.drawRect(self.temp_text_rect)
            
        for st in self.selected_strokes:
            r = st['rect']
            painter.save()
            t = QTransform()
            t.translate(r.center().x(), r.center().y())
            t.rotate(st.get('angle', 0.0))
            t.translate(-r.center().x(), -r.center().y())
            painter.setTransform(t, True)
            
            painter.setPen(QPen(QColor(0, 120, 215), 1.5, Qt.DashLine))
            painter.drawRect(r)
            painter.drawLine(int(r.center().x()), int(r.top()), int(r.center().x()), int(r.top() - 25))
            
            painter.setBrush(QBrush(Qt.white))
            painter.setPen(QPen(QColor(0,120,215), 1.5))
            handles = [r.topLeft(), QPointF(r.center().x(), r.top()), r.topRight(), QPointF(r.left(), r.center().y()), QPointF(r.right(), r.center().y()), r.bottomLeft(), QPointF(r.center().x(), r.bottom()), r.bottomRight(), QPointF(r.center().x(), r.top() - 25)]
            for h in handles: 
                painter.drawEllipse(h, 4, 4)
                
            if st['type'] == 'flex_arrow': 
                painter.setBrush(QBrush(Qt.yellow))
                painter.setPen(QPen(QColor(0,0,0), 1.5))
                px = _x(st['p_ctrl']) - r.center().x()
                py = _y(st['p_ctrl']) - r.center().y()
                painter.drawEllipse(QPointF(px, py), 6, 6)
            painter.restore()
            
        painter.restore()
        painter.setClipping(False)
        painter.setPen(QPen(QColor(0,0,0,40),1))
        painter.drawPath(path)


class Toolbar(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.current_tool = "pen"
        self.current_color = QColor("#ff0000")
        self.base_size = 4
        self.use_pressure = False
        self.active_text_box = None
        self.slider_popup = None
        self.clipboard = []
        
        self.initUI()
        self.note_boxes = []
        self.add_note_box()
        self.change_tool("pen")
        self.format_container.hide()

    def initUI(self):
        container_layout = QVBoxLayout(self)
        container_layout.setContentsMargins(0,0,0,0)
        container_layout.setSpacing(6)
        
        self.main_bar = QFrame()
        self.main_bar.setStyleSheet("QFrame { background-color: #e5e8f0; border-radius: 22px; border: none; } QPushButton { background-color: transparent; border-radius: 10px; } QPushButton:hover { background-color: #d0d4df; } QPushButton:checked { background-color: white; border: none; }")
        
        main_layout = QVBoxLayout(self.main_bar)
        main_layout.setContentsMargins(14,4,14,4)
        row1_layout = QHBoxLayout()
        
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        tools = ["select", "pen", "highlight", "eraser", "arrow", "flex_arrow", "rect", "circle", "text"]
        for t in tools:
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setFixedSize(46, 36)
            btn.setIcon(create_tool_icon(t))
            btn.setIconSize(QSize(32, 32))
            btn.setFocusPolicy(Qt.NoFocus)
            btn.clicked.connect(lambda checked, tool=t: self.handle_tool_click(tool))
            self.tool_group.addButton(btn)
            row1_layout.addWidget(btn)
            if t == "pen": 
                btn.setChecked(True)
                
        self.btn_exit = QPushButton()
        self.btn_exit.setFixedSize(46, 36)
        self.btn_exit.setFocusPolicy(Qt.NoFocus)
        self.btn_exit.setIcon(create_tool_icon("exit"))
        self.btn_exit.setIconSize(QSize(32, 32))
        self.btn_exit.setStyleSheet("QPushButton { background-color: transparent; border-radius: 10px; } QPushButton:hover { background-color: #ffcccc; }")
        self.btn_exit.clicked.connect(QApplication.instance().quit)
        row1_layout.addWidget(self.btn_exit)
        
        main_layout.addLayout(row1_layout)
        container_layout.addWidget(self.main_bar)
        
        self.format_container = QFrame()
        self.format_container.setStyleSheet("QFrame#format_container { background-color: transparent; border: none; }")
        self.format_container.setObjectName("format_container")
        format_layout = QHBoxLayout(self.format_container)
        format_layout.setContentsMargins(0,0,0,0)
        format_layout.setSpacing(6)
        
        self.color_panel = QFrame()
        self.color_panel.setStyleSheet("QFrame { background-color: #dde4f0; border-radius: 20px; border: none; }")
        color_layout = QHBoxLayout(self.color_panel)
        color_layout.setContentsMargins(6,4,6,4)
        
        self.color_group = QButtonGroup(self)
        self.color_group.setExclusive(True)
        colors = [("#ff0000","Red"), ("#ff007f","Pink"), ("#ffff00","Yellow"), ("#55aaff","Light Blue"), ("#0000ff","Dark Blue"), ("#000000","Black"), ("#ffffff","White")]
        for hc, nm in colors:
            btn = QPushButton("")
            btn.setFixedSize(36,36)
            btn.setFocusPolicy(Qt.NoFocus)
            border_css = "border: 1px solid rgba(0,0,0,0.15);" if nm == "White" else "border: 1px solid transparent;"
            btn.setStyleSheet(f"QPushButton {{ background-color: {hc}; border-radius: 12px; {border_css} margin: 6px; }} QPushButton:checked {{ background-color: {hc}; border-radius: 18px; margin: 0px; border: 4px solid #c8d0e0; padding: 2px; background-clip: content-box; }}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, h=hc: self.change_color(h))
            self.color_group.addButton(btn)
            color_layout.addWidget(btn)
            if nm == "Red": 
                btn.setChecked(True) 
                
        self.stroke_panel = QFrame()
        self.stroke_panel.setStyleSheet("QFrame { background-color: #dde4f0; border-radius: 20px; border: none; }")
        stroke_layout = QHBoxLayout(self.stroke_panel)
        stroke_layout.setContentsMargins(8,4,8,4)
        stroke_layout.setSpacing(6)
        
        self.stroke_group = QButtonGroup(self)
        self.stroke_group.setExclusive(True)
        
        for s in [4, 8, 14]: 
            btn = StrokeButton(s, self)
            self.stroke_group.addButton(btn)
            stroke_layout.addWidget(btn)
            if s == 4: 
                btn.setChecked(True)
                
        sep = QFrame()
        sep.setFixedWidth(1)
        sep.setStyleSheet("border-left: 1px dashed #a0aabf; background: transparent;")
        stroke_layout.addWidget(sep)
        
        self.btn_pressure = QPushButton()
        self.btn_pressure.setIcon(create_wave_icon())
        self.btn_pressure.setIconSize(QSize(64,24))
        self.btn_pressure.setFixedSize(64,32)
        self.btn_pressure.setCheckable(True)
        self.btn_pressure.setFocusPolicy(Qt.NoFocus)
        self.btn_pressure.setStyleSheet("QPushButton { border: none; border-radius: 16px; background: transparent; } QPushButton:checked { background-color: rgba(0,0,0,0.1); }")
        self.btn_pressure.clicked.connect(lambda checked: self.change_thickness("pressure"))
        self.stroke_group.addButton(self.btn_pressure)
        stroke_layout.addWidget(self.btn_pressure)
        
        self.eraser_panel = QFrame()
        self.eraser_panel.setStyleSheet("QFrame { background-color: #dde4f0; border-radius: 20px; border: none; }")
        eraser_layout = QHBoxLayout(self.eraser_panel)
        eraser_layout.setContentsMargins(12,4,12,4)
        eraser_layout.setSpacing(12)
        
        lbl_eraser = QLabel()
        lbl_eraser.setPixmap(create_stroke_erase_icon().pixmap(32, 32))
        lbl_eraser.setFixedSize(32, 32)
        lbl_eraser.setAlignment(Qt.AlignCenter)
        eraser_layout.addWidget(lbl_eraser)
        
        sep2 = QFrame()
        sep2.setFixedWidth(1)
        sep2.setStyleSheet("border-left: 1px dashed #a0aabf; background: transparent;")
        eraser_layout.addWidget(sep2)
        
        btn_undo = QPushButton()
        btn_undo.setIcon(create_undo_icon_png())
        btn_undo.setIconSize(QSize(26,26))
        btn_undo.setFixedSize(32,32)
        btn_undo.setFocusPolicy(Qt.NoFocus)
        btn_undo.setStyleSheet("QPushButton { border: none; border-radius: 16px; background: transparent; } QPushButton:hover { background-color: rgba(0,0,0,0.1); }")
        btn_undo.clicked.connect(self.undo_action)
        eraser_layout.addWidget(btn_undo)
        
        btn_redo = QPushButton()
        btn_redo.setIcon(create_redo_icon_png())
        btn_redo.setIconSize(QSize(26,26))
        btn_redo.setFixedSize(32,32)
        btn_redo.setFocusPolicy(Qt.NoFocus)
        btn_redo.setStyleSheet("QPushButton { border: none; border-radius: 16px; background: transparent; } QPushButton:hover { background: rgba(0,0,0,0.1); }")
        btn_redo.clicked.connect(self.redo_action)
        eraser_layout.addWidget(btn_redo)
        
        sep3 = QFrame()
        sep3.setFixedWidth(1)
        sep3.setStyleSheet("border-left: 1px dashed #a0aabf; background: transparent;")
        eraser_layout.addWidget(sep3)
        
        btn_clear = QPushButton()
        btn_clear.setIcon(create_clear_icon())
        btn_clear.setIconSize(QSize(26,26))
        btn_clear.setFixedSize(32,32)
        btn_clear.setFocusPolicy(Qt.NoFocus)
        btn_clear.setStyleSheet("QPushButton { border: none; border-radius: 16px; background: transparent; } QPushButton:hover { background-color: rgba(0,0,0,0.1); }")
        btn_clear.clicked.connect(self.clear_action)
        eraser_layout.addWidget(btn_clear)
        
        self.text_format_panel = QFrame()
        self.text_format_panel.setStyleSheet("QFrame { background-color: #dde4f0; border-radius: 20px; } QSpinBox { border: 1px solid #888; border-radius: 4px; padding: 2px; background: white;} QPushButton { background-color: transparent; border-radius: 4px; padding: 4px; font-weight: bold; color: #333; } QPushButton:hover { background-color: rgba(255,255,255,0.5); } QPushButton:checked { background-color: white; border: 2px solid #aaa; }")
        text_layout = QHBoxLayout(self.text_format_panel)
        text_layout.setContentsMargins(12,4,12,4)
        
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(8,72)
        self.size_spinbox.setValue(18)
        self.size_spinbox.setFocusPolicy(Qt.ClickFocus)
        self.size_spinbox.valueChanged.connect(self.change_text_size)
        
        self.btn_bold = QPushButton("B")
        self.btn_bold.setCheckable(True)
        self.btn_bold.setFixedSize(30,26)
        self.btn_bold.setFocusPolicy(Qt.NoFocus)
        self.btn_bold.clicked.connect(self.toggle_text_bold)
        
        text_layout.addWidget(QLabel("Size:"))
        text_layout.addWidget(self.size_spinbox)
        text_layout.addWidget(self.btn_bold)
        
        format_layout.addWidget(self.color_panel)
        format_layout.addWidget(self.stroke_panel)
        format_layout.addWidget(self.eraser_panel)
        format_layout.addWidget(self.text_format_panel)
        format_layout.addStretch()
        
        container_layout.addWidget(self.format_container)
        container_layout.addStretch()
        self.move(40,40)

    def show_stroke_slider(self, button_ref):
        if self.slider_popup: 
            self.slider_popup.close()
        self.slider_popup = StrokeSliderPopup(self)
        self.slider_popup.move(button_ref.mapToGlobal(QPoint(button_ref.width()//2-75, button_ref.height()+5)))
        self.slider_popup.show()
        
    def hide_stroke_slider(self):
        if self.slider_popup: 
            self.slider_popup.close()
            self.slider_popup = None
            
    def get_active_canvas(self): 
        return self.note_boxes[-1] if self.note_boxes else None
        
    def undo_action(self): 
        cv = self.get_active_canvas()
        if cv: 
            cv.undo()
            
    def redo_action(self): 
        cv = self.get_active_canvas()
        if cv: 
            cv.redo()
            
    def change_color(self, hex_code):
        self.current_color = QColor(hex_code)
        if getattr(self, 'active_text_box', None) and self.current_tool == "text":
            try: 
                self.active_text_box.setTextColor(self.current_color)
            except RuntimeError: 
                self.active_text_box = None
        canvas = self.get_active_canvas()
        if canvas and canvas.selected_strokes:
            for st in canvas.selected_strokes:
                if st.get('type') == 'text': 
                    st['color'] = self.current_color
                elif st.get('type') in ['pen', 'highlight', 'arrow', 'flex_arrow', 'rect', 'circle']: 
                    st['color'] = self.current_color
            canvas.update()
            
    def change_thickness(self, val):
        if val == "pressure": 
            self.use_pressure = True
        else: 
            self.base_size = val 
            if self.stroke_group.checkedButton() != self.btn_pressure: 
                self.use_pressure = False
                
    def change_text_size(self, size):
        if getattr(self, 'active_text_box', None):
            try: 
                fmt = self.active_text_box.currentCharFormat()
                fmt.setFontPointSize(size)
                self.active_text_box.mergeCurrentCharFormat(fmt)
            except RuntimeError: 
                self.active_text_box = None
        canvas = self.get_active_canvas()
        if canvas and canvas.selected_strokes:
            for st in canvas.selected_strokes:
                if st.get('type') == 'text': 
                    st['font_size'] = size
            canvas.update()
            
    def toggle_text_bold(self):
        if getattr(self, 'active_text_box', None):
            try: 
                fmt = self.active_text_box.currentCharFormat()
                fmt.setFontWeight(QFont.Bold if self.btn_bold.isChecked() else QFont.Normal)
                self.active_text_box.mergeCurrentCharFormat(fmt)
            except RuntimeError: 
                self.active_text_box = None
        canvas = self.get_active_canvas()
        if canvas and canvas.selected_strokes:
            for st in canvas.selected_strokes:
                if st.get('type') == 'text': 
                    st['is_bold'] = self.btn_bold.isChecked()
            canvas.update()

    def mousePressEvent(self, event): 
        self.raise_()
        self.hide_stroke_slider()
        if event.button() == Qt.LeftButton: 
            self.dragging = True
            self.drag_offset = event.pos()
            
    def mouseMoveEvent(self, event):
        if getattr(self, 'dragging', False): 
            self.move(self.mapToParent(event.pos() - getattr(self, 'drag_offset', QPoint())))
            
    def mouseReleaseEvent(self, event): 
        self.dragging = False
        
    def clear_action(self): 
        cv = self.get_active_canvas()
        if cv: 
            cv.clear_canvas()
            
    def add_note_box(self):
        if len(self.note_boxes) >= 10: 
            return 
        new_note = FloatingNoteBox(self)
        self.note_boxes.append(new_note)
        new_note.show()
        new_note.raise_()
        
    def remove_note_box(self, note):
        note.stamp_selection()
        if note in self.note_boxes: 
            self.note_boxes.remove(note)
            note.deleteLater()
        if len(self.note_boxes) == 0: 
            self.add_note_box()
            
    def handle_tool_click(self, tool):
        if self.current_tool == tool:
            if tool != "select": 
                self.format_container.setVisible(not self.format_container.isVisible())
        else: 
            self.change_tool(tool)
            
    def change_tool(self, tool):
        for note in self.note_boxes: 
            note.stamp_selection()
            note.draw_state = 0
            note.action = ""
            
        if self.slider_popup: 
            self.slider_popup.close()
            
        self.current_tool = tool
        has_options = False
        self.color_panel.hide()
        self.stroke_panel.hide()
        self.text_format_panel.hide()
        self.eraser_panel.hide()
        
        if tool in ["pen", "highlight", "arrow", "flex_arrow", "rect", "circle"]: 
            self.color_panel.show()
            self.stroke_panel.show()
            has_options = True
        elif tool == "eraser": 
            self.eraser_panel.show()
            has_options = True
        elif tool == "text": 
            self.color_panel.show()
            self.text_format_panel.show()
            has_options = True
            
        if has_options: 
            self.format_container.show()
        else: 
            self.format_container.hide()
            
        for note in self.note_boxes:
            for tb in note.text_boxes: 
                tb.setAttribute(Qt.WA_TransparentForMouseEvents, False)
            note.setCursor(Qt.ArrowCursor if tool == "select" else Qt.CrossCursor)
        self.raise_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    toolbar = Toolbar()
    toolbar.show()
    sys.exit(app.exec_())