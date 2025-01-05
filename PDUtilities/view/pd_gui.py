from PyQt6 import uic
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMainWindow, QWidget, QPushButton
from view.song_creator import SongCreator
from view.midi_companion import MidiCompanion
import json
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = (os.path.join(current_dir, '..'))

# Paradiddle GUI
class PD_GUI(QMainWindow):
    # Type hints
    centralwidget: QWidget
    midiCompanionButton: QPushButton
    songCreatorButton: QPushButton
    actionNew: QAction
    actionOpen: QAction

    def __init__(self):
        super(PD_GUI, self).__init__()
        uic.loadUi(os.path.join(current_dir, '..', 'gui', 'pd_gui_layout.ui'), self)
        self.song_creator = SongCreator(self.centralwidget)
        self.midi_companion = MidiCompanion(self.centralwidget)

        # Sets the window icon
        self.setWindowIcon(QIcon(os.path.join(project_dir, "assets", "favicon.ico")))

        self.songCreatorButton.clicked.connect(self._song_creator_clicked)
        self.midiCompanionButton.clicked.connect(self._midi_companion_clicked)
        # self.selectDrumTrackButton_1.clicked.connect(self._select_audio_file_clicked)
        # self.calibrationSpinBox.valueChanged.connect(self._calibration_offset_changed)

        # Disabled on MIDI Companion section
        self.actionNew.setDisabled(True)
        self.actionOpen.setDisabled(True)

        self.load_default_files()
        self.show()
    
    def closeEvent(self, event):
        # Save IP address and directories to json file
        mc_save_data = self.midi_companion.get_save_data()
        sc_save_data = self.song_creator.get_save_data()
        with open(os.path.join(project_dir, "pdsave.json"), "w") as file:
            json.dump(mc_save_data | sc_save_data, file)

        event.accept()
 
    def load_default_files(self):
        try:
            with open(os.path.join(project_dir, "pdsave.json")) as file:
                pdsave = json.load(file)
                self.midi_companion.load_saved_values(pdsave)
                self.song_creator.load_saved_values(pdsave)
        except:
            # Will load with the default values
            self.song_creator.load_saved_values({})

    def _midi_companion_clicked(self):
        self.actionNew.setDisabled(True)
        self.actionOpen.setDisabled(True)
        self.midi_companion.show()
        self.song_creator.hide()

    def _song_creator_clicked(self):
        self.actionNew.setDisabled(False)
        self.actionOpen.setDisabled(False)
        self.midi_companion.hide()
        self.song_creator.show()