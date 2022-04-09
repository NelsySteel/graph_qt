from PyQt5.QtGui import QFont, QColor, QColorConstants, QPainter
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QRect, Qt


def ClampInt(n :int, min_n:int = 0, max_n:int = 1):
    return (max(min_n, min(max_n , n)))

#The simplest vector - i don't need anything else so didn't use anymore complex ones
class Vector2d:
    def __init__(self, x = 0, y = 0):
        self.x = int(x)
        self.y = int(y)

    def __add__(self, other):
        return Vector2d(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2d(self.x - other.x, self.y - other.y)
    
    def Clone(self):
        return Vector2d(self.x, self.y)


#Creates Qt error message on error)
def CreateWarningMessage(warning_message, details = ''):
    msg = QMessageBox()
    msg.setFont(QFont("Arial", 10))
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Error!")
    msg.setText(warning_message)
    msg.setInformativeText(details)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()

#draws text on screen
def DrawText(text: str, painter: QPainter, rect: QRect, flags, size = 8, color = QColorConstants.Black, ):
    painter.save()
    font = painter.font()
    font.setPointSize(size)
    painter.setFont(font)
    painter.setPen(color)

    painter.drawText(rect, flags, text)
    painter.restore()

#draws text in nice predefined semi-transparent frame
#didn't do any style settings here for time economy, just predefined style =)
def DrawTextFrame(message:str, mouse_pos:Vector2d, painter:QPainter = None):
    painter.save()
    width = 200
    height = 50

    #some offset to avoid intersection with mouse pointer
    hint_offset = Vector2d(10, 10)
    hint_pos = mouse_pos + hint_offset


    text_margin = Vector2d(5, 0)
    text_pos = hint_pos + text_margin

    hint_rect:QRect = QRect(hint_pos.x, hint_pos.y, width, height)
    text_rect:QRect = QRect(text_pos.x, text_pos.y, width - text_margin.x, height - text_margin.y)
    r = 200
    g = 200
    b = 200
    color =  QColor.fromRgbF(r/255, g / 255, b / 255, 0.5)
    painter.setBrush(color)
    painter.setPen(QColorConstants.Black)

    painter.drawRect(hint_rect)
    
    DrawText(message, painter, text_rect, Qt.AlignLeft | Qt.AlignVCenter)
    painter.restore()

