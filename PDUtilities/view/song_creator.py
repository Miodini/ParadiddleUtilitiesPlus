from PyQt6 import uic
from PyQt6.QtWidgets import QComboBox, QWidget, QPushButton, QFileDialog, QLineEdit, QTextEdit, QLabel
from model.song_creator import SongCreatorModel
import os
import yaml

current_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = (os.path.join(current_dir, '..'))

class SongCreator(QWidget):
    # Type hints
    complexityComboBox: QComboBox
    difficultyComboBox: QComboBox
    midiTrackComboBox: QComboBox
    convertButton: QPushButton
    selectCoverImageButton: QPushButton
    selectDrumSetButton: QPushButton
    selectMidiButton: QPushButton
    selectMidiMappingButton: QPushButton
    setOutputButton: QPushButton
    artistNameLineEdit: QLineEdit
    authorNameLineEdit: QLineEdit
    coverImageLineEdit: QLineEdit
    drumSetLineEdit: QLineEdit
    midiFileLineEdit: QLineEdit
    midiMappingLineEdit: QLineEdit
    songNameLineEdit: QLineEdit
    descriptionTextEdit: QTextEdit
    statusLabel: QLabel

    def __init__(self, parent=None):
        super(SongCreator, self).__init__(parent)
        self.model = SongCreatorModel()
        uic.loadUi(os.path.join(current_dir, '..', 'gui', 'song_creator_layout.ui'), self)

        # Signal connections
        self.selectMidiButton.clicked.connect(self._select_midi_clicked)
        self.selectMidiMappingButton.clicked.connect(self._select_midi_map_clicked)
        self.selectDrumSetButton.clicked.connect(self._select_drum_set_clicked)
        self.convertButton.clicked.connect(self._convert_clicked)
        self.setOutputButton.clicked.connect(self._set_output_clicked)
        self.selectCoverImageButton.clicked.connect(self._select_cover_image_clicked)
        self.midiTrackComboBox.currentIndexChanged.connect(self._midi_track_index_changed)
        self.difficultyComboBox.currentTextChanged.connect(self._difficulty_text_changed)
        self.complexityComboBox.currentTextChanged.connect(self._complexity_text_changed)

        # TODO: May not be an issue, but try to see if there is a better way of doing things
        for i in range(5):
            songTrackBtn: QPushButton = getattr(self, ('selectSongTrackButton_' + str(i+1)), None)
            drumTrackBtn: QPushButton = getattr(self, ('selectDrumTrackButton_' + str(i+1)), None)
            if drumTrackBtn:
                drumTrackBtn.clicked.connect(self._select_audio_file_clicked)
            if songTrackBtn:
                songTrackBtn.clicked.connect(self._select_audio_file_clicked)

        self.hide()

    def _select_midi_clicked(self):
        self.midiTrackComboBox.clear()
        self.model.midi_file = QFileDialog.getOpenFileName(self, ("Select Midi File"), self.model.last_open_folder, ("Midi Files (*.mid *.midi *.kar)"))[0]
        
        if self.model.midi_file:
            self.model.is_modified = True
            default_index = self.model.get_default_midi_track()
            self.model.last_open_folder = self.model.midi_file.rsplit('/', 1)[0]
            self.midiFileLineEdit.setText(self.model.midi_file.split('/')[-1])
            for i in range(len(self.model.midi_track_names)):
                item_name = 'Track ' + str(i) + ': ' + self.model.midi_track_names[i]
                if i >= (self.midiTrackComboBox.count()):
                    self.midiTrackComboBox.addItem(item_name)
                else:
                    self.midiTrackComboBox.setItemText(i,item_name)
            self.model.convert_track_index = default_index
            print("Convert track index: " + str(self.model.convert_track_index))
            self.midiTrackComboBox.setCurrentIndex(self.model.convert_track_index)

    def _select_midi_map_clicked(self):
        file_name = QFileDialog.getOpenFileName(self, ("Select Midi File"), self.model.drum_mapping_file, ("Midi Map (*.yaml *yml)"))[0]

        if file_name:
            self.model.is_modified = True
            self.model.drum_mapping_file = file_name
            with open(file_name) as file:
                midi_yaml_dict = yaml.load(file, Loader=yaml.FullLoader)
                self.model.create_midi_map(midi_yaml_dict)
                self.midiMappingLineEdit.setText(file_name.split('/')[-1])
        
    def _set_output_clicked(self):
        output_folder = QFileDialog.getExistingDirectory(self, ("Select Folder"), self.model.output_rlrr_dir)
        if output_folder:
            self.model.is_modified = True
            self.model.output_rlrr_dir = output_folder

    def _select_drum_set_clicked(self):
        file_name = QFileDialog.getOpenFileName(self, ("Select Drum Set File"), self.model.drum_set_file, ("PD Drum Set Files (*.rlrr)"))[0]

        if file_name:
            self.model.is_modified = True
            self.model.drum_set_file = file_name
            self.model.analyze_drum_set(file_name)
            self.model.last_open_folder = file_name.rsplit('/', 1)[0]
            self.drumSetLineEdit.setText(file_name.split('/')[-1])

    def _select_audio_file_clicked(self):
        sender_name = self.sender().objectName()
        is_drum_track = "Drum" in sender_name
        track_index = int(sender_name.split('_')[-1]) - 1
        audio_file = QFileDialog.getOpenFileName(self, ("Select Audio File"), self.model.last_open_folder, ("Audio Files (*.mp3 *.wav *.ogg)"))[0]

        if audio_file:
            self.model.is_modified = True
            if is_drum_track:
                self.model.drum_tracks[track_index] = audio_file
                print(self.model.drum_tracks)
            else:
                self.model.song_tracks[track_index] = audio_file
                print(self.model.song_tracks)

            self.model.last_open_folder = audio_file.rsplit('/', 1)[0]
            line_edit = getattr(self, ('drum' if is_drum_track else 'song') + 'TrackLineEdit_' + str(track_index+1))
            print(line_edit)
            line_edit.setText(audio_file.split('/')[-1])

    def _select_cover_image_clicked(self):
        self.model.cover_image_path = QFileDialog.getOpenFileName(self, ("Select Cover Image"), self.model.last_open_folder, ("Image Files (*.png *.jpg *.jpeg)"))[0]
        if self.model.cover_image_path:
            self.model.is_modified = True
            self.model.last_open_folder = self.model.cover_image_path.rsplit('/', 1)[0]
            self.coverImageLineEdit.setText(self.model.cover_image_path.split('/')[-1])

    def _convert_clicked(self):
        self.model.song_name = self.songNameLineEdit.text()
        # TODO check if we need to escape the \n newline characters ('\n' to '\\n')
        self.statusLabel.setText("Converting...")
        self.statusLabel.repaint()
        self.model.recording_description = self.descriptionTextEdit.toPlainText() 
        self.model.artist_name = self.artistNameLineEdit.text()
        self.model.author_name = self.authorNameLineEdit.text()
        if self.model.convert_to_rlrr():
            self.statusLabel.setText("Conversion successful!")

    def _difficulty_text_changed(self, text):
        self.model.is_modified = True
        self.model.difficulty = text

    def _complexity_text_changed(self, text):
        self.model.is_modified = True
        self.model.song_complexity = int(text)

    def _midi_track_index_changed(self, index):
        self.model.is_modified = True
        self.model.convert_track_index = index

    def get_save_data(self):
        return {
            "drumSetFile": self.model.drum_set_file,
            "drumMappingFile": self.model.drum_mapping_file,
            "outputRlrrDir": self.model.output_rlrr_dir
        }
    
        
    def load_saved_values(self, pdsave: dict):
        # Initializes the paths with the saved or the default values
        default_set_file = os.path.join(project_dir, "drum_sets", "defaultset.rlrr")
        default_drum_mapping_file = os.path.join(project_dir, 'midi_maps', 'pdtracks_mapping.yaml')
        default_output_dir = os.path.join(project_dir, "rlrr_files")

        # Create the default output folder if it does not exist
        if not os.path.exists(default_output_dir):
            os.makedirs(default_output_dir)

        if "drumSetFile" in pdsave and os.path.exists(pdsave["drumSetFile"]):
            self.model.drum_set_file = pdsave["drumSetFile"] 
        else:
            self.model.drum_set_file = default_set_file

        if "drumMappingFile" in pdsave and os.path.exists(pdsave["drumMappingFile"]):
            self.model.drum_mapping_file = pdsave["drumMappingFile"]
        else:
            self.model.drum_mapping_file = default_drum_mapping_file

        if "outputRlrrDir" in pdsave and os.path.exists(pdsave["outputRlrrDir"]):
            self.model.output_rlrr_dir = pdsave["outputRlrrDir"]
        else:
            self.model.output_rlrr_dir = default_output_dir

        self.drumSetLineEdit.setText(os.path.basename(self.model.drum_set_file))
        self.midiMappingLineEdit.setText(os.path.basename(self.model.drum_mapping_file))
        self.model.analyze_drum_set(self.model.drum_set_file)

        # Sets the last open folder to drum_sets directory
        self.model.last_open_folder = os.path.dirname(self.model.drum_set_file)

        with open(self.model.drum_mapping_file) as file:
            midi_yaml_dict = yaml.load(file, Loader=yaml.FullLoader)
            self.model.create_midi_map(midi_yaml_dict)
