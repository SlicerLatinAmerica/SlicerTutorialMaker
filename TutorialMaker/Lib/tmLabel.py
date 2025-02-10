import qt

class tmLabel(qt.QLabel):
    clicked = qt.Signal()

    def __init__(self, text, index, parent=None):
        super().__init__(text, parent)
        self.index = index

    def mousePressEvent(self, event):
        self.clicked.emit()
