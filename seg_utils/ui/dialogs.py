from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize, QPoint, Qt
from PyQt5.QtGui import QFont, QIcon

from seg_utils.ui.list_widget import ListWidget
from seg_utils.utils.qt import createListWidgetItemWithSquareIcon, getIcon

from pathlib import Path
import os

BUTTON_STYLESHEET = """QPushButton {
                        background-color: lightgray;
                        color: black;
                        min-height: 2em;
                        border-width: 2px;
                        border-radius: 8px;
                        border-color: black;
                        font: bold 12px;
                        padding: 2px;
                        }
                        QPushButton::hover {
                        background-color: gray;
                        }
                        QPushButton::pressed {
                        border-style: outset;
                        }"""


class NewLabelDialog(QDialog):
    def __init__(self, parent: QWidget, *args):
        super(NewLabelDialog, self).__init__(*args)

        # Default values
        self.class_name = ""
        self.parent = parent

        # Create the shape of the QDialog
        self.setFixedSize(QSize(300, 400))
        moveToCenter(self, self.parent.pos(), self.parent.size())
        self.setWindowTitle("Select class of new shape")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Textedit
        self.shapeSearch = QTextEdit(self)
        font = QFont()
        font.setPointSize(10)
        font.setKerning(True)
        self.shapeSearch.setFont(font)
        self.shapeSearch.setPlaceholderText("Search shape label")
        self.shapeSearch.setMaximumHeight(25)
        self.shapeSearch.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.shapeSearch.textChanged.connect(self.handle_shape_search)

        # Buttons
        buttonWidget = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonWidget.accepted.connect(self.close)
        buttonWidget.rejected.connect(self.on_cancel)

        # List of labels
        self.listWidget = ListWidget(self)
        self.listWidget.itemClicked.connect(self.on_ListSelection)

        # Combining everything
        layout.addWidget(self.shapeSearch)
        layout.addWidget(buttonWidget)
        layout.addWidget(self.listWidget)

        self.fill()

    def fill(self):
        """ get all the current label classes and display them in the dialog """
        self.listWidget.clear()
        for idx, _class in enumerate(self.parent.classes):
            item = createListWidgetItemWithSquareIcon(_class, self.parent.colorMap[idx], 10)
            self.listWidget.addItem(item)

        # last entry in the list is used for creating a new label_class
        item = QListWidgetItem(QIcon('icons/plus.png'), "New")
        self.listWidget.addItem(item)

    def handle_shape_search(self):
        """ If user enters text, only suitable shapes are displayed """
        text = self.shapeSearch.toPlainText()
        for item_idx in range(self.listWidget.count()):
            item = self.listWidget.item(item_idx)
            if text not in item.text():
                item.setHidden(True)
            else:
                item.setHidden(False)

    def on_ListSelection(self, item):
        """ handles the functions to be executed when user selects something from the list"""
        text = item.text()

        # let user enter a new label class
        if text == "New":
            create_new_class = CreateNewLabelClassDialog(self)
            create_new_class.exec()

            # if user entered a name, update the stored label classes
            if create_new_class.new_label_class:
                text = create_new_class.new_label_class
                idx = len(self.parent.classes)
                self.parent.classes[text] = idx
                self.fill()
                self.listWidget.item(self.listWidget.count() - 2).setSelected(True)  # highlight new item

            # otherwise, make sure that nothing is passed on
            else:
                text = ""
                self.listWidget.currentItem().setSelected(False)

        # use selected/created label class to name the label
        self.class_name = text

    def on_cancel(self):
        self.class_name = ""
        self.close()

    def setText(self, text):
        self.shapeSearch.setText(text)
        # move the cursor to the end
        newCursor = self.shapeSearch.textCursor()
        newCursor.movePosition(self.shapeSearch.document().characterCount())
        self.shapeSearch.setTextCursor(newCursor)


class ForgotToSaveMessageBox(QMessageBox):
    def __init__(self, *args):
        super(ForgotToSaveMessageBox, self).__init__(*args)

        saveButton = QPushButton(getIcon('save'), "Save Changes")
        dismissButton = QPushButton(self.style().standardIcon(QStyle.SP_DialogDiscardButton), "Dismiss Changes")
        cancelButton = QPushButton(self.style().standardIcon(QStyle.SP_DialogCancelButton), "Cancel")

        self.setWindowTitle("Caution: Unsaved Changes")
        self.setText("Unsaved Changes: How do you want to progress?")

        # NOTE FOR SOME REASON THE ORDER IS IMPORTANT DESPITE THE ROLE - IDK WHY
        self.addButton(saveButton, QMessageBox.AcceptRole)
        self.addButton(cancelButton, QMessageBox.RejectRole)
        self.addButton(dismissButton, QMessageBox.DestructiveRole)

        moveToCenter(self, self.parentWidget().pos(), self.parentWidget().size())
        
        
