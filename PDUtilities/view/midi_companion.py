from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QPushButton, QComboBox, QLabel, QLineEdit
from model.midi_companion import MidiCompanionModel
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = (os.path.join(current_dir, '..'))

class MidiCompanion(QWidget):
    # Type hints
    connectButton: QPushButton
    midiOutputComboBox: QComboBox
    midiInputComboBox: QComboBox
    midiMessageDebugLabel: QLabel
    midiConnectionStatus: QLabel
    IPLineEdit: QLineEdit

    def __init__(self, parent=None):
        super(MidiCompanion, self).__init__(parent)
        self.model = MidiCompanionModel()
        self.model.midi_msg_cb = self._midi_msg_callback
        self.model.connection_cb = self._connection_callback
        uic.loadUi(os.path.join(current_dir, '..', 'gui', 'midi_companion_layout.ui'), self)

        # Midi Companion Buttons
        self.connectButton.clicked.connect(self._connect_clicked)
        # self.midiInputComboBox.currentIndexChanged.connect(self._midi_input_index_changed)
        self.midiOutputComboBox.currentIndexChanged.connect(self._midi_output_index_changed)
        self.midiInputComboBox.addItems(self.model.midi_inputs)
        self.midiOutputComboBox.addItems(self.model.midi_outputs)
        
    def _connect_clicked(self):
        if self.model.connected_to_host:
            self.model.disconnect_from_host()
        else:
            self.model.connect_to_host(self.IPLineEdit.text())
        self.connectButton.setText("Disconnect" if self.model.connected_to_host else "Connect")

    def _midi_output_index_changed(self, index):
        print("index changed to " + str(index))
        self.model.midi_output_index = index

    # def _midi_input_index_changed(self, index):
        # self.model.midi_input_index = index

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

    def closeEvent(self, event):
        if self.model.connected_to_host:
            self.model.stopEvent.set()
            self.model.client_socket.close()
        event.accept()
    
    def get_save_data(self):
        return { "ip": self.IPLineEdit.text() }

    def load_saved_values(self, pdsave: dict):
        if "ip" in pdsave:
            self.IPLineEdit.setText(pdsave["ip"])