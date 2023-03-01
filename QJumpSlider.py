from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSlider, QStyle, QStyleOptionSlider, QFormLayout, QWidget, QApplication


class QJumpSlider(QSlider):
    def mousePressEvent(self, event):
        super(QJumpSlider, self).mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            val = self.pixelPosToRangeValue(event.pos())
            self.setValue(val)

    def pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
                                               sliderMax - sliderMin, opt.upsideDown)
        


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    w = QWidget()
    flay = QFormLayout(w)
    w1 = QSlider(Qt.Horizontal)
    w2 = QJumpSlider(Qt.Horizontal)
    flay.addRow("default: ", w1)
    flay.addRow("modified: ", w2)
    w.show()
    sys.exit(app.exec_())