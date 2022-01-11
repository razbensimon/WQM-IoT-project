import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
from datetime import datetime
from mqtt_init import *
import json
from icecream import ic

# from PyQt5.QtCore import QTimer

global current_turbidity, current_ph_value, current_hardness_value
r = random.randrange(1, 10000000)
update_rate = 5000  # in msec


# Creating Client name - should be unique
def generate_client_id(device_id):
    return "IOT_client-WQM-Id" + device_id + '-' + str(r)


def generate_topic(device_id):
    return topic_prefix + '/' + device_id + '/sts'


def generate_alarm_topic(device_id, sensor):
    return generate_topic(device_id) + '/alarm/' + sensor


def display_number(num):
    return format(num, '.2f')


class Mqtt_client():
    def __init__(self):
        # broker IP adress:
        self.broker = ''
        self.topic = ''
        self.port = ''
        self.clientname = ''
        self.username = ''
        self.password = ''
        self.subscribeTopic = ''
        self.publishTopic = ''
        self.publishMessage = ''
        self.on_connected_to_form = ''
        self.on_disconnected_to_form = ''
        self.CONNECTED = False

    # Setters and getters
    def set_on_connected_to_form(self, on_connected_to_form):
        self.on_connected_to_form = on_connected_to_form

    def set_on_disconnected_to_form(self, on_disconnected_to_form):
        self.on_disconnected_to_form = on_disconnected_to_form

    def get_broker(self):
        return self.broker

    def set_broker(self, value):
        self.broker = value

    def get_port(self):
        return self.port

    def set_port(self, value):
        self.port = value

    def get_clientName(self):
        return self.clientName

    def set_clientName(self, value):
        self.clientName = value

    def get_username(self):
        return self.username

    def set_username(self, value):
        self.username = value

    def get_password(self):
        return self.password

    def set_password(self, value):
        self.password = value

    def get_subscribeTopic(self):
        return self.subscribeTopic

    def set_subscribeTopic(self, value):
        self.subscribeTopic = value

    def get_publishTopic(self):
        return self.publishTopic

    def set_publishTopic(self, value):
        self.publishTopic = value

    def get_publishMessage(self):
        return self.publishMessage

    def set_publishMessage(self, value):
        self.publishMessage = value

    def on_log(self, client, userdata, level, buf):
        print("log: " + buf)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
            self.CONNECTED = True
            self.on_connected_to_form()
        else:
            print("Bad connection Returned code=", rc)

    def on_disconnect(self, client, userdata, flags, rc=0):
        self.CONNECTED = False
        self.on_disconnected_to_form()
        print("DisConnected result code " + str(rc))

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        print("message from:" + topic, m_decode)
        mainwin.subscribeDock.update_mess_win(m_decode)

    def connect_to(self):
        # Init paho mqtt client class
        self.client = mqtt.Client(self.clientName, clean_session=True)  # create new client instance
        self.client.on_connect = self.on_connect  # bind call back function
        self.client.on_disconnect = self.on_disconnect
        self.client.on_log = self.on_log
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.username, self.password)
        print("Connecting to broker ", self.broker)
        self.client.connect(self.broker, self.port)  # connect to broker

    def disconnect_from(self):
        self.client.disconnect()

    def is_connected(self):
        return self.CONNECTED

    def start_listening(self):
        self.client.loop_start()

    def stop_listening(self):
        self.client.loop_stop()

    def subscribe_to(self, topic):
        if self.CONNECTED:
            self.client.subscribe(topic)
        else:
            print("Can't subscribe. Connection should be established first")

    def publish_to(self, topic, message):
        if self.CONNECTED:
            self.client.publish(topic, message)
        else:
            print("Can't publish. Connection should be established first")


