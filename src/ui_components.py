import os
os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts.warning=false"
import json
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator
from PyQt5.QtWidgets import QApplication, QFrame, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel, QWidget
from qfluentwidgets import (NavigationItemPosition, FluentWindow, SubtitleLabel, TitleLabel, LineEdit, SingleDirectionScrollArea,
                            BodyLabel, ComboBox, StrongBodyLabel, SwitchButton, PrimaryPushButton, PushButton)
from qfluentwidgets import FluentIcon as FIF
from logic import (apply_settings, reset_configuration, open_installation_folder, launch_studio, update_studio, open_plugin_editor, open_theme_manager)
import re

class Widget(QFrame):
    def __init__(self, parent=None, name=None):
        super().__init__(parent=parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.setContentsMargins(0, 0, 0, 0)

        if name:
            self.setObjectName(name)  
        else:
            print("\033[38;5;214mWARNING:\033[0m No name provided to Widget")

class ScrollableWidget(SingleDirectionScrollArea):
    def __init__(self, widget, direction=Qt.Vertical):
        super().__init__()
        self.setWidget(widget)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("background: transparent; border: none;")

class Window(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()
        self.initNavigation()
        self.loadAutoSettings()  

    def initNavigation(self):
        self.homeInterface = ScrollableWidget(Widget(self, "homeInterface"))
        self.modsInterface = ScrollableWidget(Widget(self, "modsInterface"))
        self.flagsInterface = ScrollableWidget(Widget(self, "flagsInterface"))
        self.launchoptionsInterface = ScrollableWidget(Widget(self, "launchoptionsInterface"))
        self.settingInterface = ScrollableWidget(Widget(self, "settingInterface"))

        self.homeInterface.setObjectName("homeInterface")
        self.modsInterface.setObjectName("modsInterface")
        self.flagsInterface.setObjectName("flagsInterface")
        self.launchoptionsInterface.setObjectName("launchoptionsInterface")
        self.settingInterface.setObjectName("settingInterface")

        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.modsInterface, FIF.ADD, 'Mods')
        self.addSubInterface(self.flagsInterface, FIF.FLAG, 'Flags')
        self.addSubInterface(self.launchoptionsInterface, FIF.PLAY, 'Launch Options')
        settingsInterface = self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)
        settingsInterface.setEnabled(False)
        self.navigationInterface.setAcrylicEnabled(True)

        headerLabelFlags = TitleLabel("Flags")
        headerLabelFlags.setFixedHeight(30)  
        headerLabelFlags.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  
        self.flagsInterface.widget().vBoxLayout.addWidget(headerLabelFlags)

        titleSpacer = QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)  
        self.flagsInterface.widget().vBoxLayout.addItem(titleSpacer)

        headerLabelMods = TitleLabel("Mods")
        headerLabelMods.setFixedHeight(30)
        headerLabelMods.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.modsInterface.widget().vBoxLayout.addWidget(headerLabelMods)

        titleSpacer = QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)  
        self.modsInterface.widget().vBoxLayout.addItem(titleSpacer)

        self.addLaunchOptionsButtons()

        self.loadOptions()

        self.addHomepageContent()

    def addHomepageContent(self):

        homeLayout = QVBoxLayout(self.homeInterface)
        homeLayout.setAlignment(Qt.AlignCenter)

        self.homeInterface.setStyleSheet("background-color: #272727; border: none;")

        logoLabel = QLabel()
        logoPixmap = QPixmap("RobloxStudioManager.png")

        max_width = 700
        max_height = 700
        logoPixmap = logoPixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        logoLabel.setPixmap(logoPixmap)
        logoLabel.setAlignment(Qt.AlignCenter)

        titleLabel = TitleLabel("Welcome to Roblox Studio Manager")
        descriptionLabel = SubtitleLabel("Manage your Roblox Studio settings and plugins easily.")

        titleLabel.setAlignment(Qt.AlignCenter)
        descriptionLabel.setAlignment(Qt.AlignCenter)

        homeLayout.addWidget(logoLabel)
        homeLayout.addWidget(titleLabel)
        homeLayout.addWidget(descriptionLabel)

        release_info = self.fetchLatestReleaseInfo()

        releaseLayout = QVBoxLayout()
        releaseLayout.setAlignment(Qt.AlignTop)

        releaseLabel = TitleLabel(f"Latest Release: {release_info['tag_name']}")
        releaseLabel.setAlignment(Qt.AlignCenter)
        releaseLabel.setWordWrap(True)

        releaseDescriptionLabel = SubtitleLabel(f"{release_info['body']}")
        releaseDescriptionLabel.setAlignment(Qt.AlignCenter)
        releaseDescriptionLabel.setWordWrap(True)

        releaseLayout.addWidget(releaseLabel)
        releaseLayout.addWidget(releaseDescriptionLabel)

        releaseScrollArea = SingleDirectionScrollArea(orient=Qt.Vertical)
        releaseScrollArea.setWidgetResizable(True)

        releaseWidget = QWidget(self.homeInterface)
        releaseWidget.setLayout(releaseLayout)

        releaseScrollArea.setWidget(releaseWidget)

        homeLayout.addWidget(releaseScrollArea)

        scrollArea = SingleDirectionScrollArea(orient=Qt.Vertical)  
        scrollWidget = QWidget(self.homeInterface)
        scrollWidget.setLayout(homeLayout)

        scrollArea.setWidget(scrollWidget)
        scrollArea.setWidgetResizable(True)

        self.homeInterface.widget().vBoxLayout.addWidget(scrollArea)

    def fetchLatestReleaseInfo(self):

        github_url = "https://api.github.com/repos/Firebladedoge229/RobloxStudioManager/releases/latest"

        try:

            response = requests.get(github_url)
            response.raise_for_status()  

            release_data = response.json()

            release_info = {
                'tag_name': release_data['tag_name'],  
                'body': self.cleanReleaseDescription(release_data['body'])  
            }

            return release_info

        except requests.exceptions.RequestException as e:
            print(f"\033[1;31mERROR:\033[0m Error fetching release info: {e}")
            return {'tag_name': 'N/A', 'body': 'Unable to fetch release information.'}

    def cleanReleaseDescription(self, body):

        cleaned_body = re.sub(r'>.*\n', '', body)  
        cleaned_body = re.sub(r'!\[.*?\]\(.*?\)', '', cleaned_body)  

        cleaned_body = re.sub(r'\[.*?\]\(.*?\)', '', cleaned_body)  

        return cleaned_body.strip()  

    def initWindow(self):
        print(f"\033[1;36mINFO:\033[0m Current working directory: {os.getcwd()}")
        print(f"\033[1;36mINFO:\033[0m Real path: {os.path.dirname(os.path.realpath(__file__))}")
        self.resize(900, 700)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "logo.png")))
        self.setWindowTitle('Roblox Studio Manager')
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def loadOptions(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

        try:
            with open("options.json", "r") as file:
                options = json.load(file)

                self.dropdown_widgets = {}
                self.toggle_widgets = {}
                self.type_widgets = {}

                for option in options["Dropdowns"]:
                    if "SectionTitle" in option:
                        self.addSectionHeader(option["SectionTitle"])
                    else:
                        self.addDropdown(option["Title"], option["Options"], option["Description"], option["Section"])

                for toggle in options["Toggles"]:
                    if "SectionTitle" in toggle:
                        self.addSectionHeader(toggle["SectionTitle"])
                    else:
                        self.addToggle(toggle["Title"], toggle["Description"], toggle["Section"])

                for type_option in options["Type"]:  
                    self.addTypeOption(type_option["Title"], type_option["Description"], type_option["Section"], type_option["Accept"])

        except FileNotFoundError:
            print("\033[1;31mDATA ERROR:\033[0m options.json not found!")

        bottomSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.modsInterface.widget().vBoxLayout.addItem(bottomSpacer)

        bottomSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.flagsInterface.widget().vBoxLayout.addItem(bottomSpacer)

    def addLaunchOptionsButtons(self):

        applyButton = PrimaryPushButton("Apply Settings")
        applyButton.clicked.connect(self.applySettings)

        resetButton = PushButton("Reset Configuration")
        resetButton.clicked.connect(reset_configuration)

        installButton = PushButton("Installation Folder")
        installButton.clicked.connect(open_installation_folder)

        launchButton = PrimaryPushButton("Launch Studio")
        launchButton.clicked.connect(launch_studio)

        updateButton = PushButton("Update Studio")
        updateButton.clicked.connect(update_studio)

        pluginButton = PushButton("Plugin Editor")
        pluginButton.setEnabled(False)
        pluginButton.clicked.connect(open_plugin_editor)

        themeButton = PushButton("Theme Manager")
        themeButton.setEnabled(False)
        themeButton.clicked.connect(open_theme_manager)

        self.launchoptionsInterface.widget().vBoxLayout.addWidget(applyButton)
        self.launchoptionsInterface.widget().vBoxLayout.addWidget(resetButton)
        self.launchoptionsInterface.widget().vBoxLayout.addWidget(installButton)
        self.launchoptionsInterface.widget().vBoxLayout.addWidget(launchButton)
        self.launchoptionsInterface.widget().vBoxLayout.addWidget(updateButton)
        self.launchoptionsInterface.widget().vBoxLayout.addWidget(pluginButton)
        self.launchoptionsInterface.widget().vBoxLayout.addWidget(themeButton)

    def addSectionHeader(self, section_title):

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        titleLabel = SubtitleLabel(section_title)

        layout = QVBoxLayout()
        layout.addWidget(titleLabel)

        container = QFrame()
        container.setLayout(layout)
        container.setFixedHeight(40)  

        self.flagsInterface.widget().vBoxLayout.addWidget(container)

    def addDropdown(self, labelText, items, description, section):
        container = QFrame()
        container.setStyleSheet("background-color: #323232; border-radius: 4px;")
        container.setFixedHeight(70)
        container.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  
        layout.setSpacing(5)

        leftLayout = QVBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)
        leftLayout.setSpacing(2)

        title = StrongBodyLabel(labelText)
        title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        descriptionLabel = BodyLabel(description)
        descriptionLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        leftLayout.addWidget(title, alignment=Qt.AlignLeft)
        leftLayout.addWidget(descriptionLabel, alignment=Qt.AlignLeft)

        rightLayout = QVBoxLayout()
        rightLayout.setContentsMargins(0, 0, 0, 0)
        rightLayout.setSpacing(2)

        comboBox = ComboBox()
        comboBox.addItems(items)
        comboBox.setFixedWidth(200)

        self.dropdown_widgets[labelText] = comboBox

        rightLayout.addWidget(comboBox, alignment=Qt.AlignRight)

        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)

        container.setLayout(layout)

        if section.lower() == "flags":
            self.flagsInterface.widget().vBoxLayout.addWidget(container)
        elif section.lower() == "mods":
            self.modsInterface.widget().vBoxLayout.addWidget(container)

    def addToggle(self, labelText, description, section):
        container = QFrame()
        container.setStyleSheet("background-color: #323232; border-radius: 4px;")
        container.setFixedHeight(70)
        container.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        leftLayout = QVBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)
        leftLayout.setSpacing(2)

        title = StrongBodyLabel(labelText)
        title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        descriptionLabel = BodyLabel(description)
        descriptionLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        leftLayout.addWidget(title, alignment=Qt.AlignLeft)
        leftLayout.addWidget(descriptionLabel, alignment=Qt.AlignLeft)

        rightLayout = QVBoxLayout()
        rightLayout.setContentsMargins(0, 0, 0, 0)
        rightLayout.setSpacing(2)

        toggleButton = SwitchButton()
        toggleButton.setChecked(False)
        toggleButton.setOnText("")
        toggleButton.setOffText("")

        self.toggle_widgets[labelText] = toggleButton

        rightLayout.addWidget(toggleButton, alignment=Qt.AlignRight)

        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)

        container.setLayout(layout)

        if section.lower() == "flags":
            self.flagsInterface.widget().vBoxLayout.addWidget(container)
        elif section.lower() == "mods":
            self.modsInterface.widget().vBoxLayout.addWidget(container)

    def addTypeOption(self, labelText, description, section, accept_type):
        container = QFrame()
        container.setStyleSheet("background-color: #323232; border-radius: 4px;")
        container.setFixedHeight(70)
        container.setContentsMargins(0, 0, 0, 0)

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        leftLayout = QVBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)
        leftLayout.setSpacing(2)

        title = StrongBodyLabel(labelText)
        title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        descriptionLabel = BodyLabel(description)
        descriptionLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        leftLayout.addWidget(title, alignment=Qt.AlignLeft)
        leftLayout.addWidget(descriptionLabel, alignment=Qt.AlignLeft)

        rightLayout = QVBoxLayout()
        rightLayout.setContentsMargins(0, 0, 0, 0)
        rightLayout.setSpacing(2)

        lineEdit = LineEdit()
        lineEdit.setPlaceholderText("")
        lineEdit.setText("")  

        if accept_type.lower() == "integer":

            lineEdit.setValidator(QIntValidator())

        self.type_widgets[labelText] = lineEdit  

        rightLayout.addWidget(lineEdit, alignment=Qt.AlignRight)

        layout.addLayout(leftLayout)
        layout.addLayout(rightLayout)

        container.setLayout(layout)

        if section.lower() == "flags":
            self.flagsInterface.widget().vBoxLayout.addWidget(container)
        elif section.lower() == "mods":
            self.modsInterface.widget().vBoxLayout.addWidget(container)

    def loadAutoSettings(self):
        settings_path = "RobloxStudioManagerSettings.json"

        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r") as file:
                    settings = json.load(file)

                    self.applySettingsFromJson(settings)

            except json.JSONDecodeError:
                print("\033[1;31mERROR:\033[0m Error loading settings from JSON file.")
            except Exception as e:
                print(f"\033[1;31mERROR:\033[0m {e}")

    def applySettingsFromJson(self, settings):

        for setting, value in settings.items():

            if setting in self.dropdown_widgets:

                self.dropdown_widgets[setting].setCurrentText(value)

            elif setting in self.toggle_widgets:

                self.toggle_widgets[setting].setChecked(value)

            elif setting in self.type_widgets:

                self.type_widgets[setting].setText(str(value))

            if value == "":
                value = "None"

            print(f"\033[38;2;52;235;143mDATA:\033[0m Loaded setting {setting} with the value of {value}")

    def applySettings(self):
        settings = {}
        for label, comboBox in self.dropdown_widgets.items():
            settings[label] = comboBox.currentText()

        for label, toggle in self.toggle_widgets.items():
            settings[label] = toggle.isChecked()

        for label, lineEdit in self.type_widgets.items():

            settings[label] = lineEdit.text()

        apply_settings(settings)
        print(f"\033[38;2;52;235;143mDATA:\033[0m Settings applied: {settings}")