import os
os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts.warning=false"
import json
import requests
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QIntValidator
from PyQt5.QtWidgets import QApplication, QFrame, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel, QWidget, QFileDialog
from qfluentwidgets import (NavigationItemPosition, FluentWindow, SubtitleLabel, TitleLabel, LineEdit, SingleDirectionScrollArea, ExpandGroupSettingCard, SettingCard, ToolButton, IndeterminateProgressBar,
                            BodyLabel, ComboBox, StrongBodyLabel, SwitchButton, PrimaryPushButton, PushButton)
from qfluentwidgets import FluentIcon as FIF
from logic import (apply_settings, reset_configuration, open_installation_folder, launch_studio, update_studio, open_plugin_editor, open_theme_manager)
from downloader import download
import re
import winreg

global progressBar
progressBar = None

def endDownload():
    progressBar.stop()

internet = False

try:
    requests.get("https://8.8.8.8")
    internet = True
except:
    internet = False

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

class DownloadWorker(QThread):
    progressChanged = pyqtSignal(int)  

    def __init__(self, folder, channel):
        super().__init__()
        self.folder = folder
        self.channel = channel

    def run(self):
        download(self.folder, self.channel)  

class Window(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()
        self.initNavigation()
        self.loadAutoSettings()  

    def get_windows_theme(x):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "light" if value == 1 else "dark"
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error getting Windows theme: {exception}")
            return "dark"

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
        self.addSubInterface(self.settingInterface, FIF.SETTING, 'Settings', NavigationItemPosition.BOTTOM)
        self.navigationInterface.setAcrylicEnabled(True)

        headerLabelFlags = TitleLabel("Flags")
        headerLabelFlags.setFixedHeight(37)  
        headerLabelFlags.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  
        self.flagsInterface.widget().vBoxLayout.addWidget(headerLabelFlags)

        headerLabelMods = TitleLabel("Mods")
        headerLabelMods.setFixedHeight(37)
        headerLabelMods.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.modsInterface.widget().vBoxLayout.addWidget(headerLabelMods)

        headerLabelSettings = TitleLabel("Settings")
        headerLabelSettings.setFixedHeight(37)
        headerLabelSettings.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.settingInterface.widget().vBoxLayout.addWidget(headerLabelSettings)

        self.addLaunchOptionsButtons()

        self.loadOptions()

        self.addHomepageContent()

        self.addSettingsContent()

        self.current_theme = self.get_windows_theme()
        self.applyTheme()

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

        titleLabel = TitleLabel("Welcome to Roblox Studio Manager Remastered")
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

    def addSettingsContent(self):
        self.selectedChannel = ""
        self.selectedFolderPath = ""

        settingsLayout = QVBoxLayout()
        settingsLayout.setAlignment(Qt.AlignTop)

        self.settingInterface.setStyleSheet("background-color: #272727; border: none;")

        channelDownloaderCard = ExpandGroupSettingCard(FIF.DOWNLOAD, "Channel", "Pick a channel to download Roblox from.", self.settingInterface)
        settingsLayout.addWidget(channelDownloaderCard)

        self.channelLineEdit = LineEdit()
        self.channelLineEdit.setPlaceholderText("Enter Channel")
        self.channelLineEdit.returnPressed.connect(self.onChannelReturnPressed)
        channelDownloaderCard.addWidget(self.channelLineEdit)

        folderButton = ToolButton(FIF.FOLDER)
        downloadButton = PushButton("Download")

        channelDownloaderCard.addWidget(folderButton)
        channelDownloaderCard.addWidget(downloadButton)

        folderButton.clicked.connect(self.onFolderIconClicked)
        downloadButton.clicked.connect(self.startDownload)

        self.versionCard = SettingCard(title="Version", icon=FIF.INFO, content="")
        self.versionGuidCard = SettingCard(title="VersionGuid", icon=FIF.TAG, content="")
        self.deployedCard = SettingCard(title="Deployed", icon=FIF.DATE_TIME, content="")

        self.fetchVersionInfo()
        self.fetchDeployHistory()

        channelDownloaderCard.addGroupWidget(self.versionCard)
        channelDownloaderCard.addGroupWidget(self.versionGuidCard)
        channelDownloaderCard.addGroupWidget(self.deployedCard)

        scrollArea = SingleDirectionScrollArea(orient=Qt.Vertical)
        scrollWidget = QWidget(self.settingInterface)
        scrollWidget.setLayout(settingsLayout)

        scrollArea.setWidget(scrollWidget)
        scrollArea.setWidgetResizable(True)

        self.settingInterface.widget().vBoxLayout.addWidget(scrollArea)

        global progressBar
        progressBar = IndeterminateProgressBar(start = False)

        channelDownloaderCard.addGroupWidget(progressBar)

        if not internet:
            channelDownloaderCard.setEnabled(False)
            folderButton.setEnabled(False)
            downloadButton.setEnabled(False)
        print("\033[1;36mINFO:\033[0m Settings Content Created")

    def startDownload(self):
            global progressBar
            progressBar.start()

            self.worker = DownloadWorker(self.selectedFolderPath, self.selectedChannel.lower())
            self.worker.start()  

    def onFolderIconClicked(self):
        print("\033[1;36mINFO:\033[0m Folder Dialog Opened")
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", "", QFileDialog.ShowDirsOnly)
        if folder:
            self.selectedFolderPath = folder
            print("\033[1;36mINFO:\033[0m Selected Folder:", self.selectedFolderPath)
        print("\033[1;36mINFO:\033[0m Folder Dialog Closed")

    def onChannelReturnPressed(self):
        channel = self.channelLineEdit.text().strip()

        self.selectedChannel = channel.strip()

        if not channel:
            self.fetchDeployHistory()
            self.fetchVersionInfo()
        else:
            self.fetchDeployHistory(channel)
            self.fetchVersionInfo(channel)

    def fetchDeployHistory(self, channel=None):
        url = f"https://setup.rbxcdn.com/channel/{channel.lower()}/DeployHistory.txt" if channel else "https://setup.rbxcdn.com/DeployHistory.txt"
        try:
            response = requests.get(url)
            response.raise_for_status()
            lines = response.text.splitlines()

            for line in reversed(lines):
                if "studio" in line.lower():
                    date_time = line.split("at")[-1].split(",")[0].strip()
                    version = line.split("file version:")[-1]
                    version = '.'.join(re.sub(r',\s*git hash:.*', '', version).split(', ')).strip()
                    self.updateDeploymentInfo(date_time, version)
                    break
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error fetching deploy history: {exception}")
            self.updateDeploymentInfo("Unknown", "Unknown")

    def fetchVersionInfo(self, channel=None):
        url = f"https://setup.rbxcdn.com/channel/{channel.lower()}/versionQTStudio" if channel else "https://setup.rbxcdn.com/versionQTStudio"
        try:
            response = requests.get(url)
            response.raise_for_status()
            versionGuid = response.text.strip()
            self.updateVersionInfo(versionGuid)
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error fetching version info: {exception}")
            self.updateVersionInfo("Unknown")

    def updateDeploymentInfo(self, date_time, version):
        self.deployedCard.setContent(date_time)
        self.versionCard.setContent(version)

    def updateVersionInfo(self, versionGuid):
        self.versionGuidCard.setContent(versionGuid)

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

        except requests.exceptions.RequestException as exception:
            print(f"\033[1;31mERROR:\033[0m Error fetching release info: {exception}")
            return {'tag_name': 'N/A', 'body': 'Unable to fetch release information.'}

    def cleanReleaseDescription(self, body):
        cleaned_body = re.sub(r'>.*\n', '', body)  
        cleaned_body = re.sub(r'!\[.*?\]\(.*?\)', '', cleaned_body)  
        cleaned_body = re.sub(r'\[.*?\]\(.*?\)', '', cleaned_body)  
        return cleaned_body.strip()  

    def applyTheme(self):
        if self.current_theme == "dark":
            background_color = "#272727"
            text_color = "white"
            container_color = "#323232"
        else:
            background_color = "#f0f0f0"
            text_color = "black"
            container_color = "#fdfbfb"

        self.homeInterface.setStyleSheet(f"background-color: {background_color}; border: none; color: {text_color};")

        for _, comboBox in self.dropdown_widgets.items():
            container = comboBox.parentWidget()
            container.setStyleSheet(f"background-color: {container_color}; border-radius: 4px;")

        for _, toggle in self.toggle_widgets.items():
            container = toggle.parentWidget()
            container.setStyleSheet(f"background-color: {container_color}; border-radius: 4px;")

        for _, lineEdit in self.type_widgets.items():
            container = lineEdit.parentWidget()
            container.setStyleSheet(f"background-color: {container_color}; border-radius: 4px;")

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
                        self.addSectionHeader(option["SectionTitle"], option["SectionLocation"])
                    else:
                        self.addDropdown(option["Title"], option["Options"], option["Description"], option["Section"], option["InternetRequired"])

                for toggle in options["Toggles"]:
                    if "SectionTitle" in toggle:
                        self.addSectionHeader(toggle["SectionTitle"], toggle["SectionLocation"])
                    else:
                        self.addToggle(toggle["Title"], toggle["Description"], toggle["Section"], toggle["InternetRequired"])

                for type_option in options["Type"]:  
                    self.addTypeOption(type_option["Title"], type_option["Description"], type_option["Section"], type_option["Accept"], type_option["InternetRequired"])

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

    def addSectionHeader(self, section_title, section):

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        titleLabel = SubtitleLabel(section_title)

        layout = QVBoxLayout()
        layout.addWidget(titleLabel)

        container = QFrame()
        container.setLayout(layout)
        container.setFixedHeight(40)  

        if section == "Mods":
            self.modsInterface.widget().vBoxLayout.addWidget(container)
        elif section == "Flags":
            self.flagsInterface.widget().vBoxLayout.addWidget(container)

    def addDropdown(self, labelText, items, description, section, internetRequired):
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

        if internetRequired and not internet:
            comboBox.setEnabled(False)

        if section.lower() == "flags":
            self.flagsInterface.widget().vBoxLayout.addWidget(container)
        elif section.lower() == "mods":
            self.modsInterface.widget().vBoxLayout.addWidget(container)
        elif section.lower() == "settings":
            self.settingInterface.widget().vBoxLayout.addWidget(container)

    def addToggle(self, labelText, description, section, internetRequired):
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

        if internetRequired and not internet:
            toggleButton.setEnabled(False)

        if section.lower() == "flags":
            self.flagsInterface.widget().vBoxLayout.addWidget(container)
        elif section.lower() == "mods":
            self.modsInterface.widget().vBoxLayout.addWidget(container)

    def addTypeOption(self, labelText, description, section, accept_type, internetRequired):
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

        if internetRequired and not internet:
            lineEdit.setEnabled(False)

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
            except Exception as exception:
                print(f"\033[1;31mERROR:\033[0m {exception}")

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