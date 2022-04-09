from Utils import *
from GraphObjects import *
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QEvent, QObject, QRectF
import sys


class Example(QMainWindow):
    #constant hint settings
    hint_width = 400
    hint_height = 50
    hint_margin = 10
    hint_text = 'Double click to create node'

    def __init__(self):
        super().__init__()
        self.graph: Graph = Graph(self)
        self.initUI()
        self.current_mouse_pos: Vector2d = None
        QApplication.instance().installEventFilter(self)

    def initUI(self):
        self.setGeometry(300, 300, 900, 600)
        self.setMinimumSize(300, 300)
        self.setWindowTitle('Test')
        self.show()
        
    def DrawHint(self, painter:QPainter):
        hint_rect = QRectF(self.hint_margin, self.height() - self.hint_height, self.hint_width, self.hint_height)
        DrawText(self.hint_text, painter, hint_rect, Qt.AlignLeft | Qt.AlignBottom, 20, QColorConstants.DarkGray)

        self.graph.RenderHint(painter, self.current_mouse_pos)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        self.graph.Render(qp)
        self.DrawHint(qp)

        qp.end()

    def ProcessGraphInput(self, event):
        if self.graph.ProcessInput(event):
            self.update()

    # If this events are transferred to eventFilter then events become doubled 
    # because of 'update' or 'repaint' (no matter what you use). 
    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        self.ProcessGraphInput(e)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        self.ProcessGraphInput(e)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self.ProcessGraphInput(e)

    def mouseDoubleClickEvent(self, e: QMouseEvent) -> None:
        self.ProcessGraphInput(e)

    def eventFilter(self, source: 'QObject', event: 'QEvent') -> bool:
        if event.type() == QEvent.MouseMove:
            if event.button() == Qt.MouseButton.NoButton:
                #any other events implemented here will result indoubling events because of 'update' or 'repaint'
                #this one is safe though
                pos = event.pos()
                
                #check for update or previous mouse position to update when mouse leaves figure area
                #this way there is one more update to remove hint
                graph_needs_update = self.graph.GetObjectUnderMouse(self.current_mouse_pos)

                self.current_mouse_pos = Vector2d(pos.x(), pos.y())
                if graph_needs_update:
                    self.update()
        return super().eventFilter(source, event)
    

def main():

    app = QApplication(sys.argv)
    ex = Example()
    ex.update()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()