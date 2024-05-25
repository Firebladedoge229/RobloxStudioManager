import os
import re
import sys
import json
import time
import psutil
import sv_ttk
import requests
import threading
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import ttk, messagebox
import configparser as ConfigParser

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

global selected_version
selected_version = None

optimizer = "https://raw.githubusercontent.com/rbxflags/Flags/main/ClientAppSettings.json"
versions_dir = os.path.join(os.environ['LOCALAPPDATA'], 'Roblox', 'Versions')
max_files_count = 0

for version in os.listdir(versions_dir):
    version_dir = os.path.join(versions_dir, version)

    exe_path = os.path.join(version_dir, 'RobloxStudioBeta.exe')
    if os.path.exists(exe_path):
        num_files = len([name for name in os.listdir(version_dir)])

        if num_files > max_files_count:
            max_files_count = num_files
            selected_version = version_dir

def is_modded():
    if os.path.exists(os.path.join(selected_version, 'ClientSettings')):
        return "Yes"
    else:
        return "No"

def get_channel():
    return requests.get("https://clientsettings.roblox.com/v2/user-channel?binaryType=WindowsStudio64").json()["channelName"]

def check_internet():
    try:
        requests.head("http://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def find_version_line(version, lines):
    for line in lines.splitlines():
        if version in line:
            return line
    return None

def reset_fflags():
    result = messagebox.askyesno("Roblox Studio Manager", "Are you sure you want to reset your FFlags?")
    if result:
        app_settings_path = os.path.join(selected_version, 'ClientSettings', 'ClientAppSettings.json')
        if os.path.exists(os.path.join(selected_version, 'ClientSettings')):
            open(app_settings_path, "w").close()
            open(app_settings_path, "w+").write("{}")
            
def installation_folder():
    os.system(f'explorer "{selected_version}')

def launch_studio_async():
    os.system(f"{selected_version}\RobloxStudioBeta.exe")

def update_studio_async():
    os.system(f"{selected_version}\RobloxStudioInstaller.exe")

def update_settings():
    t = threading.Thread(target=update_settings_async)
    t.start()

def launch_studio():
    t = threading.Thread(target=launch_studio_async)
    t.start()

def update_studio():
    t = threading.Thread(target=update_studio_async)
    t.start()
  
Config = ConfigParser.ConfigParser()

def update_settings_async():
    studio_id = studio_running()

    if studio_id:
        result = messagebox.askyesno("Roblox Studio Manager", "Roblox Studio is currently running. Do you want to close it to apply the changes?")
        if result:
            psutil.Process(studio_id).kill()
            psutil.Process(studio_id).wait()

    start_time = time.time()

    optimize_roblox = optimize_roblox_var.get()
    menu_type = menu_type_var.get()
    topbar_type = topbar_type_var.get()
    msaa_level = msaa_level_var.get()
    graphics_type = graphics_type_var.get()
    max_fps = max_fps_var.get()
    font_size = font_size_var.get()
    coregui_transparency = coregui_transparency_var.get()
    log_requests = log_requests_var.get()
    enable_proxy = enable_proxy_var.get()
    enable_internal = enable_internal_var.get()
    show_flags = show_flags_var.get()
    log_all = log_all_var.get()
    code_assist = code_assist_var.get()
    disable_telemetry = disable_telemetry_var.get()
    rainbow_ui = rainbow_ui_var.get()
    force_high_graphics = force_high_graphics_var.get()
    visual_verified = visual_verified_var.get()
    old_font = old_font_var.get()
    classic_error = classic_error_var.get()
    disable_updating = disable_updating_var.get()
    extra_plugins = extra_plugins_var.get()
    framerate_settings = framerate_settings_var.get()
    Config["Configuration"] = {}
    Config["Plugins"] = {}
    Config["Configuration"]["optimize_roblox"] = str(optimize_roblox_var.get())
    Config["Configuration"]["menu_type"] = str(menu_type_var.get())
    Config["Configuration"]["topbar_type"] = str(topbar_type_var.get())
    Config["Configuration"]["msaa_level"] = str(msaa_level_var.get())
    Config["Configuration"]["graphics_type"] = str(graphics_type_var.get())
    Config["Configuration"]["max_fps"] = str(max_fps_var.get())
    Config["Configuration"]["font_size"] = str(font_size_var.get())
    Config["Configuration"]["coregui_transparency"] = str(coregui_transparency_var.get())
    Config["Configuration"]["log_requests"] = str(log_requests_var.get())
    Config["Configuration"]["enable_proxy"] = str(enable_proxy_var.get())
    Config["Configuration"]["enable_internal"] = str(enable_internal_var.get())
    Config["Configuration"]["show_flags"] = str(show_flags_var.get())
    Config["Configuration"]["log_all"] = str(log_all_var.get())
    Config["Configuration"]["code_assist"] = str(code_assist_var.get())
    Config["Configuration"]["disable_telemetry"] = str(disable_telemetry_var.get())
    Config["Configuration"]["rainbow_ui"] = str(rainbow_ui_var.get())
    Config["Configuration"]["force_high_graphics"] = str(force_high_graphics_var.get())
    Config["Configuration"]["visual_verified"] = str(visual_verified_var.get())
    Config["Configuration"]["old_font"] = str(old_font_var.get())
    Config["Configuration"]["classic_error"] = str(classic_error_var.get())
    Config["Configuration"]["disable_updating"] = str(disable_updating_var.get())
    Config["Configuration"]["extra_plugins"] = str(extra_plugins_var.get())
    Config["Configuration"]["framerate_settings"] = str(framerate_settings_var.get())
    for plugin, state in plugin_check_states.items():
        if not state.get():
            Config["Plugins"][plugin] = str(state.get())

    with open("robloxstudiomanagerconfig.ini", "w") as configfile:
        Config.write(configfile)

    flags = {
        "FFlagDebugGraphicsPreferD3D11": "true",  # directx 11 usage
        "DFIntTaskSchedulerTargetFps": int(max_fps),  # max fps
        "FIntFontSizePadding": int(font_size) # font size
    }

    internal_signature = b"\x80\xBF\x78\x01\x00\x00\x00\x74\x05\xE8"
    internal_patch = b"\x80\xBF\x78\x01\x00\x00\x00\x90\x90\xE8"

    if menu_type == "Version 1":
        flags["FFlagDisableNewIGMinDUA"] = "true"  # disable version 2 menu
        flags["FFlagEnableInGameMenuControls"] = "false"  # version 4 menu
        flags["FFlagEnableMenuControlsABTest"] = "false"  # ab test
        flags["FFlagEnableMenuModernizationABTest"] = "false"  # ab test
        flags["FFlagEnableMenuModernizationABTest2"] = "false"  # ab test
        flags["FFlagEnableV3MenuABTest3"] = "false"  # ab test
    elif menu_type == "Version 2":
        flags["FFlagDisableNewIGMinDUA"] = "false"  # disable version 2 menu
        flags["FFlagEnableInGameMenuControls"] = "false"  # version 4 menu
        flags["FFlagEnableMenuControlsABTest"] = "false"  # ab test
        flags["FFlagEnableMenuModernizationABTest"] = "false"  # ab test
        flags["FFlagEnableMenuModernizationABTest2"] = "false"  # ab test
        flags["FFlagEnableV3MenuABTest3"] = "false"  # ab test
    elif menu_type == "Version 4":
        flags["FFlagDisableNewIGMinDUA"] = "true"  # disable version 2 menu
        flags["FFlagEnableInGameMenuControls"] = "true"  # version 4 menu
        flags["FFlagEnableMenuControlsABTest"] = "false"  # ab test
        flags["FFlagEnableMenuModernizationABTest"] = "false"  # ab test
        flags["FFlagEnableMenuModernizationABTest2"] = "false"  # ab test
        flags["FFlagEnableV3MenuABTest3"] = "false"  # ab test

    if topbar_type == "Old":
        flags["FFlagEnableInGameMenuChrome"] = "false"  # version 4 menu
    elif topbar_type == "New":
        flags["FFlagEnableInGameMenuChrome"] = "true"  # version 4 menu
        flags["FFlagEnableChromePinnedChat"] = "false" # disable chat

    if log_requests:
        flags["DFLogHttpTraceLight"] = 12
    else:
        flags["DFLogHttpTraceLight"] = 6

    if enable_proxy:
        flags["FFlagStudioReEnableNetworkProxy_Dev"] = "true"  # proxy settings
        flags["DFFlagHideProxySettings"] = "false"  # proxy settings
        flags["DFFlagDebugEnableHttpProxy"] = "true"  # proxy settings"
    else:
        flags["FFlagStudioReEnableNetworkProxy_Dev"] = "false"  # proxy settings
        flags["DFFlagHideProxySettings"] = "true"  # proxy settings
        flags["DFFlagDebugEnableHttpProxy"] = "false"  # proxy settings"

    if msaa_level == "1x":
        flags["DebugForceMSAASamples"] = 1  # msaa level
    elif msaa_level == "2x":
        flags["DebugForceMSAASamples"] = 2  # msaa level
    elif msaa_level == "4x":
        flags["DebugForceMSAASamples"] = 4  # msaa level
    elif msaa_level == "8x":
        flags["DebugForceMSAASamples"] = 8  # msaa level

    if graphics_type == "10":
        flags["FFlagFixGraphicsQuality"] = "false"  # 21 levels
    elif graphics_type == "21":
        flags["FFlagFixGraphicsQuality"] = "true"  # 21 levels

    if show_flags:
        flag_list = ""
        for flag in flags:
            flag_list += flag + ","
        flags["FStringDebugShowFlagState"] = flag_list[:-1]

    if log_all:
        jsonData = requests.get(
            "https://raw.githubusercontent.com/MaximumADHD/Roblox-FFlag-Tracker/main/PCStudioApp.json").json()
        for flag, value in jsonData.items():
            if flag.startswith("FLog") or flag.startswith("DFLog"):
                flags[flag] = 12

    if code_assist:
        flags["FFlagRelatedScriptsCodeAssist"] = "true"
        flags["FFlagCodeAssistFeature"] = "true"
        flags["FFlagAICOChatBot"] = "true"

    if disable_telemetry:
        response = requests.get(
            "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/FVariables.txt")
        if response.status_code == 200:
            telemetryFlags = re.findall(r'\[.*\]\s*(\w+Telemetry\w*)', response.text)
            for flag in telemetryFlags:
                flag_name = re.sub(r'\[.*\]\s*', '', flag)
                flags[flag_name] = "false"

    if rainbow_ui:
        flags["FFlagDebugDisplayUnthemedInstances"] = "true"

    if force_high_graphics:
        flags["DFFlagDisableDPIScale"] = "true"
        flags["FIntTextureCompositorLowResFactor"] = 4
        flags["DFFlagEnableRequestAsyncCompression"] = "false"

    if visual_verified:
        flags["FFlagOverridePlayerVerifiedBadge"] = "true"

    if old_font:
        flags["FFlagUIBloxDevUseNewFontNameMapping"] = "false"
        flags["FFlagEnableNewFontNameMappingABTest2"] = "false"

    if classic_error:
        flags["FFlagErrorPromptResizesHeight"] = "false"

    if extra_plugins:
        flags["FFlagEnableRibbonPlugin"] = "true"
        flags["FFlagDebugAvatarInternalToolsPlugin"] = "true"
        flags["NestedPackagePublisherPlugin"] = "true"
        flags["DebugEnableBootcampPlugin"] = "true"
        flags["RetireAudioDiscoveryPlugin"] = "false"

    if framerate_settings:
        flags["FFlagGameBasicSettingsFramerateCap5"] = "true"

    if selected_version is not None:
        app_settings_path = os.path.join(selected_version, 'ClientSettings', 'ClientAppSettings.json')
        
        if not os.path.exists(os.path.join(selected_version, 'ClientSettings')):
            os.makedirs(os.path.join(selected_version, 'ClientSettings'))

        open(app_settings_path, "w").close()
        open(app_settings_path, "w+").write("{}")

        with open(app_settings_path, 'r+') as f:
            app_settings = json.load(f)
            if optimize_roblox:
                request = requests.get(
                    optimizer).json()
                for k, v in request.items():
                    if k != "DFIntTaskSchedulerTargetFPS":
                        app_settings[k] = v
            for k, v in flags.items():
                if k != "DFIntTaskSchedulerTargetFPS":
                        app_settings[k] = v
            f.seek(0)
            json.dump(app_settings, f, indent=4)
            f.truncate()

        if enable_internal:
            exe_path = os.path.join(selected_version, 'RobloxStudioBeta.exe')
            with open(exe_path, 'r+b') as f:
                content = f.read()
                index = content.find(internal_signature)
                if index != -1:
                    f.seek(index)
                    f.write(internal_patch)
        elif enable_internal == False:
            exe_path = os.path.join(selected_version, 'RobloxStudioBeta.exe')
            with open(exe_path, 'r+b') as f:
                content = f.read()
                index = content.find(internal_patch)
                if index != -1:
                    f.seek(index)
                    f.write(internal_signature)

        result = find_version_line(os.path.basename(selected_version), requests.get("https://setup.rbxcdn.com/DeployHistory.txt").text)
        result = re.search(r'git hash:\s*(\d+\.\d+\.\d+\.\d+)', result).group().replace("git hash: ", "")
        patch = re.sub(r'\d', '9', result)
        result = bytes.fromhex("".join(format(ord(char), '02X') for char in result))
        patch = bytes.fromhex("".join(format(ord(char), '02X') for char in patch))

        if disable_updating:
            exe_path = os.path.join(selected_version, 'RobloxStudioBeta.exe')
            with open(exe_path, 'r+b') as f:
                content = f.read()
                index = content.find(result)
                if index != -1:
                    f.seek(index)
                    f.write(patch)
        elif disable_updating == False:
            exe_path = os.path.join(selected_version, 'RobloxStudioBeta.exe')
            with open(exe_path, 'r+b') as f:
                content = f.read()
                index = content.find(patch)
                if index != -1:
                    f.seek(index)
                    f.write(result)

        tree = ET.parse(os.path.join(os.path.join(os.environ['LOCALAPPDATA'], 'Roblox'), "GlobalBasicSettings_13_Studio.xml"))
        root = tree.getroot()

        for item in root.findall(".//Item[@class='UserGameSettings']"):
            for prop in item.find('Properties'):
                if prop.tag == 'float' and prop.attrib.get('name') == 'PreferredTransparency':
                    prop.text = str((4 / 99) * float(coregui_transparency) + (95 / 99))
                    break

        tree.write(os.path.join(os.path.join(os.environ['LOCALAPPDATA'], 'Roblox'), "GlobalBasicSettings_13_Studio.xml"), encoding='utf-8', xml_declaration=True)

        for plugin in pluginList:
            update_plugin_state(plugin)

        end_time = time.time()

        result = messagebox.showinfo("Roblox Studio Manager", f"Successfully patched in {str(round(end_time - start_time, 2))}ms.")

def studio_running():
    for proc in psutil.process_iter():
        if "RobloxStudioBeta" in proc.name():
            return proc.pid
    return False

def get_config_value(section, option, default):
    try:
        return Config.get(section, option)
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
        return default

root = tk.Tk()
root.title("Roblox Studio Manager")

Config.read("robloxstudiomanagerconfig.ini")

optimize_roblox_var = tk.BooleanVar(value=get_config_value("Configuration", "optimize_roblox", False))
menu_type_var = tk.StringVar(value=get_config_value("Configuration", "menu_type", "Version 4"))
topbar_type_var = tk.StringVar(value=get_config_value("Configuration", "topbar_type", "New"))
msaa_level_var = tk.StringVar(value=get_config_value("Configuration", "msaa_level", "4x"))
graphics_type_var = tk.StringVar(value=get_config_value("Configuration", "graphics_type", "21"))
max_fps_var = tk.StringVar(value=get_config_value("Configuration", "max_fps", "9999"))
font_size_var = tk.StringVar(value=get_config_value("Configuration", "font_size", "1"))
coregui_transparency_var = tk.StringVar(value=get_config_value("Configuration", "coregui_transparency", "1"))
log_requests_var = tk.BooleanVar(value=get_config_value("Configuration", "log_requests", False))
enable_proxy_var = tk.BooleanVar(value=get_config_value("Configuration", "enable_proxy", False))
show_flags_var = tk.BooleanVar(value=get_config_value("Configuration", "show_flags", False))
log_all_var = tk.BooleanVar(value=get_config_value("Configuration", "log_all", False))
code_assist_var = tk.BooleanVar(value=get_config_value("Configuration", "code_assist", False))
disable_telemetry_var = tk.BooleanVar(value=get_config_value("Configuration", "disable_telemetry", True))
rainbow_ui_var = tk.BooleanVar(value=get_config_value("Configuration", "rainbow_ui", False))
force_high_graphics_var = tk.BooleanVar(value=get_config_value("Configuration", "force_high_graphics", True))
visual_verified_var = tk.BooleanVar(value=get_config_value("Configuration", "visual_verified", False))
old_font_var = tk.BooleanVar(value=get_config_value("Configuration", "old_font", True))
classic_error_var = tk.BooleanVar(value=get_config_value("Configuration", "classic_error", True))
extra_plugins_var = tk.BooleanVar(value=get_config_value("Configuration", "extra_plugins", False))
framerate_settings_var = tk.BooleanVar(value=get_config_value("Configuration", "framerate_settings", False))
disable_updating_var = tk.BooleanVar(value=get_config_value("Configuration", "disable_updating", False))
enable_internal_var = tk.BooleanVar(value=get_config_value("Configuration", "enable_internal", False))

type_settings_one_column = 0
type_settings_one_input_column = 1
type_settings_two_column = 2
type_settings_two_input_column = 3
checkbox_column_one = 4
checkbox_column_two = 5

ttk.Label(root, text="Roblox Studio Manager", font=("Segoe UI", 16)).grid(row=0, column=0, columnspan=6, pady=10)

ttk.Checkbutton(root, text="Optimize Roblox", variable=optimize_roblox_var).grid(row=1, column=0, sticky=tk.W, padx=10)
ttk.Label(root, text="Menu Type:").grid(row=2, column=0, sticky=tk.W, padx=10)
optimize_roblox_cb = ttk.Checkbutton(root, text="Optimize Roblox", variable=optimize_roblox_var)
optimize_roblox_cb.grid(row=1, column=0, sticky=tk.W, padx=10)

ttk.Label(root, text="Menu Type:").grid(row=2, column=type_settings_one_column, sticky=tk.W, padx=10)
combo_menu_type = ttk.Combobox(root, textvariable=menu_type_var, values=["Version 4", "Default", "Version 1", "Version 2", "Version 4"], style="TCombobox", state="readonly")
combo_menu_type.grid(row=2, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Topbar Type:").grid(row=3, column=type_settings_one_column, sticky=tk.W, padx=10)
combo_topbar_type = ttk.Combobox(root, textvariable=topbar_type_var, values=["New", "Old", "New"], style="TCombobox", state="readonly")
combo_topbar_type.grid(row=3, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="MSAA Level:").grid(row=4, column=type_settings_one_column, sticky=tk.W, padx=10)
combo_msaa_level = ttk.Combobox(root, textvariable=msaa_level_var, values=["4x", "Default", "1x", "2x", "4x", "8x"], style="TCombobox", state="readonly")
combo_msaa_level.grid(row=4, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Graphics Type:").grid(row=5, column=type_settings_one_column, sticky=tk.W, padx=10)
combo_graphics_type = ttk.Combobox(root, textvariable=graphics_type_var, values=["21", "Default", "10", "21"], style="TCombobox", state="readonly")
combo_graphics_type.grid(row=5, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Max FPS:").grid(row=6, column=type_settings_one_column, sticky=tk.W, padx=10)
ttk.Entry(root, textvariable=max_fps_var).grid(row=6, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Font Size:").grid(row=7, column=type_settings_one_column, sticky=tk.W, padx=10)
ttk.Entry(root, textvariable=font_size_var).grid(row=7, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="CoreGUI Transparency:").grid(row=8, column=type_settings_one_column, sticky=tk.W, padx=10)
ttk.Entry(root, textvariable=coregui_transparency_var).grid(row=8, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Version:").grid(row=2, column=type_settings_two_column, sticky=tk.W, padx=10)
ttk.Label(root, text=os.path.basename(selected_version)).grid(row=2, column=type_settings_two_input_column, sticky=tk.W, padx=10)

ttk.Label(root, text="Modded:").grid(row=3, column=type_settings_two_column, sticky=tk.W, padx=10)
ttk.Label(root, text=is_modded()).grid(row=3, column=type_settings_two_input_column, sticky=tk.W, padx=10)

ttk.Label(root, text="Channel:").grid(row=4, column=type_settings_two_column, sticky=tk.W, padx=10)
ttk.Label(root, text=get_channel()).grid(row=4, column=type_settings_two_input_column, sticky=tk.W, padx=10)

ttk.Checkbutton(root, text="Log Requests", variable=log_requests_var).grid(row=1, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Enable Proxy", variable=enable_proxy_var).grid(row=2, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Show Flags", variable=show_flags_var).grid(row=3, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Log All", variable=log_all_var).grid(row=4, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Code Assist", variable=code_assist_var).grid(row=5, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Disable Telemetry", variable=disable_telemetry_var).grid(row=6, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Rainbow UI", variable=rainbow_ui_var).grid(row=7, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Force High Graphics", variable=force_high_graphics_var).grid(row=8, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Verified Badge", variable=visual_verified_var).grid(row=9, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Classic Font", variable=old_font_var).grid(row=1, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Classic Error", variable=classic_error_var).grid(row=2, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Extra Plugins", variable=extra_plugins_var).grid(row=3, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Framerate Settings", variable=framerate_settings_var).grid(row=4, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
disable_updates_cb = ttk.Checkbutton(root, text="Disable Updates", variable=disable_updating_var, state = "disabled")
disable_updates_cb.grid(row=5, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Enable Internal", variable=enable_internal_var).grid(row=6, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)

global pluginList
pluginList = []

global plugin_check_states
plugin_check_states = {}

def plugin_editor():
    new_window = tk.Toplevel(root)
    new_window.title("Roblox Studio Manager: Plugin Editor")
    new_window.iconbitmap(application_path + "\\icon.ico")
    
    main_frame = ttk.Frame(new_window)
    main_frame.pack(padx=20, pady=20)
    
    frame = ttk.Frame(main_frame)
    frame.grid(row=0, column=0, padx=20, pady=20)

    plugin_dirs = [
        os.path.join(selected_version, r"BuiltInPlugins\Optimized_Embedded_Signature"),
        os.path.join(selected_version, r"BuiltInStandalonePlugins\Optimized_Embedded_Signature")
    ]
    
    plugins = set()
    
    for dir_path in plugin_dirs:
        if os.path.exists(dir_path):
            for plugin in os.listdir(dir_path):
                plugins.add(plugin)
    
    sorted_plugins = sorted(plugins)
    
    row = 0
    column = 0
    
    global pluginList
    pluginList.clear()
    for i, plugin in enumerate(sorted_plugins):
        if plugin not in plugin_check_states:
            plugin_check_states[plugin] = tk.BooleanVar(value=get_config_value("Plugins", plugin, True))
        var = plugin_check_states[plugin]
        pluginList.append(plugin)
        chk = ttk.Checkbutton(frame, text=plugin.replace(".rbxm", ""), variable=var, onvalue=True, offvalue=False)
        chk.grid(row=row, column=column, sticky='w', padx=5, pady=5)

        row += 1 
        if (i + 1) % 20 == 0:
            row = 0
            column += 1
    
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=0, pady=(0, 20), sticky="n")
    
    ttk.Button(button_frame, text="Enable All", command=enable_all).grid(row=0, column=0, pady=(20, 0))
    ttk.Button(button_frame, text="Disable All", command=disable_all).grid(row=0, column=1, pady=(20, 0), padx=(6, 0))
    ttk.Button(button_frame, text="Reset to Settings", command=reset_checkboxes).grid(row=0, column=2, pady=(20, 0), padx=(6, 0))

def enable_all():
    for plugin in plugin_check_states:
        plugin_check_states[plugin].set(value = True)

def disable_all():
    for plugin in plugin_check_states:
        plugin_check_states[plugin].set(value = False)

def reset_checkboxes():
    enable_all()
    for plugin in plugin_check_states:
        try:
            plugin_check_states[plugin].set(value = Config["Plugins"][str(plugin).lower()])
        except:
            pass

def update_plugin_state(plugin):
    state = plugin_check_states[plugin].get()
    if state:
        enable_plugin(plugin)
    else:
        disable_plugin(plugin)

def enable_plugin(plugin):
    plugin_dirs = [
        os.path.join(selected_version, "BuiltInPlugins", "Optimized_Embedded_Signature"),
        os.path.join(selected_version, "BuiltInStandalonePlugins", "Optimized_Embedded_Signature")
    ]

    for plugin_dir in plugin_dirs:
        plugin_path = os.path.join(plugin_dir, plugin)
        if os.path.exists(plugin_path):
            with open(plugin_path, 'r+b') as f:
                content = f.read()
                if content[-8:] == b"DISABLED":
                    f.seek(-8, os.SEEK_END)
                    f.truncate()
            break

def disable_plugin(plugin):
    plugin_dirs = [
        os.path.join(selected_version, "BuiltInPlugins", "Optimized_Embedded_Signature"),
        os.path.join(selected_version, "BuiltInStandalonePlugins", "Optimized_Embedded_Signature")
    ]

    for plugin_dir in plugin_dirs:
        plugin_path = os.path.join(plugin_dir, plugin)
        if os.path.exists(plugin_path):
            with open(plugin_path, 'r+b') as f:
                content = f.read()
                if b"DISABLED" not in content:
                    f.seek(0)
                    f.write(content + b"DISABLED")
            break

def reset_states():
    plugin_dirs = [
        os.path.join(selected_version, "BuiltInPlugins", "Optimized_Embedded_Signature"),
        os.path.join(selected_version, "BuiltInStandalonePlugins", "Optimized_Embedded_Signature")
    ]

    for plugin_dir in plugin_dirs:
        for plugin in os.listdir(plugin_dir):
            plugin_path = os.path.join(plugin_dir, plugin)
            with open(plugin_path, 'r+b') as f:
                content = f.read()
                if b"DISABLED" in content:
                    content = content.replace(b"DISABLED", b"")
                    f.seek(0)
                    f.write(content)

def check_disabled_state(plugin):
    plugin_dirs = [
        os.path.join(selected_version, "BuiltInPlugins", "Optimized_Embedded_Signature"),
        os.path.join(selected_version, "BuiltInStandalonePlugins", "Optimized_Embedded_Signature")
    ]

    for plugin_dir in plugin_dirs:
        plugin_path = os.path.join(plugin_dir, plugin)
        if os.path.exists(plugin_path):
            with open(plugin_path, 'rb') as f:
                content = f.read()
                if b"DISABLED" in content:
                    return True
            break

    return False

            
button_frame_top = ttk.Frame(root)
button_frame_top.grid(row=10, column=0, columnspan=6, pady=(0, 1), sticky="n")
button_frame_bottom = ttk.Frame(root)
button_frame_bottom.grid(row=11, column=0, columnspan=6, sticky="n")

ttk.Button(button_frame_top, text="Apply Settings", command=update_settings).grid(row=10, column=0, pady=(20, 0))
ttk.Button(button_frame_top, text="Reset Configuration", command=reset_fflags).grid(row=10, column=1, pady=(20, 0), padx=(6, 0))
ttk.Button(button_frame_top, text="Installation Folder", command=installation_folder).grid(row=10, column=2, pady=(20, 0), padx=(6, 0))
ttk.Button(button_frame_bottom, text="Launch Studio", command=launch_studio).grid(row=11, column=0, pady=(6, 20))
ttk.Button(button_frame_bottom, text="Update Studio", command=update_studio).grid(row=11, column=1, pady=(6, 20), padx=(6, 0))
ttk.Button(button_frame_bottom, text="Plugin Editor", command=plugin_editor).grid(row=11, column=2, pady=(6, 20), padx=(6, 0))

label = tk.Label(root, font=("Segoe UI", 12), text="Fireblade", padx=2, pady = 2)

label.place(relx=1.0, rely=1.0, anchor='se')

if not check_internet():
    optimize_roblox_cb.configure(state = "disabled")
    disable_updates_cb.configure(state = "disabled")

sv_ttk.set_theme("dark")
root.resizable(False, False)
root.iconbitmap(application_path + "\\icon.ico")

root.mainloop()
