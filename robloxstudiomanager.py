import os
import re
import sys
import json
import time
import ctypes
import psutil
import sv_ttk
import zipfile
import requests
import threading
import subprocess
import tkinter as tk
from io import BytesIO
import xml.etree.ElementTree as ET
from tkinter import ttk, messagebox
import configparser as ConfigParser

if getattr(sys, "frozen", False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

totalFlags = {}

try:
    fvariables_text = requests.get("https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/FVariables.txt").text
    fvariables_flags = {line.split(" ")[-1]: False for line in fvariables_text.splitlines() if line}
    client_app_settings = requests.get("https://clientsettings.roblox.com/v2/settings/application/PCDesktopClient").json()["applicationSettings"]
    for key, value in client_app_settings.items():
            totalFlags[key] = value
    for key, value in fvariables_flags.items():
        if key not in totalFlags:
            totalFlags[key] = value
except Exception:
    pass

global selected_version
selected_version = None

optimizer = "https://raw.githubusercontent.com/rbxflags/Flags/main/ClientAppSettings.json"

versions_dir = os.path.join(os.environ["LOCALAPPDATA"], "Roblox", "Versions")

max_files_count = 0

for version in os.listdir(versions_dir):
    version_dir = os.path.join(versions_dir, version)

    exe_path = os.path.join(version_dir, "RobloxStudioBeta.exe")
    if os.path.exists(exe_path):

        num_files = len([name for name in os.listdir(version_dir)])

        if num_files > max_files_count:
            max_files_count = num_files
            selected_version = version_dir

if not selected_version:
    versions_dir = os.path.join(os.environ["PROGRAMFILES(X86)"], "Roblox", "Versions")

    max_files_count = 0

    for version in os.listdir(versions_dir):
        version_dir = os.path.join(versions_dir, version)

        exe_path = os.path.join(version_dir, "RobloxStudioBeta.exe")
        if os.path.exists(exe_path):

            num_files = len([name for name in os.listdir(version_dir)])

            if num_files > max_files_count:
                max_files_count = num_files
                selected_version = version_dir

def is_modded():
    if os.path.exists(os.path.join(selected_version, "ClientSettings")):
        return "Yes"
    else:
        return "No"

def get_channel():
    status = "Offline"
    try: 
        status = requests.get("https://clientsettings.roblox.com/v2/user-channel?binaryType=WindowsStudio64").json()["channelName"]
    except Exception:
        pass
    return status

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

def find_latest_studio_version(lines):
    latestStudio = ""
    for line in lines.splitlines():
        if "Studio64" in line:
            latestStudio = line
    return latestStudio

def reset_fflags():
    result = messagebox.askyesno("Roblox Studio Manager", "Are you sure you want to reset your FFlags?")
    if result:
        app_settings_path = os.path.join(selected_version, "ClientSettings", "ClientAppSettings.json")
        if os.path.exists(os.path.join(selected_version, "ClientSettings")):
            open(app_settings_path, "w").close()
            open(app_settings_path, "w+").write("{}")

def installation_folder():
    subprocess.Popen(f"explorer \"{selected_version}", shell = True)

def launch_studio_async():
    subprocess.Popen(f"{selected_version}\RobloxStudioBeta.exe", shell = True)

def update_studio_async():
    subprocess.Popen(f"{selected_version}\RobloxStudioInstaller.exe", shell = True)

def update_settings():
    t = threading.Thread(target=update_settings_async)
    t.start()

def launch_studio():
    t = threading.Thread(target=launch_studio_async)
    t.start()

def update_studio():
    t = threading.Thread(target=update_studio_async)
    t.start()

def fluent_background():
    hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
    if fluent_ui_var.get() == True:
        sv_ttk.set_theme("dark")
        root.wm_attributes("-transparentcolor", "#1c1c1c")
        root.update_idletasks()
        apply_blur_effect(hwnd)
    elif fluent_ui_var.get() == False:
        sv_ttk.set_theme("dark")
        root.wm_attributes("-transparentcolor", "#000001")
        remove_blur_effect(hwnd)
        root.configure(background="#1c1c1c")
        root.attributes("-alpha", 1.0)

Config = ConfigParser.ConfigParser()

def update_settings_async():
    studio_id = studio_running()

    if studio_id:
        result = messagebox.askyesno("Roblox Studio Manager", "Roblox Studio is currently running. Do you want to close it to apply the changes?")
        if result:
            psutil.Process(studio_id).kill()
            psutil.Process(studio_id).wait()

    checkboxes = [
        optimize_roblox_var, log_requests_var, enable_proxy_var, show_flags_var,
        log_all_var, minimize_logging_var, code_assist_var, disable_telemetry_var,
        rainbow_ui_var, force_high_graphics_var, visual_verified_var, old_font_var,
        classic_error_var, extra_plugins_var, faster_menu_var, cleaner_ui_var, 
        performance_mode_var, foundation_colors_var, disable_updating_var, enable_internal_var
    ]

    total_checked = sum(var.get() for var in checkboxes if var.get())
    progressbar.configure(maximum = total_checked + 0.0000001)

    start_time = time.time()

    optimize_roblox = optimize_roblox_var.get()
    menu_type = menu_type_var.get()
    topbar_type = topbar_type_var.get()
    msaa_level = msaa_level_var.get()
    graphics_type = graphics_type_var.get()
    max_fps = max_fps_var.get()
    font_size = font_size_var.get()
    coregui_transparency = coregui_transparency_var.get()
    rendering_engine = rendering_engine_var.get()
    scroll_delta = scroll_delta_var.get()
    log_requests = log_requests_var.get()
    enable_proxy = enable_proxy_var.get()
    enable_internal = enable_internal_var.get()
    show_flags = show_flags_var.get()
    log_all = log_all_var.get()
    minimize_logging = minimize_logging_var.get()
    code_assist = code_assist_var.get()
    disable_telemetry = disable_telemetry_var.get()
    rainbow_ui = rainbow_ui_var.get()
    force_high_graphics = force_high_graphics_var.get()
    visual_verified = visual_verified_var.get()
    old_font = old_font_var.get()
    classic_error = classic_error_var.get()
    disable_updating = disable_updating_var.get()
    extra_plugins = extra_plugins_var.get()
    fluent_ui = fluent_ui_var.get()
    performance_mode = performance_mode_var.get()
    faster_menu = faster_menu_var.get()
    cleaner_ui = cleaner_ui_var.get()
    foundation_colors = foundation_colors_var.get()
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
    Config["Configuration"]["rendering_engine"] = str(rendering_engine_var.get())
    Config["Configuration"]["scroll_delta"] = str(scroll_delta_var.get())
    Config["Configuration"]["log_requests"] = str(log_requests_var.get())
    Config["Configuration"]["enable_proxy"] = str(enable_proxy_var.get())
    Config["Configuration"]["enable_internal"] = str(enable_internal_var.get())
    Config["Configuration"]["show_flags"] = str(show_flags_var.get())
    Config["Configuration"]["log_all"] = str(log_all_var.get())
    Config["Configuration"]["minimize_logging"] = str(minimize_logging_var.get())
    Config["Configuration"]["code_assist"] = str(code_assist_var.get())
    Config["Configuration"]["disable_telemetry"] = str(disable_telemetry_var.get())
    Config["Configuration"]["rainbow_ui"] = str(rainbow_ui_var.get())
    Config["Configuration"]["force_high_graphics"] = str(force_high_graphics_var.get())
    Config["Configuration"]["visual_verified"] = str(visual_verified_var.get())
    Config["Configuration"]["old_font"] = str(old_font_var.get())
    Config["Configuration"]["classic_error"] = str(classic_error_var.get())
    Config["Configuration"]["disable_updating"] = str(disable_updating_var.get())
    Config["Configuration"]["extra_plugins"] = str(extra_plugins_var.get())
    Config["Configuration"]["fluent_ui"] = str(fluent_ui_var.get())
    Config["Configuration"]["performance_mode"] = str(performance_mode_var.get())
    Config["Configuration"]["faster_menu"] = str(faster_menu_var.get())
    Config["Configuration"]["cleaner_ui"] = str(cleaner_ui_var.get())
    Config["Configuration"]["foundation_colors"] = str(foundation_colors_var.get())
    for plugin, state in plugin_check_states.items():
        if not state.get():
            Config["Plugins"][plugin] = str(state.get())

    with open("robloxstudiomanagerconfig.ini", "w") as configfile:
        Config.write(configfile)

    flags = {
        "FFlagDebugGraphicsPreferD3D11": "true",  
        "DFIntTaskSchedulerTargetFps": int(max_fps),  
        "FFlagTaskSchedulerLimitTargetFpsTo2402": "false", 
        "FIntFontSizePadding": int(font_size),
        "FIntScrollWheelDeltaAmount": int(scroll_delta)
    }

    internal_signature = b"\x41\x38\x9E\x78\x01\x00\x00\x74\x05\xE8"
    internal_patch = b"\x41\x38\x9E\x78\x01\x00\x00\x90\x90\xE8"
    watermark_signature = b"\x53\x74\x75\x64\x69\x6F\x2E\x41\x70\x70\x2E\x41\x62\x6F\x75\x74\x53\x74\x75\x64\x69\x6F\x44\x69\x61\x6C\x6F\x67\x2E\x43\x6F\x6E\x74\x61\x63\x74\x55\x73\x2C\x2C\x2C\x43\x6F\x6E\x74\x61\x63\x74\x20\x55\x73\x2C\x43\x6F\x6E\x74\x61\x63\x74\x20\x55\x73"
    watermark_patch = b"\x53\x74\x75\x64\x69\x6F\x2E\x41\x70\x70\x2E\x41\x62\x6F\x75\x74\x53\x74\x75\x64\x69\x6F\x44\x69\x61\x6C\x6F\x67\x2E\x43\x6F\x6E\x74\x61\x63\x74\x55\x73\x2C\x2C\x2C\x4D\x6F\x64\x64\x65\x64\x20\x52\x53\x4D\x2C\x4D\x6F\x64\x64\x65\x64\x20\x52\x53\x4D"

    if menu_type == "Version 1":
        flags["FFlagDisableNewIGMinDUA"] = "true"  
        flags["FFlagEnableInGameMenuControls"] = "false"  
        flags["FFlagEnableMenuControlsABTest"] = "false"  
        flags["FFlagEnableMenuModernizationABTest"] = "false"  
        flags["FFlagEnableMenuModernizationABTest2"] = "false"  
        flags["FFlagEnableInGameMenuChromeABTest3"] = "false"
        flags["FFlagEnableV3MenuABTest3"] = "false"  
    elif menu_type == "Version 2":
        flags["FFlagDisableNewIGMinDUA"] = "false"  
        flags["FFlagEnableInGameMenuControls"] = "false"  
        flags["FFlagEnableMenuControlsABTest"] = "false"  
        flags["FFlagEnableMenuModernizationABTest"] = "false"  
        flags["FFlagEnableMenuModernizationABTest2"] = "false" 
        flags["FFlagEnableInGameMenuChromeABTest3"] = "false"
        flags["FFlagEnableV3MenuABTest3"] = "false"  
    elif menu_type == "Version 4":
        flags["FFlagDisableNewIGMinDUA"] = "true"  
        flags["FFlagEnableInGameMenuControls"] = "true"  
        flags["FFlagEnableMenuControlsABTest"] = "false"  
        flags["FFlagEnableMenuModernizationABTest"] = "false"  
        flags["FFlagEnableMenuModernizationABTest2"] = "false"  
        flags["FFlagEnableInGameMenuChromeABTest3"] = "false"
        flags["FFlagEnableV3MenuABTest3"] = "false"  

    if topbar_type == "Old":
        flags["FFlagEnableInGameMenuChrome"] = "false"  
        flags["FFlagEnableMenuControlsABTest"] = "false"
        flags["FFlagEnableMenuModernizationABTest"] = "false"  
        flags["FFlagEnableMenuModernizationABTest2"] = "false" 
        flags["FFlagEnableInGameMenuChromeABTest3"] = "false"
    elif topbar_type == "New":
        flags["FFlagEnableInGameMenuChrome"] = "true"  
        flags["FFlagEnableChromePinnedChat"] = "false" 

    if log_requests:
        flags["DFLogHttpTraceLight"] = 12
        progressbar.step(1)
    else:
        flags["DFLogHttpTraceLight"] = 6

    if enable_proxy:
        flags["FFlagStudioReEnableNetworkProxy_Dev"] = "true"  
        flags["DFFlagHideProxySettings"] = "false"  
        flags["DFFlagDebugEnableHttpProxy"] = "true"  
        progressbar.step(1)
    else:
        flags["FFlagStudioReEnableNetworkProxy_Dev"] = "false"  
        flags["DFFlagHideProxySettings"] = "true"  
        flags["DFFlagDebugEnableHttpProxy"] = "false"  

    if msaa_level == "1x":
        flags["DebugForceMSAASamples"] = 1  
    elif msaa_level == "2x":
        flags["DebugForceMSAASamples"] = 2  
    elif msaa_level == "4x":
        flags["DebugForceMSAASamples"] = 4  
    elif msaa_level == "8x":
        flags["DebugForceMSAASamples"] = 8  

    if graphics_type == "10":
        flags["FFlagFixGraphicsQuality"] = "false"  
    elif graphics_type == "21":
        flags["FFlagFixGraphicsQuality"] = "true"  

    if rendering_engine == "DirectX 11":
        flags["FFlagDebugGraphicsDisableOpenGL"] = "true"
        flags["FFlagDebugGraphicsDisableVulkan"] = "true"
        flags["FFlagDebugGraphicsDisableVulkan11"] = "true"
        flags["FFlagDebugGraphicsPreferD3D11"] = "true"
        flags["FFlagDebugGraphicsPreferVulkan"] = "false"
        flags["FFlagDebugGraphicsPreferD3D11FL10"] = "false"
    elif rendering_engine == "DirectX 10":
        flags["FFlagDebugGraphicsDisableOpenGL"] = "true"
        flags["FFlagDebugGraphicsDisableVulkan"] = "true"
        flags["FFlagDebugGraphicsDisableVulkan11"] = "true"
        flags["FFlagDebugGraphicsPreferD3D11FL10"] = "true"
        flags["FFlagDebugGraphicsDisableDirect3D11"] = "false"
        flags["FFlagDebugGraphicsPreferVulkan"] = "false"
        flags["FFlagDebugGraphicsPreferD3D11"] = "false"
    elif rendering_engine == "Vulkan":
        flags["FFlagDebugGraphicsDisableDirect3D11"] = "true"
        flags["FFlagDebugGraphicsDisableOpenGL"] = "true"
        flags["FFlagDebugGraphicsPreferVulkan"] = "true"
        flags["FFlagDebugGraphicsDisableVulkan"] = "false"
        flags["FFlagDebugGraphicsDisableVulkan11"] = "false"
        flags["FFlagDebugGraphicsPreferD3D11"] = "false"
        flags["FFlagDebugGraphicsPreferD3D11FL10"] = "false"
    elif rendering_engine == "Metal":
        flags["FFlagDebugGraphicsDisableDirect3D11"] = "true"
        flags["FFlagDebugGraphicsDisableOpenGL"] = "true"
        flags["FFlagDebugGraphicsDisableVulkan"] = "true"
        flags["FFlagDebugGraphicsDisableVulkan11"] = "true"
        flags["FFlagDebugGraphicsPreferMetal"] = "true"
        flags["FFlagDebugGraphicsPreferVulkan"] = "false"
        flags["FFlagDebugGraphicsPreferD3D11"] = "false"
        flags["FFlagDebugGraphicsPreferOpenGL"] = "false"
        flags["FFlagDebugGraphicsPreferD3D11FL10"] = "false"
    elif rendering_engine == "OpenGL":
        flags["FFlagDebugGraphicsDisableDirect3D11"] = "true"
        flags["FFlagDebugGraphicsDisableVulkan"] = "true"
        flags["FFlagDebugGraphicsDisableVulkan11"] = "true"
        flags["FFlagDebugGraphicsPreferOpenGL"] = "true"
        flags["FFlagDebugGraphicsForceGL2"] = "true"
        flags["FFlagDebugGraphicsDisableOpenGL"] = "false"
        flags["FFlagDebugGraphicsPreferVulkan"] = "false"
        flags["FFlagDebugGraphicsPreferD3D11"] = "false"
        flags["FFlagDebugGraphicsPreferD3D11FL10"] = "false"

    if log_all:
        for flag, value in totalFlags.items():
            if (flag.startswith("FLog") or flag.startswith("DFLog") or flag.startswith("SFLog")) and ("FLogStudioQtCategoryLog_default" != flag and "DFLogMaxJoinDataSizeKB" != flag and "DFLogHttpCurlProxyHostAndPort" not in flag and "FLogDataModelPatcherRevokedSignatureTypes" != flag and "DFLogHttpUniverseBlacklist" != flag and "FLogAppConfigurationOverrideAppPolicy" != flag and "FLogDebugShowFlagState" != flag and "FLogDebugCommaSepBuiltInPluginsToDebug" != flag):
                flags[flag] = 12
        progressbar.step(1)

    if minimize_logging:
        for flag, value in totalFlags.items():
            if (flag.startswith("FLog") or flag.startswith("DFLog") or flag.startswith("SFLog")) and ("FLogStudioQtCategoryLog_default" != flag and "DFLogMaxJoinDataSizeKB" != flag and "DFLogHttpCurlProxyHostAndPort" not in flag and "FLogDataModelPatcherRevokedSignatureTypes" != flag and "DFLogHttpUniverseBlacklist" != flag and "FLogAppConfigurationOverrideAppPolicy" != flag and "FLogDebugShowFlagState" != flag and "FLogDebugCommaSepBuiltInPluginsToDebug" != flag):
                flags[flag] = 0
        progressbar.step(1)

    if code_assist:
        flags["FFlagRelatedScriptsCodeAssist"] = "true"
        flags["FFlagCodeAssistFeature"] = "true"
        flags["FFlagAICOChatBot"] = "true"
        progressbar.step(1)

    if disable_telemetry:
        for flag, value in totalFlags.items():
            if "analytics" in flag.lower() or "telemetry" in flag.lower():
                if flag.startswith("FFlag") or flag.startswith("DFFlag") or flag.startswith("SFlag"):
                    flags[flag] = "false"
                elif flag.startswith("FString") or flag.startswith("DFString") or flag.startswith("SFString"):
                    flags[flag] = "https://0.0.0.0"
                else:
                    flags[flag] = "0"
                    if "interval" in flag.lower():
                        flags[flag] = "2147483647"
        progressbar.step(1)

    if rainbow_ui:
        flags["FFlagDebugDisplayUnthemedInstances"] = "true"
        progressbar.step(1)

    if force_high_graphics:
        flags["DFFlagDisableDPIScale"] = "true"
        flags["FIntTextureCompositorLowResFactor"] = 4
        flags["DFFlagEnableRequestAsyncCompression"] = "false"
        progressbar.step(1)

    if visual_verified:
        flags["FFlagOverridePlayerVerifiedBadge"] = "true"
        progressbar.step(1)

    if old_font:
        flags["FFlagUIBloxDevUseNewFontNameMapping"] = "false"
        flags["FFlagEnableNewFontNameMappingABTest2"] = "false"
        flags["FFlagSwitchGothamFontToBuilderSans"] = "false"
        flags["FFlagAddGothamToLegacyContent"] = "false"
        zip_path = os.path.join(selected_version, "content", "fonts", "GothamFont.zip")
        try:
            response = requests.get("https://github.com/Firebladedoge229/GothamFont/archive/refs/heads/main.zip", stream=True)
            with open(zip_path, "wb") as output:
                output.write(response.content)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                target_dir = None
                for file_info in zip_ref.infolist():
                    if file_info.is_dir():
                        target_dir = file_info.filename
                        break

                if target_dir:
                    for file_info in zip_ref.infolist():
                        if file_info.filename.startswith(target_dir) and (file_info.filename.endswith(".ttf") or file_info.filename.endswith(".otf")):
                            filename = os.path.basename(file_info.filename)
                            dest_path = os.path.join(selected_version, "content", "fonts", filename)
                            with zip_ref.open(file_info) as source, open(dest_path, "wb") as target:
                                target.write(source.read())

            os.remove(zip_path)
        except Exception:
            pass
            
        progressbar.step(1)

    if classic_error:
        flags["FFlagErrorPromptResizesHeight"] = "false"
        progressbar.step(1)

    if extra_plugins:
        flags["FFlagEnableRibbonPlugin"] = "true"
        flags["FFlagDebugAvatarInternalToolsPlugin"] = "true"
        flags["NestedPackagePublisherPlugin"] = "true"
        flags["DebugEnableBootcampPlugin"] = "true"
        flags["RetireAudioDiscoveryPlugin"] = "false"
        progressbar.step(1)

    if faster_menu:
        flags["FFlagInGameMenuV1FadeBackgroundAnimation"]  = "true"
        progressbar.step(1)

    if cleaner_ui:
        flags["FFlagChatTranslationLaunchEnabled"] = "false"
        flags["FIntV1MenuLanguageSelectionFeaturePerMillageRollout"] = "0"
        flags["FFlagDisablePlayerListDisplayCloseBtn"] = "true"
        flags["FFlagEnableAccessibilitySettingsAPIV2"] = "false"
        flags["FFlagEnableAccessibilitySettingsEffectsInCoreScripts2"] = "false"
        flags["FFlagEnableAccessibilitySettingsEffectsInExperienceChat"] = "false"
        flags["FFlagEnableAccessibilitySettingsInExperienceMenu2"] = "false"
        flags["FFlagGameBasicSettingsFramerateCap5"] = "false"
        flags["FFlagEnablePreferredTextSizeScale"] = "false"
        flags["FFlagEnablePreferredTextSizeSettingInMenus2"] = "false"
        progressbar.step(1)

    if performance_mode:
       performance_flags = requests.get("https://gist.github.com/Firebladedoge229/917827fdd94bbec986b503fafb7fb8ba").text
       start_pos = performance_flags.find("Compiled List")
       if start_pos != -1:
            after = performance_flags[start_pos:]

            match = re.search(r'<pre>(.*?)</pre>', after, re.DOTALL)
            if match:
                string = match.group(1)
                cleaned_string = re.sub(r'<.*?>', '', string)
                cleaned_string = re.sub(r'^[ \t]+', '', cleaned_string, flags=re.MULTILINE)
                position = cleaned_string.rfind(",")
                if position != -1:
                    cleaned_string = cleaned_string[:position] + cleaned_string[position+1:]
                data = json.loads(cleaned_string)
                for k, v in data.items():
                    if k != "DFIntTaskSchedulerTargetFPS":
                        flags[k] = v
                progressbar.step(1)

    if foundation_colors:
        flags["FFlagLuaAppEnableFoundationColors"] = "true"
        progressbar.step(1)
    
    if enable_internal:
        flags["FFlagInternalDebugWidgetSleepButton"] = "true"
        progressbar.step(1)

    if show_flags:
        flag_list = ""
        for flag in flags:
            flag_list += flag + ","
        flags["FStringDebugShowFlagState"] = flag_list[:-1]
        progressbar.step(1)
    
    if selected_version is not None:
        app_settings_path = os.path.join(selected_version, "ClientSettings", "ClientAppSettings.json")

        if not os.path.exists(os.path.join(selected_version, "ClientSettings")):
            os.makedirs(os.path.join(selected_version, "ClientSettings"))

        open(app_settings_path, "w").close()
        open(app_settings_path, "w+").write("{}")

        with open(app_settings_path, "r+") as f:
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
            exe_path = os.path.join(selected_version, "RobloxStudioBeta.exe")
            with open(exe_path, "r+b") as f:
                content = f.read()
                index = content.find(internal_signature)
                if index != -1:
                    f.seek(index)
                    f.write(internal_patch)
        elif enable_internal == False:
            exe_path = os.path.join(selected_version, "RobloxStudioBeta.exe")
            with open(exe_path, "r+b") as f:
                content = f.read()
                index = content.find(internal_patch)
                if index != -1:
                    f.seek(index)
                    f.write(internal_signature)

        if disable_updating:
            deployHistory = requests.get("https://setup.rbxcdn.com/DeployHistory.txt").text
            result = find_version_line(os.path.basename(selected_version), deployHistory)
            latest_version = find_latest_studio_version(deployHistory)
            result = re.search(r"git hash:\s*(\d+\.\d+\.\d+\.\d+)", result).group().replace("git hash: ", "")
            latest_result = re.search(r"git hash:\s*(\d+\.\d+\.\d+\.\d+)", latest_version).group().replace("git hash: ", "")
            if len(result) != len(latest_result):
                messagebox.showinfo("Roblox Studio Manager", "The current version and latest version are not the same size. Due to hex limitations, you cannot disable updating on this version.")
            else:
                result = bytes.fromhex("".join(format(ord(char), "02X") for char in result))
                patch = bytes.fromhex("".join(format(ord(char), "02X") for char in latest_result))

                exe_path = os.path.join(selected_version, "RobloxStudioBeta.exe")
                with open(exe_path, "r+b") as f:
                    content = f.read()
                    index = content.find(result)
                    if index != -1:
                        f.seek(index)
                        f.write(patch)
            progressbar.step(1)

            exe_path = os.path.join(selected_version, "RobloxStudioBeta.exe")
            with open(exe_path, "r+b") as f:
                content = f.read()
                index = content.find(watermark_signature)
                if index != -1:
                    f.seek(index)
                    f.write(watermark_patch)

        tree = ET.parse(os.path.join(os.path.join(os.environ["LOCALAPPDATA"], "Roblox"), "GlobalBasicSettings_13_Studio.xml"))
        root = tree.getroot()

        for item in root.findall(".//Item[@class=\"UserGameSettings\"]"):
            for prop in item.find("Properties"):
                if prop.tag == "float" and prop.attrib.get("name") == "PreferredTransparency":
                    prop.text = str((4 / 99) * float(coregui_transparency) + (95 / 99))
                    break

        tree.write(os.path.join(os.path.join(os.environ["LOCALAPPDATA"], "Roblox"), "GlobalBasicSettings_13_Studio.xml"), encoding="utf-8", xml_declaration=True)

        for plugin in pluginList:
            update_plugin_state(plugin)

        end_time = time.time()

        result = messagebox.showinfo("Roblox Studio Manager", f"Successfully patched in {str(round(end_time - start_time, 2))}ms.")
        progressbar["value"] = 0

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

class ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_int),
        ("AnimationId", ctypes.c_int)
    ]

class WINCOMPATTRDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.POINTER(ACCENT_POLICY)),
        ("SizeOfData", ctypes.c_size_t)
    ]

def apply_blur_effect(hwnd):
    accent = ACCENT_POLICY()
    accent.AccentState = 3

    data = WINCOMPATTRDATA()
    data.Attribute = 19
    data.Data = ctypes.pointer(accent)
    data.SizeOfData = ctypes.sizeof(accent)

    ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.pointer(data))

def remove_blur_effect(hwnd):
    accent = ACCENT_POLICY()
    accent.AccentState = 0

    data = WINCOMPATTRDATA()
    data.Attribute = 13
    data.Data = ctypes.pointer(accent)
    data.SizeOfData = ctypes.sizeof(accent)

    ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.pointer(data))

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
rendering_engine_var = tk.StringVar(value=get_config_value("Configuration", "rendering_engine", "DirectX 11"))
scroll_delta_var = tk.StringVar(value=get_config_value("Configuration", "scroll_delta", "150"))
log_requests_var = tk.BooleanVar(value=get_config_value("Configuration", "log_requests", False))
enable_proxy_var = tk.BooleanVar(value=get_config_value("Configuration", "enable_proxy", False))
show_flags_var = tk.BooleanVar(value=get_config_value("Configuration", "show_flags", False))
log_all_var = tk.BooleanVar(value=get_config_value("Configuration", "log_all", False))
minimize_logging_var = tk.BooleanVar(value=get_config_value("Configuration", "minimize_logging", False))
code_assist_var = tk.BooleanVar(value=get_config_value("Configuration", "code_assist", False))
disable_telemetry_var = tk.BooleanVar(value=get_config_value("Configuration", "disable_telemetry", True))
rainbow_ui_var = tk.BooleanVar(value=get_config_value("Configuration", "rainbow_ui", False))
force_high_graphics_var = tk.BooleanVar(value=get_config_value("Configuration", "force_high_graphics", True))
visual_verified_var = tk.BooleanVar(value=get_config_value("Configuration", "visual_verified", False))
old_font_var = tk.BooleanVar(value=get_config_value("Configuration", "old_font", True))
classic_error_var = tk.BooleanVar(value=get_config_value("Configuration", "classic_error", True))
extra_plugins_var = tk.BooleanVar(value=get_config_value("Configuration", "extra_plugins", False))
faster_menu_var = tk.BooleanVar(value=get_config_value("Configuration", "faster_menu", False))
cleaner_ui_var = tk.BooleanVar(value=get_config_value("Configuration", "cleaner_ui", True))
fluent_ui_var = tk.BooleanVar(value=get_config_value("Configuration", "fluent_ui", False))
performance_mode_var = tk.BooleanVar(value=get_config_value("Configuration", "performance_mode", False))
foundation_colors_var = tk.BooleanVar(value=get_config_value("Configuration", "foundation_colors", False))
disable_updating_var = tk.BooleanVar(value=get_config_value("Configuration", "disable_updating", False))
enable_internal_var = tk.BooleanVar(value=get_config_value("Configuration", "enable_internal", False))

