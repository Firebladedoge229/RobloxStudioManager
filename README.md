![Roblox Studio Manager](https://github.com/Firebladedoge229/RobloxStudioManager/blob/main/images/RobloxStudioManager.png?raw=true)

# Roblox Studio Manager

A fork of [Roblox Studio Patcher](https://github.com/Firebladedoge229/RobloxStudioPatcher) with additional UI features.

![Showcase](https://github.com/Firebladedoge229/RobloxStudioManager/blob/main/images/RobloxStudioManagerScrsht.png?raw=true)

## Frequently Asked Questions

**Q: Is this a malicious program?**

**A:** No, this program does not have any malicious intent. It is packaged into an executable using PyInstaller, which can occasionally cause **false positives** in antivirus software. As a result, Roblox Studio Manager may be flagged as a potential threat. If you are concerned about the legitimacy of this program, feel free to check out the source code located in the [/src/](https://github.com/Firebladedoge229/RobloxStudioManager/tree/main/src) folder.

**Q: Could using this program result in a ban?**

**A:** The likelihood of getting banned for using this program is **extremely low**; however some features are more risky than others. This is especially limited to those that modify core ROBLOX Studio files. Such features are clearly outlined in the repository's [wiki](https://github.com/Firebladedoge229/RobloxStudioManager/wiki/Advanced-and-Risky-Features), allowing you to make an informed decision. **Please note that if, for any reason, you do get banned—independent of the usage this program—I take no responsibility for it. You have been warned.**

**Q: Is this program compatible with all versions of ROBLOX Studio?**

**A:** This program is designed to work with the **latest version** of ROBLOX Studio, although some features may not function properly with older versions. I would recommended to keep ROBLOX Studio up to date for the best experience.

**Q: Can I use this program on Mac/Linux?**

**A:** As of right now, this program is **only supported on Windows**. There is too much of a reliance on features specific to the Windows version of ROBLOX Studio. Mac and Linux [Wine] support may be added in the future.

**Q: Does this program require an internet connection?**

**A:** Some features, such as enabling beta features or disabling telemetry, **may require an internet connection**. Most of the features in the Flags section do not require internet.

**Q: Can I contribute to the project?**

**A:** Yes! **Contributions are always welcome**. Check out the repository’s contributing guidelines for more information on how you can help improve the program.

**Q: What happens if an update breaks an aspect of the program?**

**A:** If an update to ROBLOX Studio breaks compatibility with specific features of this program, please feel free to **make an issue or pull request** within the repository!

## Features

- FastFlag Editor: Effortlessly add and test ROBLOX Beta Features with ease.
- Theming Manager: Apply custom, user-created themes to personalize your ROBLOX Studio experience
- Plugin Editor: Manage the status of Built-In plugins by enabling or disabling them with ease.
- Advanced Options: Unlock more powerful features, such as enabling ROBLOX Studio's internal settings or pausing updates.

## Installation

Simply run the executable found at the [Releases](https://github.com/Firebladedoge229/RobloxStudioManager/releases/latest/download/RobloxStudioManager.exe) page.

A [Windows Defender SmartScreen](https://learn.microsoft.com/en-us/windows/security/operating-system-security/virus-and-threat-protection/microsoft-defender-smartscreen/) window may display, or your anti-virus might trigger. This is due to the application signing system of [PyInstaller](https://github.com/pyinstaller/pyinstaller).

If you are suspicious, feel free to compile the [code](https://github.com/Firebladedoge229/RobloxStudioManager/archive/refs/heads/main.zip) yourself!

### Build Command
```py
pyinstaller --onefile --noconsole --icon=images/logo.ico --add-data="src/ui_components.py:." --add-data="src/downloader.py:." --add-data="src/logic.py:." --add-data="data:." --add-data="images/logo.png:." --add-data="images/RobloxStudioManager.png:." src/main.py
```

## Author

[Firebladedoge229](https://www.github.com/Firebladedoge229) - Creator and Maintainer

## Credits 

[ROBLOX Corporation](https://web.archive.org/web/20190123202500if_/https://assets.contentstack.io/v3/assets/bltc2ad39afa86662c8/blt2387a75699f139aa/5c004be20df41c16214e0b69/Roblox_2.0_Brand_Guidelines_Nov_2018.pdf?disposition=inline) - Roblox Studio
