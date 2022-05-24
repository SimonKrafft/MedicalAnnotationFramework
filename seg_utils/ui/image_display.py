from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from seg_utils.ui.image_viewer import ImageViewer
from seg_utils.ui.annotation_group import AnnotationGroup
from seg_utils.utils.qt import get_icon


class CenterDisplayWidget(QWidget):
    """ widget to manage the central display in the GUI
    controls a QGraphicsView and a QGraphicsScene for drawing on top of a pixmap """

    sRequestLabelListUpdate = pyqtSignal(int)
    CREATE, EDIT = 0, 1

    def __init__(self, *args):
        super(CenterDisplayWidget, self).__init__(*args)

        # main components of the display
        self.scene = QGraphicsScene()
        self.image_viewer = ImageViewer(self.scene)

        self.pixmap = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap)
        self.annotations = AnnotationGroup()
        self.scene.addItem(self.annotations)

        self.image_size = QSize()

        self.hide_button = QPushButton(get_icon("next"), "", self)
        self.hide_button.setGeometry(0, 0, 40, 40)

        # put the viewer in the ImageDisplay-Frame
        self.image_viewer.setFrameShape(QFrame.NoFrame)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.image_viewer)

    def mousePressEvent(self, event: QMouseEvent):
        # TODO: add the drawing mode control. right now this will create a new shape on every click
        self.annotations.create_shape()
        event.accept()

    def clear(self):
        """This function deletes all currently stored labels
        and triggers the image_viewer to display a default image"""
        self.scene.b_isInitialized = False
        self.image_viewer.b_isEmpty = True
        self.scene.clear()
        self.set_labels([])

    def get_pixmap_dimensions(self):
        return [self.pixmap.pixmap().width(), self.pixmap.pixmap().height()]

    def init_image(self, filepath: str, labels):
        pixmap = QPixmap(filepath)
        self.image_size = pixmap.size()
        self.pixmap.setPixmap(pixmap)
        # self.set_labels(labels)
        self.hide_button.raise_()

    def is_empty(self):
        return self.image_viewer.b_isEmpty

    def set_initialized(self):
        self.scene.b_isInitialized = True
        self.image_viewer.b_isEmpty = False

    def set_mode(self, mode: int):
        assert mode in [self.CREATE, self.EDIT]
        self.scene.mode = mode
