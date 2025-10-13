![Roblox Studio Manager](https://github.com/Firebladedoge229/RobloxStudioManager/blob/main/images/RobloxStudioManager.png?raw=true)

# Roblox Studio Manager

> [!CAUTION]
> RobloxStudioManager has the ability to modify core Roblox Studio files, which may be detected as unauthorized.  
> Neither I nor any contributors are responsible for account bans or other consequences from its use.

A fork of [Roblox Studio Patcher](https://github.com/Firebladedoge229/RobloxStudioPatcher) with additional UI features.

A simple, easy-to-use program that contains many useful tools for customizing and managing ROBLOX Studio—whether you're changing themes, editing plugins, or modifying advanced settings.

![Showcase](https://github.com/Firebladedoge229/RobloxStudioManager/blob/main/images/RobloxStudioManagerScrsht.png?raw=true)

## Frequently Asked Questions

**Q: Is this a malicious program?**

  **A:** No, this program does not have any malicious intent. It is packaged into an executable using Nuitka, which can occasionally cause **false positives** in antivirus software. If you are concerned about the legitimacy of this program, feel free to check out the source code located in the [/src/](https://github.com/Firebladedoge229/RobloxStudioManager/tree/main/src) directory.

**Q: Could using this program result in a ban?**

**A:** The likelihood of getting banned for using this program is **extremely low**, however, some features are more risky than others. This is especially limited to those that modify core ROBLOX Studio files. Such features are clearly outlined in the repository's [wiki](https://github.com/Firebladedoge229/RobloxStudioManager/wiki/Advanced-and-Risky-Features). **Please note that if, for any reason, you do get banned—independent of the usage this program—I take no responsibility for it. You have been warned.**

**Q: Can I use this program on Mac or Linux?**

**A:** As of right now, this program is **only supported on Windows**. There is too much of a reliance on features specific to the Windows version of ROBLOX Studio. Mac and Linux [Wine] support may be added in the future.

**Q: What happens if an update breaks an aspect of the program?**

**A:** If an update to ROBLOX Studio breaks compatibility with specific features of this program, please feel free to **make an issue or pull request** within the repository!

## Features

- FastFlag Editor: Effortlessly add and test ROBLOX Beta Features with ease.
- Theming Manager: Apply custom, user-created themes to personalize your ROBLOX Studio experience
- Plugin Editor: Manage the status of Built-In plugins by enabling or disabling them with ease.
- Advanced Options: Unlock more powerful features, such as enabling ROBLOX Studio's internal settings or pausing updates.

## Themes

> [!WARNING]
> Roblox has been rolling out a new interface in Roblox Studio that reduces UI customizability.\
> Disable the "Next-Gen Studio Interface" option in the Flags menu if you plan to modify your theme.

Roblox Studio Manager lets you customize themes easily:  

- Access **Settings > Theme Manager** to modify themes.  
- Patching Roblox Studio is required to use custom themes.  
- Community-created themes are available in the [Discussions](https://github.com/Firebladedoge229/RobloxStudioManager/discussions) tab.

## Installation

Simply run the executable found at the [Releases](https://github.com/Firebladedoge229/RobloxStudioManager/releases/latest/download/RobloxStudioManager.exe) page.

A [Windows Defender SmartScreen](https://learn.microsoft.com/en-us/windows/security/operating-system-security/virus-and-threat-protection/microsoft-defender-smartscreen/) window may display, or your anti-virus might trigger. This is due to the application signing system of [PyInstaller](https://github.com/pyinstaller/pyinstaller) and [Nuitka](https://github.com/Nuitka/Nuitka).

If you are suspicious, feel free to compile the [code](https://github.com/Firebladedoge229/RobloxStudioManager/archive/refs/heads/main.zip) yourself!

> [!note]
> The project has since [moved](https://github.com/Firebladedoge229/RobloxStudioManager/commit/6111a6f15e8637141cda28f73307f455f62447a3) from PyInstaller to Nuitka for compiling the application after version v2.4.1.

> [!important]
> When building, make sure to download the latest version of [Resource Hacker](https://www.angusj.com/resourcehacker/resource_hacker.zip), placing the executable in the main directory.

### Build Command
#### Nuitka
```py
nuitka src/main.py --standalone --onefile --windows-disable-console --output-dir=build --output-filename=RobloxStudioManager --windows-icon-from-ico=images/logo.ico --noinclude-default-mode=nofollow --nofollow-imports --enable-plugin=pyqt5 --enable-plugin=anti-bloat --include-data-files="src/ui_components.py=ui_components.py" --include-data-files="src/downloader.py=downloader.py" --include-data-files="src/logic.py=logic.py" --include-data-files="data/fastflags.json=fastflags.json" --include-data-files="data/options.json=options.json" --include-data-files="images/logo.png=logo.png" --include-data-files="images/RobloxStudioManager.png=RobloxStudioManager.png" --include-data-files="build/ResourceHacker.exe=ResourceHacker.exe"
```
#### PyInstaller
```py
pyinstaller src/main.py --onefile --noconsole --icon=images/logo.ico --name=RobloxStudioManager --add-data="src/ui_components.py:." --add-data="src/downloader.py:." --add-data="src/logic.py:." --add-data="data/fastflags.json:data" --add-data="data/options.json:data" --add-data="images/logo.png:images" --add-data="images/RobloxStudioManager.png:images" --add-data="build/ResourceHacker.exe:build"
```

## Author

[Firebladedoge229](https://www.github.com/Firebladedoge229) - Creator and Maintainer

## Credits 

<ul style="list-style-type: square;">
  <li><a href="https://www.angusj.com/resourcehacker/">Resource Hacker</a> - Logo Replacement</li>
  <li><a href="https://web.archive.org/web/20190123202500im_/https://assets.contentstack.io/v3/assets/bltc2ad39afa86662c8/blt2387a75699f139aa/5c004be20df41c16214e0b69/Roblox_2.0_Brand_Guidelines_Nov_2018.pdf?disposition=inline">ROBLOX Corporation</a> - Roblox Studio</li>
  <li><a href="https://github.com/7ap/internal-studio-patcher">ROBLOX Internal Patcher</a> - Internal Features</li>
</ul>
