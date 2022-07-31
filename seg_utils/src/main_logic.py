from seg_utils.utils.database import SQLiteDatabase
from seg_utils.ui.main_window import LabelingMainWindow


class MainLogic:
    def __init__(self):

        # active elements
        self.main_window = LabelingMainWindow()
        self.database = SQLiteDatabase()
        self.connect_events()

        self.main_window.show()

    def connect_events(self):

        # main window -> database
        self.main_window.image_display.hide_button.clicked.connect(self.main_window.hide_toolbar)
        self.main_window.sSaveToDatabase.connect(self.database.save)
        self.main_window.sAddFile.connect(self.database.add_file)
        self.main_window.sAddPatient.connect(self.database.add_patient)
        self.main_window.sRequestUpdate.connect(self.database.update_gui)
        self.main_window.sDeleteFile.connect(self.database.delete_file)
        self.main_window.sUpdateSettings.connect(self.database.update_settings)

        # main window's menubar -> database
        self.main_window.menubar.sCreateNewProject.connect(self.database.initialize)
        self.main_window.menubar.sOpenProject.connect(self.database.initialize)
        self.main_window.menubar.sRequestImport.connect(self.database.send_import_info)
        self.main_window.menubar.sRequestSettings.connect(self.database.open_settings)

        # database -> main window
        self.database.sUpdate.connect(self.main_window.update_window)
        self.database.sImportFile.connect(self.main_window.import_file)
        self.database.sOpenSettings.connect(self.main_window.open_settings)
        self.database.sApplySettings.connect(self.main_window.apply_settings)