class ConnectionDock(QDockWidget):
    """Main """

    def __init__(self, mc):
        QDockWidget.__init__(self)

        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        self.mc.set_on_disconnected_to_form(self.on_disconnected)
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)

        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)

        self.eDeviceID = QLineEdit()
        self.eDeviceID.setText(device_id)  # just for init default mock

        self.eUserName = QLineEdit()
        self.eUserName.setText(username)

        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)

        self.eKeepAlive = QLineEdit()
        self.eKeepAlive.setValidator(QIntValidator())
        self.eKeepAlive.setText("60")

        self.eSSL = QCheckBox()

        self.eCleanSession = QCheckBox()
        self.eCleanSession.setChecked(True)

        self.eConnectBtn = QPushButton("Enable/Connect", self)
        self.eConnectBtn.setToolTip("click me to dis/connect")
        self.eConnectBtn.clicked.connect(self.on_button_connect_click)
        self.eConnectBtn.setStyleSheet("background-color: gray")

        self.Ph = QLineEdit()
        self.Ph.setText('')

        self.Turbidity = QLineEdit()
        self.Turbidity.setText('')

        self.Hardness = QLineEdit()
        self.Hardness.setText('')

        formLayot = QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectBtn)
        formLayot.addRow("Device Id", self.eDeviceID)
        formLayot.addRow("pH", self.Ph)
        formLayot.addRow("Turbidity(NTU)", self.Turbidity)
        formLayot.addRow("Hardness (mg/L)", self.Hardness)

        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)
        self.setWindowTitle("Connect")

    def on_connected(self):
        self.eConnectBtn.setStyleSheet("background-color: green")

    def on_disconnected(self):
        self.eConnectBtn.setStyleSheet("background-color: red")

    def on_button_connect_click(self):
        if self.mc.is_connected():
            print('disconnecting...')
            self.mc.stop_listening()
            self.mc.disconnect_from()
        else:
            print('connecting...')
            self.mc.set_broker(self.eHostInput.text())
            self.mc.set_port(int(self.ePort.text()))
            clientname = generate_client_id(self.eDeviceID.text())
            print('client name is ' + clientname)
            self.mc.set_clientName(clientname)
            self.mc.set_username(self.eUserName.text())
            self.mc.set_password(self.ePassword.text())
            self.mc.connect_to()
            self.mc.start_listening()


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # Init of Mqtt_client class
        self.mc = Mqtt_client()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(update_rate)  # in msec

        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)

        # set up main window
        self.setGeometry(30, 600, 300, 150)
        self.setWindowTitle('Water Quality')

        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)

        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)

    def update_data(self):
        if not self.mc.is_connected():
            print('not connected, dont send data')
            return

        ph_level = display_number(base_ph_value + random.randrange(0, 30) / 30)  # 0->1
        turbidity_level = display_number(base_turbidity + random.randrange(0, 30) / 60)  # 0->0.5
        hardness_level = display_number(base_hardness_value + random.randrange(0, 10))

        # re-render UI
        self.connectionDock.Ph.setText(ph_level)
        self.connectionDock.Turbidity.setText(turbidity_level)
        self.connectionDock.Hardness.setText(hardness_level)

        message = {"turbidity": float(turbidity_level), "hardness": float(hardness_level),
                   "ph": float(ph_level),
                   "time": datetime.now().isoformat()}

        self.send_data(message)
        self.send_alarms_if_needed(message)

    def send_data(self, message):
        # publish JSON with sensors data
        msg_json = json.dumps(message)
        topic = generate_topic(self.connectionDock.eDeviceID.text())
        ic(topic, message)
        self.mc.publish_to(topic, msg_json)

    def send_alarms_if_needed(self, message):
        validation_func_map = {"turbidity": self.should_alarm_turbidity, "hardness": self.should_alarm_hardness,
                               "ph": self.should_alarm_ph}
        for key, value in message.items():
            if key == 'time':
                continue
            should_alarm = validation_func_map.get(key)
            if should_alarm(value):
                alarm_topic = generate_alarm_topic(self.connectionDock.eDeviceID.text(), key)
                message = {"sensor": key, "alarmed_value": value, "time": datetime.now().isoformat()}
                msg_json = json.dumps(message)
                ic('ALARM 🚨', alarm_topic, message)
                self.mc.publish_to(alarm_topic, msg_json)

    def should_alarm_turbidity(self, value):
        return value > turbidity_max

    def should_alarm_ph(self, value):
        return value > ph_value_max or value < ph_value_min

    def should_alarm_hardness(self, value):
        return value > hardness_max


app = QApplication(sys.argv)
mainwin = MainWindow()
mainwin.show()
app.exec_()
