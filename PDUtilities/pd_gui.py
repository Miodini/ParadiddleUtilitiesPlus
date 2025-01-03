from PyQt6.QtGui import QIcon
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QFileDialog
from midiconvert import MidiConverter
from midicompanion import MidiCompanion
import yaml
import json
import os

project_dir = os.path.dirname(os.path.realpath(__file__))    

# Paradiddle GUI
class PD_GUI(QtWidgets.QMainWindow):
    def __init__(self):
        super(PD_GUI, self).__init__()
        self.mc = MidiConverter()
        self.midicompanion = MidiCompanion()
        self.midicompanion.midi_msg_cb = self._midi_msg_callback
        self.midicompanion.connection_cb = self._connection_callback
        self.lastOpenFolder = "."
        # Sets the window icon
        self.setWindowIcon(QIcon(os.path.join(project_dir, "assets", "favicon.ico")))

        # Loads the .ui file
        uic.loadUi(os.path.join(project_dir, "pd_gui_layout.ui"), self)
        self.songCreatorWidget.hide()

        # Midi Companion Buttons
        self.connectButton.clicked.connect(self._connect_clicked)
        # self.midiInputComboBox.currentIndexChanged.connect(self._midi_input_index_changed)
        self.midiOutputComboBox.currentIndexChanged.connect(self._midi_output_index_changed)
        self.midiInputComboBox.addItems(self.midicompanion.midi_inputs)
        self.midiOutputComboBox.addItems(self.midicompanion.midi_outputs)
        
        # Connecting the Button's frontend to the Button's backend
        # I.E: Everytime button is clicked, call function
        self.selectMidiButton.clicked.connect(self._select_midi_clicked)
        self.selectMidiMappingButton.clicked.connect(self._select_midi_map_clicked)
        self.selectDrumSetButton.clicked.connect(self._select_drum_set_clicked)
        self.convertButton.clicked.connect(self._convert_clicked)
        self.setOutputButton.clicked.connect(self._set_output_clicked)
        self.selectCoverImageButton.clicked.connect(self._select_cover_image_clicked)
        self.songCreatorButton.clicked.connect(self._song_creator_clicked)
        self.midiCompanionButton.clicked.connect(self._midi_companion_clicked)
        # self.selectDrumTrackButton_1.clicked.connect(self._select_audio_file_clicked)
        # self.calibrationSpinBox.valueChanged.connect(self._calibration_offset_changed)
        
        # TODO: May not be an issue, but try to see if there is a better way of doing things
        for i in range(5):
            songTrackBtn = getattr(self, ('selectSongTrackButton_' + str(i+1)), None)
            drumTrackBtn = getattr(self, ('selectDrumTrackButton_' + str(i+1)), None)
            if drumTrackBtn:
                drumTrackBtn.clicked.connect(self._select_audio_file_clicked)
            if songTrackBtn:
                songTrackBtn.clicked.connect(self._select_audio_file_clicked)
        
        self.midiTrackComboBox.currentIndexChanged.connect(self._midi_track_index_changed)
        self.difficultyComboBox.currentTextChanged.connect(self._difficulty_text_changed)
        self.complexityComboBox.currentTextChanged.connect(self._complexity_text_changed)
                
        self.load_default_files()
        self.show()
    
    def closeEvent(self, event):
        if self.midicompanion.connected_to_host:
            self.midicompanion.stopEvent.set()
            self.midicompanion.client_socket.close()
        
        # Save IP address and directories to json file
        with open(os.path.join(project_dir, "pdsave.json"), "w") as file:
            json.dump({
                "ip": self.IPLineEdit.text(),
                "drumSetFile": self.mc.drum_set_file,
                "drumMappingFile": self.mc.drum_mapping_file,
                "outputRlrrDir": self.mc.output_rlrr_dir
                }, file)

        event.accept()
 
    def load_default_files(self):
        # Initializes the paths with the saved or the default values
        default_set_file = os.path.join(project_dir, "drum_sets", "defaultset.rlrr")
        default_drum_mapping_file = os.path.join(project_dir, 'midi_maps', 'pdtracks_mapping.yaml')
        default_output_dir = os.path.join(project_dir, "rlrr_files")
        # Create the default output folder if it does not exist
        if not os.path.exists(default_output_dir):
            os.makedirs(default_output_dir)

        try:
            with open(os.path.join(project_dir, "pdsave.json")) as file:
                pdsave = json.load(file)
                if "ip" in pdsave:
                    self.IPLineEdit.setText(pdsave["ip"])

                if "drumSetFile" in pdsave and os.path.exists(pdsave["drumSetFile"]):
                    self.mc.drum_set_file = pdsave["drumSetFile"] 
                else:
                    self.mc.drum_set_file = default_set_file

                if "drumMappingFile" in pdsave and os.path.exists(pdsave["drumMappingFile"]):
                    self.mc.drum_mapping_file = pdsave["drumMappingFile"]
                else:
                    self.mc.drum_mapping_file = default_drum_mapping_file

                if "outputRlrrDir" in pdsave and os.path.exists(pdsave["outputRlrrDir"]):
                    self.mc.output_rlrr_dir = pdsave["outputRlrrDir"]
                else:
                    self.mc.output_rlrr_dir = default_output_dir
        except:
            self.mc.drum_set_file = default_set_file
            self.mc.drum_mapping_file = default_drum_mapping_file
            self.mc.output_rlrr_dir = default_output_dir
        finally:
            self.drumSetLineEdit.setText(os.path.basename(self.mc.drum_set_file))
            self.midiMappingLineEdit.setText(os.path.basename(self.mc.drum_mapping_file))

        self.mc.analyze_drum_set(self.mc.drum_set_file)
        
        # Sets the last open folder to drum_sets directory
        self.lastOpenFolder = os.path.dirname(self.mc.drum_set_file)
         
        with open(self.mc.drum_mapping_file) as file:
            midi_yaml_dict = yaml.load(file, Loader=yaml.FullLoader)
            self.mc.create_midi_map(midi_yaml_dict)

    # LOCAL GUI FUNCTIONS

    def _difficulty_text_changed(self, text):
        self.mc.difficulty = text

    def _complexity_text_changed(self, text):
        self.mc.song_complexity = int(text)

    def _select_midi_clicked(self):
        self.midiTrackComboBox.clear()
        self.mc.midi_file = QFileDialog.getOpenFileName(self, ("Select Midi File"), self.lastOpenFolder, ("Midi Files (*.mid *.midi *.kar)"))[0]
        
        if self.mc.midi_file:
            (default_track, default_index) = self.mc.get_default_midi_track()
            self.lastOpenFolder = self.mc.midi_file.rsplit('/', 1)[0]
            self.midiFileLineEdit.setText(self.mc.midi_file.split('/')[-1])
            for i in range(len(self.mc.midi_track_names)):
                item_name = 'Track ' + str(i) + ': ' + self.mc.midi_track_names[i]
                if i >= (self.midiTrackComboBox.count()):
                    self.midiTrackComboBox.addItem(item_name)
                else:
                    self.midiTrackComboBox.setItemText(i,item_name)
            self.mc.convert_track_index = default_index
            print("Convert track index: " + str(self.mc.convert_track_index))
            self.midiTrackComboBox.setCurrentIndex(self.mc.convert_track_index)

    def _select_midi_map_clicked(self):
        file_name = QFileDialog.getOpenFileName(self, ("Select Midi File"), self.mc.drum_mapping_file, ("Midi Map (*.yaml *yml)"))[0]

        if file_name:
            self.mc.drum_mapping_file = file_name
            with open(file_name) as file:
                midi_yaml_dict = yaml.load(file, Loader=yaml.FullLoader)
                self.mc.create_midi_map(midi_yaml_dict)
                self.midiMappingLineEdit.setText(file_name.split('/')[-1])
        
    def _set_output_clicked(self):
        output_folder = QFileDialog.getExistingDirectory(self, ("Select Folder"), self.mc.output_rlrr_dir)
        if output_folder:
            self.mc.output_rlrr_dir = output_folder

    def _midi_track_index_changed(self, index):
        self.mc.convert_track_index = index

    def _select_drum_set_clicked(self):
        file_name = QFileDialog.getOpenFileName(self, ("Select Drum Set File"), self.mc.drum_set_file, ("PD Drum Set Files (*.rlrr)"))[0]

        if file_name:
            self.mc.drum_set_file = file_name
            self.mc.analyze_drum_set(file_name)
            self.lastOpenFolder = file_name.rsplit('/', 1)[0]
            self.drumSetLineEdit.setText(file_name.split('/')[-1])

    def _select_audio_file_clicked(self):
        sender_name = self.sender().objectName()
        is_drum_track = "Drum" in sender_name
        track_index = int(sender_name.split('_')[-1]) - 1
        audio_file = QFileDialog.getOpenFileName(self, ("Select Audio File"), self.lastOpenFolder, ("Audio Files (*.mp3 *.wav *.ogg)"))[0]

        if audio_file:
            if is_drum_track:
                self.mc.drum_tracks[track_index] = audio_file
                print(self.mc.drum_tracks)
            else:
                self.mc.song_tracks[track_index] = audio_file
                print(self.mc.song_tracks)

            self.lastOpenFolder = audio_file.rsplit('/', 1)[0]
            line_edit = getattr(self, ('drum' if is_drum_track else 'song') + 'TrackLineEdit_' + str(track_index+1))
            print(line_edit)
            line_edit.setText(audio_file.split('/')[-1])

    def _select_cover_image_clicked(self):
        self.mc.cover_image_path = QFileDialog.getOpenFileName(self, ("Select Cover Image"), self.lastOpenFolder, ("Image Files (*.png *.jpg *.jpeg)"))[0]
        if self.mc.cover_image_path:
            self.lastOpenFolder = self.mc.cover_image_path.rsplit('/', 1)[0]
            self.coverImageLineEdit.setText(self.mc.cover_image_path.split('/')[-1])

    def _convert_clicked(self):
        self.mc.song_name = self.songNameLineEdit.text()
        # TODO check if we need to escape the \n newline characters ('\n' to '\\n')
        self.statusLabel.setText("Converting...")
        self.statusLabel.repaint()
        self.mc.recording_description = self.descriptionTextEdit.toPlainText() 
        self.mc.artist_name = self.artistNameLineEdit.text()
        self.mc.author_name = self.authorNameLineEdit.text()
        if self.mc.convert_to_rlrr():
            self.statusLabel.setText("Conversion successful!")

    def _connect_clicked(self):
        if self.midicompanion.connected_to_host:
            self.midicompanion.disconnect_from_host()
        else:
            self.midicompanion.connect_to_host(self.IPLineEdit.text())
        self.connectButton.setText("Disconnect" if self.midicompanion.connected_to_host else "Connect")

    def _midi_input_index_changed(self, index):
        self.midicompanion.midi_input_index = index

    def _midi_output_index_changed(self, index):
        print("index changed to " + str(index))
        self.midicompanion.midi_output_index = index

    def _midi_companion_clicked(self):
        self.midiCompanionWidget.show()
        self.songCreatorWidget.hide()

    def _song_creator_clicked(self):
        self.midiCompanionWidget.hide()
        self.songCreatorWidget.show()

    def _midi_msg_callback(self, msg):
        self.midiMessageDebugLabel.setText(msg)

    def _connection_callback(self, connected):
        self.midiConnectionStatus.setText("Connected" if connected else "Disconnected")
        # self.connectButton.setText("Disconnect" if connected else "Connect")
        # self.midiInputComboBox.setEnabled(not connected)
        # self.midiOutputComboBox.setEnabled(not connected)
        # self.IPLineEdit.setEnabled(not connected)
        # self.midiCompanionButton.setEnabled(not connected)
        # self.midiCompanionWidget.setEnabled(not connected)
        # self.midiCompanionWidget.hide()
        # self.songCreatorButton.setEnabled(not connected)
        # self.songCreatorWidget.setEnabled(not connected)
        # self.songCreatorWidget.hide()

    # def calibration_offset_changed(self):
    #     calibration_offset = self.calibrationSpinBox.value()