class DeleteShapeMessageBox(QMessageBox):
    def __init__(self, shape: str, *args):
        super(DeleteShapeMessageBox, self).__init__(*args)
        moveToCenter(self, self.parentWidget().pos(), self.parentWidget().size())
        reply = self.question(self, "Deleting Shape", f"You are about to delete {shape}. Continue?",
                      QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.answer = 1
        else:
            self.answer = 0


class CreateNewLabelClassDialog(QDialog):
    """ handles a QDialog used to let the user enter a new label class """
    def __init__(self, parent: NewLabelDialog):
        super(CreateNewLabelClassDialog, self).__init__()

        self.setFixedSize(QSize(200, 120))
        moveToCenter(self, parent.pos(), parent.size())
        self.setWindowTitle("Create new Shape class")

        # need it later to prevent duplicates
        self.new_label_class = ""
        self.existing_classes = parent.parent.classes

        # Textedit
        self.shapeText = QTextEdit(self)
        font = QFont()
        font.setPointSize(10)
        font.setKerning(True)
        self.shapeText.setFont(font)
        self.shapeText.setPlaceholderText("Enter new Shape name")
        self.shapeText.setMaximumHeight(25)

        # Buttons
        self.buttonWidget = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonWidget.accepted.connect(self.ok_clicked)
        self.buttonWidget.rejected.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(self.shapeText)
        layout.addWidget(self.buttonWidget)

    def ok_clicked(self):
        """ only accepts the new label class if
        (1) the name doesn't already exist and
        (2) the name is not an empty string"""
        name = self.shapeText.toPlainText()
        if name in self.existing_classes:
            self.shapeText.setText("")
            self.shapeText.setPlaceholderText("'{}' already exists".format(name))
        elif name:
            self.new_label_class = name
            self.close()


class SelectFileTypeDialog(QDialog):
    """
    handles a QDialog to let the user select between video, image and whole slide image
    the selected type is the used when importing a new file
    """
    def __init__(self):
        super(SelectFileTypeDialog, self).__init__()

        self.setFixedSize(QSize(250, 150))
        self.setWindowTitle("Select File Type")
        self.filetype = ""

        # create buttons and apply stylesheet
        v = QPushButton("Video")
        i = QPushButton("Image")
        w = QPushButton("Whole Slide Image")
        v.setStyleSheet(BUTTON_STYLESHEET)
        i.setStyleSheet(BUTTON_STYLESHEET)
        w.setStyleSheet(BUTTON_STYLESHEET)

        # TODO: Extend by other accepted types, substitute 'whatever' by actual WSI type
        v.clicked.connect(lambda: self.set_type("mp4"))
        i.clicked.connect(lambda: self.set_type("png"))
        w.clicked.connect(lambda: self.set_type("whatever"))

        ft_layout = QVBoxLayout(self)
        ft_layout.addWidget(v)
        ft_layout.addWidget(i)
        ft_layout.addWidget(w)

    def set_type(self, t: str):
        """ updates the class variable by the selected filetype"""
        self.filetype = t
        self.close()


class ProjectHandlerDialog(QDialog):
    def __init__(self, parent):
        super(ProjectHandlerDialog, self).__init__()
        self.setFixedSize(parent.size() / 2)
        self.setWindowTitle('Create new Project')

        self.project_path = ""
        self.files = list()

        # Header for LineEdit
        self.header = QLabel()
        self.header.setStyleSheet("font: bold 12px")
        self.header.setText("Choose Project Location")

        # LineEdit where user can enter a path
        self.enter_path = QLineEdit(self)
        self.enter_path.setFixedHeight(30)

        # suggestion for a project location
        suggestion = f"{Path.home()}{os.path.sep}AnnotationProjects{os.path.sep}project"
        for i in range(1, 100):
            if not os.path.exists(suggestion + str(i)):
                suggestion = suggestion + str(i)
                break
        self.enter_path.setText(suggestion)

        # button to open up a FileDialog
        self.select_path_button = QPushButton()
        self.select_path_button.setFixedSize(QSize(40, 30))
        self.select_path_button.setStyleSheet(BUTTON_STYLESHEET)
        self.select_path_button.setText('...')
        self.select_path_button.clicked.connect(self.select_path)

        # button to add initial files
        self.add_files_button = QPushButton()
        self.add_files_button.setFixedWidth(180)
        self.add_files_button.setStyleSheet(BUTTON_STYLESHEET)
        self.add_files_button.setText("Add files to get started")
        self.add_files_button.clicked.connect(self.add_files)

        # ListWidget to display added files
        self.added_files = QListWidget()

        # Accept & cancel buttons
        self.confirmation = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.confirmation.button(QDialogButtonBox.Ok).setText("Create Project")
        self.confirmation.accepted.connect(self.check_path)
        self.confirmation.rejected.connect(self.close)

        # layout setup
        self.header_frame = QFrame()
        self.header_layout = QHBoxLayout(self.header_frame)
        self.header_layout.setContentsMargins(10, 20, 10, 0)
        self.header_layout.addWidget(self.header)

        self.upper_row = QFrame()
        self.upper_row_layout = QHBoxLayout(self.upper_row)
        self.upper_row_layout.setContentsMargins(10, 0, 10, 0)
        self.upper_row_layout.addWidget(self.enter_path)
        self.upper_row_layout.addWidget(self.select_path_button)

        self.bottom = QFrame()
        self.bottom_layout = QVBoxLayout(self.bottom)
        self.bottom_layout.addWidget(self.add_files_button)
        self.bottom_layout.addWidget(self.added_files)
        self.bottom_layout.addWidget(self.confirmation)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.header_frame)
        self.layout.addWidget(self.upper_row)
        self.layout.addStretch(1)
        self.layout.addWidget(self.bottom)

    def add_files(self):
        """ function to let user select a file which will be added when the project is finally created"""

        # user first needs to specify the type of the file to be imported
        select_filetype = SelectFileTypeDialog()
        select_filetype.exec()

        if select_filetype.filetype:
            # TODO: implement smarter filetype recognition
            _filter = '*png *jpg *jpeg' if select_filetype.filetype == 'png' else select_filetype.filetype

            filepath, _ = QFileDialog.getOpenFileName(self,
                                                      caption="Select File",
                                                      directory=str(Path.home()),
                                                      filter="File ({})".format(_filter),
                                                      options=QFileDialog.DontUseNativeDialog)

            # only care about the filename itself (not regarding its path), to make it easier to handle
            filename = os.path.basename(filepath)
            if self.exists(filename):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("The file\n{}\nalready exists.\nOverwrite?".format(filename))
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg.accepted.connect(lambda: self.overwrite(filepath, filename))
                msg.exec()
            elif filename:
                # TODO: Implement possibility to add several files at once
                self.files.append(filepath)
                self.added_files.addItem(QListWidgetItem(filename))

    def check_path(self):
        """ this function verifies/rejects the project path which the user entered in the LineEdit"""
        project_path = self.enter_path.text()

        # check if user entered a non-empty directory
        if os.path.exists(project_path):
            content = os.listdir(project_path)
            if len(content) != 0:

                # confirmation dialog; directory will be cleared if user proceeds
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("The directory\n{}\nis not empty.".format(project_path))
                msg.setInformativeText("All existing files in that directory will be deleted.\nProceed?")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg.accepted.connect(lambda: self.create_project(project_path))
                msg.exec()
            else:
                self.project_path = project_path
                self.close()

        # if user entered a valid absolute path, create the project
        elif os.path.isabs(project_path):
            self.project_path = project_path
            self.close()

        # else do nothing
        else:
            msg = QMessageBox()
            msg.setText("Please enter a valid project location.")
            msg.exec()

    def create_project(self, project_path: str):
        """This function stores a valid path as class variable and closes the dialog"""
        self.project_path = project_path
        self.close()

    def exists(self, filename: str):
        """ check if a filename is already in the list
        also prevents name clashes when two files from different paths have the same name"""
        for i in range(self.added_files.count()):
            cur = self.added_files.item(i).text()
            if cur == filename:
                return True
        return False

    def overwrite(self, filepath, filename):
        """overwrites an existing file in the file list"""

        # find and delete the corresponding item in the files list
        for fn in self.files:
            cur = os.path.basename(fn)
            if cur == filename:
                self.files.remove(fn)
                break

        # append the new filepath
        self.files.append(filepath)

    def select_path(self):
        """opens a dialog to let the user select a directory from its OS """

        # dialog to select a directory in the user's environment
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.DontUseNativeDialog)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setDirectory(str(Path.home()))

        # store selected path in the LineEdit
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            self.enter_path.setText(filename)


class CommentDialog(QDialog):
    """QDialog to let the user enter notes regarding a specific annotation"""

    def __init__(self, comment: str):
        super(CommentDialog, self).__init__()
        self.setWindowTitle("Notes")
        self.setFixedSize(500, 300)
        self.comment = comment

        # TextEdit where user can enter a comment
        self.enter_comment = QTextEdit(self)
        self.enter_comment.setText(self.comment)

        # Accept & cancel buttons
        self.confirmation = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.confirmation.accepted.connect(self.create_comment)
        self.confirmation.rejected.connect(self.close)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.enter_comment)
        self.layout.addWidget(self.confirmation)

    def create_comment(self):
        """stores the written notes in the class variable and closes the dialog"""
        self.comment = self.enter_comment.toPlainText()
        self.close()


def moveToCenter(widget, parent_pos: QPoint, parent_size: QSize):
    r"""Moves the QDialog to the center of the parent Widget.
    As self.move moves the upper left corner to the place, one needs to subtract the own size of the window"""
    widget.move(parent_pos.x() + (parent_size.width() - widget.size().width())/2,
                parent_pos.y() + (parent_size.height() - widget.size().height())/2)