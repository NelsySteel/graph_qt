from Utils import *
from GraphObjects import *
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QEvent, QObject, QRectF, QTimer
import sys


class Example(QMainWindow):
    #constant hint settings
    hint_width = 400
    hint_height = 50
    hint_margin = 10
    hint_text = 'Double click to create node'

    def __init__(self):
        super().__init__()
        self.initUI()
        self.graph: Graph = Graph(self)
        self.current_mouse_pos: Vector2d = None
        QApplication.instance().installEventFilter(self)

        #binding input event functions to input processor
        self.mouseMoveEvent = self.ProcessGraphInput
        self.mousePressEvent = self.ProcessGraphInput
        self.mouseReleaseEvent = self.ProcessGraphInput
        self.mouseDoubleClickEvent = self.ProcessGraphInput

        self.timer=QTimer()
        self.timer.timeout.connect(self.updateFPSText)
        self.timer.start(1000)
    
        self.frameCount = 0
        self.previousFPS = -1
        self.fpsText = ''
        self.fpsPos = Vector2d(0,0)

    def updateFPSText(self):
        self.fpsText = 'FPS:' + str(self.frameCount)
        if self.previousFPS != self.frameCount: #just for the sake of beautiful "0" in top left corner))
            self.Refresh()
        self.frameCount = 0

    def initUI(self):
        self.setGeometry(300, 300, 900, 600)
        self.setMinimumSize(300, 300)
        self.setWindowTitle('Test')
        self.show()
        
    def DrawHint(self, painter:QPainter):
        hint_rect = QRectF(self.hint_margin, self.height() - self.hint_height, self.hint_width, self.hint_height)
        DrawText(self.hint_text, painter, hint_rect, Qt.AlignLeft | Qt.AlignBottom, 20, QColorConstants.DarkGray)

        if self.current_mouse_pos:
            self.graph.RenderHint(painter, self.current_mouse_pos)

    def DrawFPS(self, painter:QPainter):
        fps_rect = QRectF(self.fpsPos.x, self.fpsPos.y, self.hint_width, self.hint_height)
        DrawText(self.fpsText, painter, fps_rect, Qt.AlignLeft | Qt.AlignTop, 15, QColorConstants.DarkGray)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        self.graph.RenderGrid(qp)
        self.graph.Render(qp)
        self.DrawFPS(qp)
        self.DrawHint(qp)

        qp.end()

    def ProcessGraphInput(self, event: QMouseEvent):
        if self.graph.ProcessInput(event):
            self.Refresh()
            
    def Refresh(self):
        self.frameCount+=1
        self.update()
    
    def eventFilter(self, source: QObject, event: QEvent) -> bool:
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
                    self.Refresh()
        if event.type() == QEvent.KeyRelease:
            if event.text() == 'q':
                self.graph.FillWindow()

        return super().eventFilter(source, event)
    

def main():

    app = QApplication(sys.argv)
    ex = Example()
    ex.update()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()