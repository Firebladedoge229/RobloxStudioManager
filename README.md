![Roblox Studio Manager](https://github.com/Firebladedoge229/RobloxStudioManager/blob/main/images/RobloxStudioManager.png?raw=true)

# Roblox Studio Manager

A fork of [Roblox Studio Patcher](https://github.com/Firebladedoge229/RobloxStudioPatcher) with additional UI features.

![Showcase](https://github.com/Firebladedoge229/RobloxStudioManager/blob/main/images/RobloxStudioManagerScrsht.png?raw=true)

## Installation

Simply run the executable found at the [Releases](https://github.com/Firebladedoge229/RobloxStudioManager/releases/latest/download/RobloxStudioManager.exe) page.

A [Windows Defender SmartScreen](https://learn.microsoft.com/en-us/windows/security/operating-system-security/virus-and-threat-protection/microsoft-defender-smartscreen/) window may display, or your anti-virus might trigger, this is due to the application signing system by [PyInstaller](https://github.com/pyinstaller/pyinstaller).

If you are suspicious, feel free to compile the [code](https://github.com/Firebladedoge229/RobloxStudioManager/archive/refs/heads/main.zip) yourself!

### Build Command
```py
pyinstaller --onefile --noconsole --icon=images/logo.ico --add-data="src/ui_components.py:." --add-data="src/downloader.py:." --add-data="src/logic.py:." --add-data="data:." --add-data="images/logo.png:." --add-data="images/RobloxStudioManager.png:." src/main.py
```

## Author

[Firebladedoge229](https://www.github.com/Firebladedoge229) - Creator

## Credits 

[ROBLOX Corporation](https://web.archive.org/web/20190123202500if_/https://assets.contentstack.io/v3/assets/bltc2ad39afa86662c8/blt2387a75699f139aa/5c004be20df41c16214e0b69/Roblox_2.0_Brand_Guidelines_Nov_2018.pdf?disposition=inline) - Roblox Studio
