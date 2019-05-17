# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\denni\Documents\LabelingApp\project\gui\designer_gui_3.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(693, 714)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter_main = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_main.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_main.setObjectName("splitter_main")
        self.verticalLayout_data = QtWidgets.QFrame(self.splitter_main)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalLayout_data.sizePolicy().hasHeightForWidth())
        self.verticalLayout_data.setSizePolicy(sizePolicy)
        self.verticalLayout_data.setObjectName("verticalLayout_data")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayout_data)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mediaPlayer = QMediaPlayer(self.verticalLayout_data)
        self.mediaPlayer.setObjectName("mediaPlayer")
        # self.verticalLayout.addWidget(self.mediaPlayer)
        self.splitter_data = QtWidgets.QSplitter(self.verticalLayout_data)
        self.splitter_data.setOrientation(QtCore.Qt.Vertical)
        self.splitter_data.setChildrenCollapsible(False)
        self.splitter_data.setObjectName("splitter_data")
        self.widget = QtWidgets.QWidget(self.splitter_data)
        self.widget.setObjectName("widget")
        self.verticalLayout_video_player = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_video_player.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_video_player.setObjectName("verticalLayout_video_player")
        self.label_video = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_video.setFont(font)
        self.label_video.setAlignment(QtCore.Qt.AlignCenter)
        self.label_video.setObjectName("label_video")
        self.verticalLayout_video_player.addWidget(self.label_video)
        self.videoWidget_player = QVideoWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.videoWidget_player.sizePolicy().hasHeightForWidth())
        self.videoWidget_player.setSizePolicy(sizePolicy)
        self.videoWidget_player.setObjectName("videoWidget_player")
        self.verticalLayout_video_player.addWidget(self.videoWidget_player)
        self.horizontalLayout_media_control = QtWidgets.QHBoxLayout()
        self.horizontalLayout_media_control.setObjectName("horizontalLayout_media_control")
        self.pushButton_play = QtWidgets.QPushButton(self.widget)
        self.pushButton_play.setText("")
        self.pushButton_play.setObjectName("pushButton_play")
        self.horizontalLayout_media_control.addWidget(self.pushButton_play)
        self.horizontalSlider_time = QtWidgets.QSlider(self.widget)
        self.horizontalSlider_time.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_time.setObjectName("horizontalSlider_time")
        self.horizontalLayout_media_control.addWidget(self.horizontalSlider_time)
        self.label_duration = QtWidgets.QLabel(self.widget)
        self.label_duration.setObjectName("label_duration")
        self.horizontalLayout_media_control.addWidget(self.label_duration)
        self.verticalLayout_video_player.addLayout(self.horizontalLayout_media_control)
        self.widget1 = QtWidgets.QWidget(self.splitter_data)
        self.widget1.setObjectName("widget1")
        self.verticalLayout_sensor_data = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout_sensor_data.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_sensor_data.setObjectName("verticalLayout_sensor_data")
        self.label_sensor_data = QtWidgets.QLabel(self.widget1)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_sensor_data.setFont(font)
        self.label_sensor_data.setAlignment(QtCore.Qt.AlignCenter)
        self.label_sensor_data.setObjectName("label_sensor_data")
        self.verticalLayout_sensor_data.addWidget(self.label_sensor_data)
        self.verticalLayout_plot = QtWidgets.QVBoxLayout()
        self.verticalLayout_plot.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout_plot.setObjectName("verticalLayout_plot")
        self.verticalLayout_sensor_data.addLayout(self.verticalLayout_plot)
        self.verticalLayout.addWidget(self.splitter_data)
        self.widget2 = QtWidgets.QWidget(self.splitter_main)
        self.widget2.setObjectName("widget2")
        self.verticalLayout_settings = QtWidgets.QVBoxLayout(self.widget2)
        self.verticalLayout_settings.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_settings.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_settings.setObjectName("verticalLayout_settings")
        self.label_date_title = QtWidgets.QLabel(self.widget2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_date_title.setFont(font)
        self.label_date_title.setObjectName("label_date_title")
        self.verticalLayout_settings.addWidget(self.label_date_title)
        self.label_date = QtWidgets.QLabel(self.widget2)
        self.label_date.setText("")
        self.label_date.setObjectName("label_date")
        self.verticalLayout_settings.addWidget(self.label_date)
        self.label_time_title = QtWidgets.QLabel(self.widget2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_time_title.setFont(font)
        self.label_time_title.setObjectName("label_time_title")
        self.verticalLayout_settings.addWidget(self.label_time_title)
        self.label_time = QtWidgets.QLabel(self.widget2)
        self.label_time.setText("")
        self.label_time.setObjectName("label_time")
        self.verticalLayout_settings.addWidget(self.label_time)
        self.label_camera_id = QtWidgets.QLabel(self.widget2)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_camera_id.setFont(font)
        self.label_camera_id.setTextFormat(QtCore.Qt.AutoText)
        self.label_camera_id.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label_camera_id.setObjectName("label_camera_id")
        self.verticalLayout_settings.addWidget(self.label_camera_id)
        self.comboBox_camera_ids = QtWidgets.QComboBox(self.widget2)
        self.comboBox_camera_ids.setObjectName("comboBox_camera_ids")
        self.verticalLayout_settings.addWidget(self.comboBox_camera_ids)
        self.label_new_camera = QtWidgets.QLabel(self.widget2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_new_camera.sizePolicy().hasHeightForWidth())
        self.label_new_camera.setSizePolicy(sizePolicy)
        self.label_new_camera.setObjectName("label_new_camera")
        self.verticalLayout_settings.addWidget(self.label_new_camera)
        self.horizontalLayout_new_camera = QtWidgets.QHBoxLayout()
        self.horizontalLayout_new_camera.setObjectName("horizontalLayout_new_camera")
        self.lineEdit_new_camera = QtWidgets.QLineEdit(self.widget2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_new_camera.sizePolicy().hasHeightForWidth())
        self.lineEdit_new_camera.setSizePolicy(sizePolicy)
        self.lineEdit_new_camera.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lineEdit_new_camera.setObjectName("lineEdit_new_camera")
        self.horizontalLayout_new_camera.addWidget(self.lineEdit_new_camera)
        self.pushButton_add = QtWidgets.QPushButton(self.widget2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_add.sizePolicy().hasHeightForWidth())
        self.pushButton_add.setSizePolicy(sizePolicy)
        self.pushButton_add.setIconSize(QtCore.QSize(16, 16))
        self.pushButton_add.setShortcut("")
        self.pushButton_add.setObjectName("pushButton_add")
        self.horizontalLayout_new_camera.addWidget(self.pushButton_add)
        self.verticalLayout_settings.addLayout(self.horizontalLayout_new_camera)
        self.horizontalLayout_video_offset = QtWidgets.QHBoxLayout()
        self.horizontalLayout_video_offset.setObjectName("horizontalLayout_video_offset")
        self.label_video_offset = QtWidgets.QLabel(self.widget2)
        self.label_video_offset.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_video_offset.setObjectName("label_video_offset")
        self.horizontalLayout_video_offset.addWidget(self.label_video_offset)
        self.doubleSpinBox_video_offset = QtWidgets.QDoubleSpinBox(self.widget2)
        self.doubleSpinBox_video_offset.setMinimumSize(QtCore.QSize(70, 0))
        self.doubleSpinBox_video_offset.setObjectName("doubleSpinBox_video_offset")
        self.horizontalLayout_video_offset.addWidget(self.doubleSpinBox_video_offset)
        self.verticalLayout_settings.addLayout(self.horizontalLayout_video_offset)
        self.horizontalLayout_speed = QtWidgets.QHBoxLayout()
        self.horizontalLayout_speed.setObjectName("horizontalLayout_speed")
        self.label_speed = QtWidgets.QLabel(self.widget2)
        self.label_speed.setObjectName("label_speed")
        self.horizontalLayout_speed.addWidget(self.label_speed)
        self.doubleSpinBox_speed = QtWidgets.QDoubleSpinBox(self.widget2)
        self.doubleSpinBox_speed.setMinimumSize(QtCore.QSize(70, 0))
        self.doubleSpinBox_speed.setObjectName("doubleSpinBox_speed")
        self.horizontalLayout_speed.addWidget(self.doubleSpinBox_speed)
        self.verticalLayout_settings.addLayout(self.horizontalLayout_speed)
        self.horizontalLayout_plot_width = QtWidgets.QHBoxLayout()
        self.horizontalLayout_plot_width.setObjectName("horizontalLayout_plot_width")
        self.label_plot_width = QtWidgets.QLabel(self.widget2)
        self.label_plot_width.setObjectName("label_plot_width")
        self.horizontalLayout_plot_width.addWidget(self.label_plot_width)
        self.doubleSpinBox_plot_width = QtWidgets.QDoubleSpinBox(self.widget2)
        self.doubleSpinBox_plot_width.setMinimumSize(QtCore.QSize(70, 0))
        self.doubleSpinBox_plot_width.setObjectName("doubleSpinBox_plot_width")
        self.horizontalLayout_plot_width.addWidget(self.doubleSpinBox_plot_width)
        self.verticalLayout_settings.addLayout(self.horizontalLayout_plot_width)
        spacerItem = QtWidgets.QSpacerItem(20, 100, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_settings.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.widget2)
        self.label.setText("")
        self.label.setObjectName("label")
        self.verticalLayout_settings.addWidget(self.label)
        self.comboBox_functions = QtWidgets.QComboBox(self.widget2)
        self.comboBox_functions.setObjectName("comboBox_functions")
        self.verticalLayout_settings.addWidget(self.comboBox_functions)
        self.label_function_name = QtWidgets.QLabel(self.widget2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_function_name.sizePolicy().hasHeightForWidth())
        self.label_function_name.setSizePolicy(sizePolicy)
        self.label_function_name.setObjectName("label_function_name")
        self.verticalLayout_settings.addWidget(self.label_function_name)
        self.lineEdit_function_name = QtWidgets.QLineEdit(self.widget2)
        self.lineEdit_function_name.setObjectName("lineEdit_function_name")
        self.verticalLayout_settings.addWidget(self.lineEdit_function_name)
        self.label_function_regex = QtWidgets.QLabel(self.widget2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_function_regex.sizePolicy().hasHeightForWidth())
        self.label_function_regex.setSizePolicy(sizePolicy)
        self.label_function_regex.setObjectName("label_function_regex")
        self.verticalLayout_settings.addWidget(self.label_function_regex)
        self.lineEdit_function_regex = QtWidgets.QLineEdit(self.widget2)
        self.lineEdit_function_regex.setObjectName("lineEdit_function_regex")
        self.verticalLayout_settings.addWidget(self.lineEdit_function_regex)
        self.pushButton_label = QtWidgets.QPushButton(self.widget2)
        self.pushButton_label.setObjectName("pushButton_label")
        self.verticalLayout_settings.addWidget(self.pushButton_label)
        self.gridLayout.addWidget(self.splitter_main, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 693, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_Video = QtWidgets.QAction(MainWindow)
        self.actionOpen_Video.setObjectName("actionOpen_Video")
        self.actionOpen_Sensor_Data = QtWidgets.QAction(MainWindow)
        self.actionOpen_Sensor_Data.setObjectName("actionOpen_Sensor_Data")
        self.actionExport_Sensor_Data = QtWidgets.QAction(MainWindow)
        self.actionExport_Sensor_Data.setObjectName("actionExport_Sensor_Data")
        self.actionImport_Settings = QtWidgets.QAction(MainWindow)
        self.actionImport_Settings.setObjectName("actionImport_Settings")
        self.actionLabel_Settings = QtWidgets.QAction(MainWindow)
        self.actionLabel_Settings.setObjectName("actionLabel_Settings")
        self.actionSubject_Mapping = QtWidgets.QAction(MainWindow)
        self.actionSubject_Mapping.setObjectName("actionSubject_Mapping")
        self.actionMachine_Learning = QtWidgets.QAction(MainWindow)
        self.actionMachine_Learning.setObjectName("actionMachine_Learning")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionOpen_Video)
        self.menuFile.addAction(self.actionOpen_Sensor_Data)
        self.menuFile.addAction(self.actionExport_Sensor_Data)
        self.menuFile.addAction(self.actionImport_Settings)
        self.menuFile.addAction(self.actionLabel_Settings)
        self.menuFile.addAction(self.actionSubject_Mapping)
        self.menuFile.addAction(self.actionMachine_Learning)
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_video.setText(_translate("MainWindow", "Video"))
        self.label_duration.setText(_translate("MainWindow", "00:00:00"))
        self.label_sensor_data.setText(_translate("MainWindow", "Sensor Data"))
        self.label_date_title.setText(_translate("MainWindow", "Date"))
        self.label_time_title.setText(_translate("MainWindow", "Time"))
        self.label_camera_id.setText(_translate("MainWindow", "Camera ID"))
        self.label_new_camera.setText(_translate("MainWindow", "Add new camera ID:"))
        self.pushButton_add.setText(_translate("MainWindow", "Add"))
        self.label_video_offset.setText(_translate("MainWindow", "Video offset (s)"))
        self.label_speed.setText(_translate("MainWindow", "Speed"))
        self.label_plot_width.setText(_translate("MainWindow", "Plot width (s)"))
        self.label_function_name.setText(_translate("MainWindow", "Name"))
        self.label_function_regex.setText(_translate("MainWindow", "Regular expression"))
        self.pushButton_label.setText(_translate("MainWindow", "Label"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionOpen_Video.setText(_translate("MainWindow", "Open Video"))
        self.actionOpen_Sensor_Data.setText(_translate("MainWindow", "Open Sensor Data"))
        self.actionExport_Sensor_Data.setText(_translate("MainWindow", "Export Sensor Data"))
        self.actionImport_Settings.setText(_translate("MainWindow", "Import Settings"))
        self.actionLabel_Settings.setText(_translate("MainWindow", "Label Settings"))
        self.actionSubject_Mapping.setText(_translate("MainWindow", "Subject Mapping"))
        self.actionMachine_Learning.setText(_translate("MainWindow", "Machine Learning"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))

from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