if fluent_ui_var.get() == True:
    fluent_background()

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
combo_menu_type = ttk.Combobox(root, textvariable=menu_type_var, values=["Version 1", "Version 2", "Version 4"], style="TCombobox", state="readonly")
combo_menu_type.grid(row=2, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Topbar Type:").grid(row=3, column=type_settings_one_column, sticky=tk.W, padx=10)
combo_topbar_type = ttk.Combobox(root, textvariable=topbar_type_var, values=["Old", "New"], style="TCombobox", state="readonly")
combo_topbar_type.grid(row=3, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="MSAA Level:").grid(row=4, column=type_settings_one_column, sticky=tk.W, padx=10)
combo_msaa_level = ttk.Combobox(root, textvariable=msaa_level_var, values=["1x", "2x", "4x", "8x"], style="TCombobox", state="readonly")
combo_msaa_level.grid(row=4, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Graphics Type:").grid(row=5, column=type_settings_one_column, sticky=tk.W, padx=10)
combo_graphics_type = ttk.Combobox(root, textvariable=graphics_type_var, values=["10", "21"], style="TCombobox", state="readonly")
combo_graphics_type.grid(row=5, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Max FPS:").grid(row=6, column=type_settings_one_column, sticky=tk.W, padx=10)
ttk.Entry(root, textvariable=max_fps_var).grid(row=6, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Font Size:").grid(row=7, column=type_settings_one_column, sticky=tk.W, padx=10)
ttk.Entry(root, textvariable=font_size_var).grid(row=7, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="CoreGUI Transparency:").grid(row=8, column=type_settings_one_column, sticky=tk.W, padx=10)
ttk.Entry(root, textvariable=coregui_transparency_var).grid(row=8, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Graphics Renderer:").grid(row=9, column=type_settings_one_column, sticky=tk.W, padx=10)
combo_graphics_type = ttk.Combobox(root, textvariable=rendering_engine_var, values=["DirectX 11", "DirectX 10", "Vulkan", "Metal", "OpenGL"], style="TCombobox", state="readonly")
combo_graphics_type.grid(row=9, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Scroll Delta:").grid(row=10, column=type_settings_one_column, sticky=tk.W, padx=10)
ttk.Entry(root, textvariable=scroll_delta_var).grid(row=10, column=type_settings_one_input_column, sticky="ew")

ttk.Label(root, text="Version:").grid(row=2, column=type_settings_two_column, sticky=tk.W, padx=10)
ttk.Label(root, text=os.path.basename(selected_version)).grid(row=2, column=type_settings_two_input_column, sticky=tk.W, padx=10)

ttk.Label(root, text="Modded:").grid(row=3, column=type_settings_two_column, sticky=tk.W, padx=10)
ttk.Label(root, text=is_modded()).grid(row=3, column=type_settings_two_input_column, sticky=tk.W, padx=10)

ttk.Label(root, text="Channel:").grid(row=4, column=type_settings_two_column, sticky=tk.W, padx=10)
ttk.Label(root, text=get_channel()).grid(row=4, column=type_settings_two_input_column, sticky=tk.W, padx=10)

ttk.Checkbutton(root, text="Log Requests", variable=log_requests_var).grid(row=1, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Enable Proxy", variable=enable_proxy_var).grid(row=2, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Show Flags", variable=show_flags_var).grid(row=3, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
log_all_cb = ttk.Checkbutton(root, text="Log All", variable=log_all_var)
log_all_cb.grid(row=4, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
minimize_logging_cb = ttk.Checkbutton(root, text="Minimize Logging", variable=minimize_logging_var)
minimize_logging_cb.grid(row=5, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Code Assist", variable=code_assist_var).grid(row=6, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
disable_telemetry_cb = ttk.Checkbutton(root, text="Disable Telemetry", variable=disable_telemetry_var)
disable_telemetry_cb.grid(row=7, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Rainbow UI", variable=rainbow_ui_var).grid(row=8, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Force High Graphics", variable=force_high_graphics_var).grid(row=9, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Verified Badge", variable=visual_verified_var).grid(row=10, column=checkbox_column_one, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Classic Font", variable=old_font_var).grid(row=1, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Classic Error", variable=classic_error_var).grid(row=2, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Extra Plugins", variable=extra_plugins_var).grid(row=3, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Faster Menu", variable=faster_menu_var).grid(row=4, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Cleaner UI", variable=cleaner_ui_var).grid(row=5, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Fluent UI [BETA]", variable=fluent_ui_var, command=fluent_background).grid(row=6, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Performance Mode", variable=performance_mode_var).grid(row=7, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Foundation Colors", variable=foundation_colors_var).grid(row=8, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
disable_updates_cb = ttk.Checkbutton(root, text="Disable Updates", variable=disable_updating_var)
disable_updates_cb.grid(row=9, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)
ttk.Checkbutton(root, text="Enable Internal", variable=enable_internal_var).grid(row=10, column=checkbox_column_two, sticky=tk.W, padx=10, pady=3)

global pluginList
pluginList = []

global plugin_check_states
plugin_check_states = {}

def plugin_editor():
    new_window = tk.Toplevel(root)
    new_window.resizable(False, False)
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
        chk.grid(row=row, column=column, sticky="w", padx=5, pady=5)

        row += 1 
        if (i + 1) % 20 == 0:
            row = 0
            column += 1

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=0, pady=(0, 20), sticky="n")

    ttk.Button(button_frame, text="Enable All", command=enable_all).grid(row=0, column=0, pady=(20, 0))
    ttk.Button(button_frame, text="Disable All", command=disable_all).grid(row=0, column=1, pady=(20, 0), padx=(6, 0))
    ttk.Button(button_frame, text="Reset to Settings", command=reset_checkboxes).grid(row=0, column=2, pady=(20, 0), padx=(6, 0))

def check_zip_file(zip_file):
    with zipfile.ZipFile(zip_file) as z:
        root = ""
        names = z.namelist()

        top_level_dirs = set(os.path.dirname(name).split("/")[0] for name in names if os.path.dirname(name))
        if len(top_level_dirs) == 1:
            root = top_level_dirs.pop() + "/"
        
        required_dirs = {"content", "ExtraContent", "PlatformContent", "shaders", "ssl"}
        for name in names:
            base_name = os.path.basename(name.rstrip("/"))
            if base_name in required_dirs:
                return True

        for name in names:
            if name.startswith(root):
                base_name = os.path.basename(name.rstrip("/"))
                if base_name in required_dirs:
                    return True

    return False

def check_zip_file(zip_file):
    with zipfile.ZipFile(zip_file) as z:
        root = ""
        names = z.namelist()

        top_level_dirs = set(os.path.dirname(name).split("/")[0] for name in names if os.path.dirname(name))
        if len(top_level_dirs) == 1:
            root = top_level_dirs.pop() + "/"
        
        required_dirs = {"content", "ExtraContent", "PlatformContent", "shaders", "ssl"}
        for name in names:
            base_name = os.path.basename(name.rstrip("/"))
            if base_name in required_dirs:
                return True

        for name in names:
            if name.startswith(root):
                base_name = os.path.basename(name.rstrip("/"))
                if base_name in required_dirs:
                    return True

    return False

def extract_and_move(zip_file):
    try:
        with zipfile.ZipFile(zip_file) as z:
            root = ""
            names = z.namelist()

            top_level_dirs = set(os.path.dirname(name).split("/")[0] for name in names if os.path.dirname(name))
            if len(top_level_dirs) == 1:
                root = top_level_dirs.pop() + "/"

            for name in names:
                if name.startswith(root):
                    base_name = os.path.basename(name.rstrip("/"))
                    if base_name:
                        relative_path = os.path.relpath(name, root)
                        target_path = os.path.join(selected_version, relative_path)

                        if name.endswith("/"):
                            os.makedirs(target_path, exist_ok=True)
                        else:
                            try:
                                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                                with z.open(name) as source, open(target_path, "wb") as target:
                                    target.write(source.read())
                            except Exception:
                                pass

    except zipfile.BadZipFile:
        pass
    except Exception:
        pass
                    
def theme_selector():
    theme_selector_window = tk.Toplevel(root)
    theme_selector_window.resizable(False, False)
    theme_selector_window.title("Roblox Studio Manager: Theme Selector")
    theme_selector_window.iconbitmap(application_path + "\\icon.ico")

    main_frame = ttk.Frame(theme_selector_window, padding=20)
    main_frame.pack()

    url_label = ttk.Label(main_frame, text="Download Link:", padding=10)
    url_label.pack()

    url_entry = ttk.Entry(main_frame, width=40)
    url_entry.pack()

    status_label = ttk.Label(main_frame, text="Enter URL", font=("Segoe UI", 12), foreground="#00FFC4")
    status_label.pack(pady=10)

    def check_theme():
        url = url_entry.get()
        status_label.config(text="Checking...", foreground="#00FFC4")

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException:
            status_label.config(text="❌Invalid URL", foreground="#FF003B")
            return

        zip_file = BytesIO(response.content)

        if check_zip_file(zip_file):
            status_label.config(text="Valid Theme", foreground="#00FFC4")
            extract_and_move(zip_file)
            status_label.config(text="Theme Applied", foreground="#00FFC4")
        else:
            status_label.config(text="❌Invalid Theme", foreground="#FF003B")

    check_button = ttk.Button(main_frame, text="Check Theme", command=check_theme)
    check_button.pack(pady=10)

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
        for plugin in os.listdir(plugin_dir):
            plugin_path = os.path.join(plugin_dir, plugin)
            with open(plugin_path, "r+b") as f:
                content = f.read()

                index = content[24:].find(b"DISABLED")
                if index == 0:  
                    content = content[:24] + content[32:]  
                    f.seek(0)
                    f.write(content)
                    f.truncate()

def disable_plugin(plugin):

    plugin_dirs = [
        os.path.join(selected_version, "BuiltInPlugins", "Optimized_Embedded_Signature"),
        os.path.join(selected_version, "BuiltInStandalonePlugins", "Optimized_Embedded_Signature")
    ]

    for plugin_dir in plugin_dirs:
        plugin_path = os.path.join(plugin_dir, plugin)
        if os.path.exists(plugin_path):
            with open(plugin_path, "r+b") as f:
                content = f.read()

                if b"DISABLED" not in content[24:]:
                    f.seek(0)
                    new_content = content[:24] + b"DISABLED" + content[24:]
                    f.write(new_content)
            break

def reset_states():

    plugin_dirs = [
        os.path.join(selected_version, "BuiltInPlugins", "Optimized_Embedded_Signature"),
        os.path.join(selected_version, "BuiltInStandalonePlugins", "Optimized_Embedded_Signature")
    ]

    for plugin_dir in plugin_dirs:
        for plugin in os.listdir(plugin_dir):
            plugin_path = os.path.join(plugin_dir, plugin)
            with open(plugin_path, "r+b") as f:
                content = f.read()

                index = content[24:].find(b"DISABLED")
                if index != -1:
                    index += 24  
                    content = content[:index] + content[index+8:]  
                    f.seek(0)
                    f.truncate()  
                    f.write(content)

def check_disabled_state(plugin):

    plugin_dirs = [
        os.path.join(selected_version, "BuiltInPlugins", "Optimized_Embedded_Signature"),
        os.path.join(selected_version, "BuiltInStandalonePlugins", "Optimized_Embedded_Signature")
    ]

    for plugin_dir in plugin_dirs:
        plugin_path = os.path.join(plugin_dir, plugin)
        if os.path.exists(plugin_path):
            with open(plugin_path, "rb") as f:
                content = f.read()
                if b"DISABLED" in content:
                    return True
            break

    return False

button_frame_top = ttk.Frame(root)
button_frame_top.grid(row=11, column=0, columnspan=6, pady=(0, 1), sticky="n")
button_frame_bottom = ttk.Frame(root)
button_frame_bottom.grid(row=12, column=0, columnspan=6, sticky="n")
progress_frame = ttk.Frame(root)
progress_frame.grid(row=13, column=1, pady=(6, 20), padx=(6, 6), sticky="ew", columnspan=4)
progress_frame.rowconfigure(0, weight=44, minsize=4100)

ttk.Button(button_frame_top, text="Apply Settings", command=update_settings).grid(row=11, column=0, pady=(20, 0))
ttk.Button(button_frame_top, text="Reset Configuration", command=reset_fflags).grid(row=11, column=1, pady=(20, 0), padx=(6, 0))
ttk.Button(button_frame_top, text="Installation Folder", command=installation_folder).grid(row=11, column=2, pady=(20, 0), padx=(6, 0))
ttk.Button(button_frame_bottom, text="Launch Studio", command=launch_studio).grid(row=12, column=0, pady=(6, 20))
update_studio_b = ttk.Button(button_frame_bottom, text="Update Studio", command=update_studio)
update_studio_b.grid(row=12, column=1, pady=(6, 20), padx=(6, 0))
ttk.Button(button_frame_bottom, text="Plugin Editor", command=plugin_editor).grid(row=12, column=2, pady=(6, 20), padx=(6, 0))
ttk.Button(button_frame_bottom, text="Theme Manager", command=theme_selector).grid(row=12, column=3, pady=(6, 20), padx=(6, 0))

progressbar = ttk.Progressbar(progress_frame, mode="determinate", length = 20)
progressbar.pack(expand=True, fill="both")

label = tk.Label(root, font=("Segoe UI", 12), text="Fireblade", padx=2, pady = 2)
label.place(relx=1.0, rely=1.0, anchor="se")

if not check_internet():
    optimize_roblox_var.set(value = False)
    disable_updating_var.set(value = False)
    log_all_var.set(value = False)
    disable_telemetry_var.set(value = False)
    optimize_roblox_cb.configure(state = "disabled")
    disable_updates_cb.configure(state = "disabled")  
    log_all_cb.configure(state = "disabled")  
    disable_telemetry_cb.configure(state = "disabled")
    update_studio_b.configure(state = "disabled")  

sv_ttk.set_theme("dark")
root.resizable(False, False)
root.iconbitmap(application_path + "\\icon.ico")

if fluent_ui_var.get() == True:
    fluent_background()

root.mainloop()
