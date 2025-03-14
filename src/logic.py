import json
import os
import zipfile
import requests
import re
import ctypes
import subprocess
import psutil
import xml.etree.ElementTree as ET

repoLocation = "https://raw.githubusercontent.com/Firebladedoge229/RobloxStudioManager/refs/heads/main/"

clientAppSettingsURL = "https://clientsettings.roblox.com/v2/settings/application/PCStudioApp/"
fvariablesURL = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/FVariables.txt"

cursorURL = f"{repoLocation}misc/ArrowCursor.png"
cursorFarURL = f"{repoLocation}/misc/ArrowFarCursor.png"
legacyCursorURL = f"{repoLocation}/misc/LegacyArrowCursor.png"
legacyCursorFarURL = f"{repoLocation}/misc/LegacyArrowFarCursor.png"

ouchURL = f"{repoLocation}misc/Ouch.ogg"
legacyOuchURL = f"{repoLocation}misc/LegacyOuch.ogg"

clientSettingsSuccess = False
fVariablesSuccess = False

try:
    clientAppSettingsURL = requests.get(clientAppSettingsURL).json()
    clientSettingsSuccess = True
except Exception as exception:
    print(f"\033[1;31mERROR:\033[0m ClientAppSettings could not be fetched: {exception}")

try:
    fvariablesURL = requests.get(fvariablesURL).text
    fVariablesSuccess = True
except Exception as exception:
    print(f"\033[1;31mERROR:\033[0m FVariables could not be fetched: {exception}")

def find_version_line(version, lines):
    return next((line for line in lines.splitlines() if version in line), None)

def find_latest_studio_version(lines):
    return next((line for line in reversed(lines.splitlines()) if "Studio64" in line), "")

def find_latest_version(base_dir):
    selected_version = None
    max_files_count = 0
    for version in os.listdir(base_dir):
        version_dir = os.path.join(base_dir, version)
        exe_path = os.path.join(version_dir, "RobloxStudioBeta.exe")
        if os.path.exists(exe_path):
            num_files = len(os.listdir(version_dir))
            if num_files > max_files_count:
                max_files_count = num_files
                selected_version = version_dir
    return selected_version

def patch_exe(exe_path, signature, patch):
    try:
        with open(exe_path, "r+b") as f:
            content = f.read()
            index = content.find(signature)
            if index != -1:
                f.seek(index)
                f.write(patch)
                return True
        return False
    except Exception as e:
        print(f"\033[1;31mERROR:\033[0m Error patching {exe_path}: {e}")
        return False

def fetch_internal_patch_data():
    try:
        response = requests.get("https://raw.githubusercontent.com/7ap/internal-studio-patcher/refs/heads/main/src/main.rs")
        matches = re.findall(r'0x([0-9A-Fa-f]{2})', response.text)
        if len(matches) >= 24:
            return (b"".join(bytes.fromhex(s) for s in matches[:12]), b"".join(bytes.fromhex(p) for p in matches[12:24]))
        else:
            print("\033[1;31mERROR:\033[0m Not enough matches found in the response.")
            return None
    except Exception as e:
        print(f"\033[1;31mERROR:\033[0m Error fetching signature backups: {e}")
        return None

def apply_patch(enable_internal, selected_version, internal_signature, internal_patch, internal_signature_backup, internal_patch_backup):
    exe_path = os.path.join(selected_version, "RobloxStudioBeta.exe")
    if enable_internal:
        if patch_exe(exe_path, internal_signature, internal_patch):
            patch_exe(exe_path, internal_signature_backup, internal_patch_backup)
    else:
        if patch_exe(exe_path, internal_patch, internal_signature):
            patch_exe(exe_path, internal_patch_backup, internal_signature_backup)

def save_settings(settings):
    settings_file = os.path.join(os.getcwd(), 'RobloxStudioManagerSettings.json')
    try:
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        print(f"\033[38;2;52;235;143mDATA:\033[0m Settings saved to {settings_file}")
    except Exception as e:
        print(f"\033[1;31mERROR:\033[0m Error saving settings: {e}")

def check_if_integer(value):
    try:
        int_value = int(value)
        return True  
    except ValueError:
        return False  

def handle_flags(settings):
    json_file_path = os.path.join(os.getcwd(), 'fastflags.json')
    if not os.path.exists(json_file_path):
        print("\033[1;31mERROR:\033[0m fastflags.json file not found.")
        return

    with open(json_file_path, 'r') as f:
        flags_data = json.load(f)

    applied_flags = {}

    clientAppSettings = os.path.join(selected_version, "ClientSettings", "ClientAppSettings.json")

    for key, value in settings.items():
        if key in flags_data:

            if isinstance(value, bool):  
                flag_value = str(value)  
                if flag_value in flags_data[key]:
                    applied_flags.update(flags_data[key][flag_value])
                else:
                    print(f"\033[38;5;214mWARNING:\033[0m No matching flag for {key} with value {value} BOOLEAN")

            elif check_if_integer(value):  
                if key in flags_data:

                    for flag_key, flag_value in flags_data[key].items():
                        if isinstance(flag_value, int) and not isinstance(flag_value, bool):  
                            flags_data[key][flag_key] = value
                            applied_flags[flag_key] = value
                        else:
                            applied_flags[flag_key] = flag_value

            elif isinstance(value, str):  
                if value == "":
                    print(f"\033[38;5;214mWARNING:\033[0m Empty value for {key}. Skipping..")
                    if key in applied_flags:
                        del applied_flags[key]

                    with open(clientAppSettings, 'w') as f:
                        json.dump(applied_flags, f, indent=4)
                    continue
                if value in flags_data[key]:
                    applied_flags.update(flags_data[key][value])
                else:
                    print(f"\033[38;5;214mWARNING:\033[0m No matching flag for {key} with value {value}")
            else:
                print(f"\033[38;5;214mWARNING:\033[0m Unsupported value type for {key}: {value}")
        else:
            print(f"\033[38;5;214mWARNING:\033[0m No flag data found for {key}")

    if not os.path.exists(clientAppSettings):
        print("\033[1;31mERROR:\033[0m ClientAppSettings.json not found.")
        return

    if settings["Show Flags"] == True:
        flag_list = ""
        for flag in applied_flags:
            flag_list += flag + ","
        applied_flags["FStringDebugShowFlagState"] = flag_list[:-1]

    if settings["Telemetry [UNSTABLE]"] == False:
        if clientSettingsSuccess:
            for key, _ in clientAppSettingsURL.items():
                key = key.lower()
                if "telemetry" in key or "analytics" in key or "metrics" in key and "createplacefromplace" not in key:
                    if "createplacefromplace" in key:
                        print(f"\033[1;36mINFO:\033[0m Skipping {key}")
                        continue
                    elif "percent" in key:
                        applied_flags[key] = 0
                    elif "rate" in key:
                        applied_flags[key] = 999999999999999
                    elif "fflag" in key and "percent" not in key:
                        applied_flags[key] = "false"
                    elif "fint" in key and "interval" in key:
                        applied_flags[key] = 999999999999999
                    elif "fint" in key and "interval" not in key:
                        applied_flags[key] = 0
                    elif "fstring" in key and "url" in key:
                        applied_flags[key] = "https://0.0.0.0"
                    elif "fstring" in key and "url" not in key:
                        applied_flags[key] = ""
        if fVariablesSuccess: 
            for line in fvariablesURL.splitlines():
                key = re.sub(r"\[[^\]]*\]\s*", "", line.strip())
                key = key.lower()
                if "telemetry" in key or "analytics" in key or "metrics" in key and "createplacefromplace" not in key:
                    if "createplacefromplace" in key:
                        print(f"\033[1;36mINFO:\033[0m Skipping {key}")
                        continue
                    elif "percent" in key:
                        applied_flags[key] = 0
                    elif "rate" in key:
                        applied_flags[key] = 999999999999999
                    elif "fflag" in key and "percent" not in key:
                        applied_flags[key] = "false"
                    elif "fint" in key and "interval" in key:
                        applied_flags[key] = 999999999999999
                    elif "fint" in key and "interval" not in key:
                        applied_flags[key] = 0
                    elif "fstring" in key and "url" in key:
                        applied_flags[key] = "https://0.0.0.0"
                    elif "fstring" in key and "url" not in key:
                        applied_flags[key] = ""

    if check_if_integer(settings["CoreGUI Transparency"]):
        tree = ET.parse(os.path.join(os.path.join(os.environ["LOCALAPPDATA"], "Roblox"), "GlobalBasicSettings_13_Studio.xml"))
        root = tree.getroot()

        for item in root.findall(".//Item[@class=\"UserGameSettings\"]"):
            for prop in item.find("Properties"):
                if prop.tag == "float" and prop.attrib.get("name") == "PreferredTransparency":
                    transparency_value = (4 / 99) * float(settings["CoreGUI Transparency"]) + (95 / 99)
                    prop.text = str(transparency_value)
                    print(f"\033[1;36mINFO:\033[0m CoreGUI Transparency set to {transparency_value}")
                    break
    else:
        for item in root.findall(".//Item[@class=\"UserGameSettings\"]"):
            for prop in item.find("Properties"):
                if prop.tag == "float" and prop.attrib.get("name") == "PreferredTransparency":
                    prop.text = "1"
                    print(f"\033[1;36mINFO:\033[0m CoreGUI Transparency set to default")
                    break

        tree.write(os.path.join(os.path.join(os.environ["LOCALAPPDATA"], "Roblox"), "GlobalBasicSettings_13_Studio.xml"), encoding="utf-8", xml_declaration=True)

    if settings["Classic Death Sound"] == True:
        legacyOuchData = requests.get(legacyOuchURL).content

        with open(os.path.join(selected_version, "content", "sounds", "ouch.ogg"), "wb") as f:
            f.write(legacyOuchData)
    else:
        ouchData = requests.get(ouchURL).content

        with open(os.path.join(selected_version, "content", "sounds", "ouch.ogg"), "wb") as f:
            f.write(ouchData)

    if settings["Legacy Cursor"] == True:
        legacyCursorData = requests.get(legacyCursorURL).content
        legacyCursorFarData = requests.get(legacyCursorFarURL).content

        with open(os.path.join(selected_version, "content", "textures", "Cursors", "KeyboardMouse", "ArrowCursor.png"), "wb") as f:
            f.write(legacyCursorData)

        with open(os.path.join(selected_version, "content", "textures", "Cursors", "KeyboardMouse", "ArrowFarCursor.png"), "wb") as f:
            f.write(legacyCursorFarData)
    else:
        cursorData = requests.get(cursorURL).content
        cursorFarData = requests.get(cursorFarURL).content

        with open(os.path.join(selected_version, "content", "textures", "Cursors", "KeyboardMouse", "ArrowCursor.png"), "wb") as f:
            f.write(cursorData)

        with open(os.path.join(selected_version, "content", "textures", "Cursors", "KeyboardMouse", "ArrowFarCursor.png"), "wb") as f:
            f.write(cursorFarData)

    with open(clientAppSettings, 'w') as f:
        json.dump(applied_flags, f, indent=4)

    print(f"\033[1;32mSUCCESS:\033[0m Flags have been set in {clientAppSettings}")

def download_and_apply_font(selected_version):
    zip_path = os.path.join(selected_version, "content", "fonts", "GothamFont.zip")
    try:
        response = requests.get("https://github.com/Firebladedoge229/GothamFont/archive/refs/heads/main.zip", stream=True)
        with open(zip_path, "wb") as output:
            output.write(response.content)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            target_dir = next((file_info.filename for file_info in zip_ref.infolist() if file_info.is_dir()), None)
            if target_dir:
                for file_info in zip_ref.infolist():
                    if file_info.filename.startswith(target_dir) and file_info.filename.endswith(('.ttf', '.otf')):
                        dest_path = os.path.join(selected_version, "content", "fonts", os.path.basename(file_info.filename))
                        with zip_ref.open(file_info) as source, open(dest_path, "wb") as target:
                            target.write(source.read())

        os.remove(zip_path)
    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m Error Downloading and Applying Font: {exception}")

def disable_updates(selected_version):
    try:
        deploy_history = requests.get("https://setup.rbxcdn.com/DeployHistory.txt").text
    except Exception as exception:
        deploy_history = ""
        print("\033[1;31mERROR:\033[0m", exception)

    result = find_version_line(os.path.basename(selected_version), deploy_history)
    latest_version = find_latest_studio_version(deploy_history)

    if result and latest_version:
        print(f"\033[1;36mINFO:\033[0m Result: {result}")  
        print(f"\033[1;36mINFO:\033[0m Latest Version: {latest_version}")  

        result_hash_match = re.search(r"git hash:\s*([\d\.]+)", result)
        latest_hash_match = re.search(r"git hash:\s*([\d\.]+)", latest_version)

        if result_hash_match and latest_hash_match:
            result_hash = result_hash_match.group(1)
            latest_hash = latest_hash_match.group(1)

            print(f"\033[1;36mINFO:\033[0m Result Hash: {result_hash}")  
            print(f"\033[1;36mINFO:\033[0m Latest Hash: {latest_hash}")  

            if len(result_hash) != len(latest_hash):
                ctypes.windll.user32.MessageBoxW(0, "The current version and latest version are not the same size. Due to hex limitations, you cannot disable updating on this version.", "Roblox Studio Manager", 1)
            else:
                result_bytes = bytes.fromhex("".join(format(ord(c), "02X") for c in result_hash))
                patch_bytes = bytes.fromhex("".join(format(ord(c), "02X") for c in latest_hash))

                exe_path = os.path.join(selected_version, "RobloxStudioBeta.exe")
                with open(exe_path, "r+b") as f:
                    content = f.read()
                    index = content.find(result_bytes)
                    if index != -1:
                        f.seek(index)
                        f.write(patch_bytes)
        else:
            print("\033[1;31mERROR:\033[0m Unable to find git hash in either the result or latest version.")
    else:
        print("\033[1;31mERROR:\033[0m Version information not found in the deploy history.")

def apply_settings(settings):
    print("\033[1;36mINFO:\033[0m Applied settings:", settings)

    studio_running = False
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == "RobloxStudioBeta.exe":
            studio_running = True
            break

    if studio_running:
        response = ctypes.windll.user32.MessageBoxW(0, "Roblox Studio is currently running. Do you want to close it to apply the changes?", "Roblox Studio Manager", 0x04)
        if response == 6:  

            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == "RobloxStudioBeta.exe":
                    proc.terminate()
                    print("\033[1;36mINFO:\033[0m Roblox Studio has been forcefully terminated.")
                    break
        else:
            print("\033[1;36mINFO:\033[0m User chose not to force quit Roblox Studio.")
            return

    handle_flags(settings)

    if settings.get("Classic Font"):
        download_and_apply_font(selected_version)

    if settings.get("Disable Updates"):
        disable_updates(selected_version)

    try:
        if internal_signature:
            pass
    except:
        internal_signature = None

    if settings.get("Enable Internal"):
        if internal_signature:
            apply_patch(True, selected_version, internal_signature, internal_patch, internal_signature_backup, internal_patch_backup)
    else:
        if internal_signature:
            apply_patch(False, selected_version, internal_signature, internal_patch, internal_signature_backup, internal_patch_backup)

    save_settings(settings)

def reset_configuration():
    response = ctypes.windll.user32.MessageBoxW(0, "Are you sure you want to reset your FFlags?", "Roblox Studio Manager", 0x04)
    if response == 6:
        clientPath = os.path.join(selected_version, "ClientSettings", "ClientAppSettings.json")
        if os.path.exists(clientPath):
            os.remove(clientPath)
            print("\033[1;36mINFO:\033[0m Configuration reset")
        else:
            print("\033[1;31mERROR:\033[0m The file does not exist")
        print("\033[1;36mINFO:\033[0m Reset Configuration clicked")

def open_installation_folder():
    subprocess.Popen(["explorer", selected_version])
    print("\033[1;36mINFO:\033[0m Installation Folder clicked")

def launch_studio():
    subprocess.Popen([os.path.join(selected_version, "RobloxStudioBeta.exe")])
    print("\033[1;36mINFO:\033[0m Launch Studio clicked")

def update_studio():
    subprocess.Popen([os.path.join(selected_version, "RobloxStudioInstaller.exe")])
    print("\033[1;36mINFO:\033[0m Update Studio clicked")

def open_plugin_editor():
    print("\033[1;36mINFO:\033[0m Plugin Editor clicked")

def open_theme_manager():
    print("\033[1;36mINFO:\033[0m Theme Manager clicked")

selected_version = find_latest_version(os.path.join(os.environ["LOCALAPPDATA"], "Roblox", "Versions"))
if not selected_version:
    selected_version = find_latest_version(os.path.join(os.environ["PROGRAMFILES(X86)"], "Roblox", "Versions"))

print(f"\033[1;36mINFO:\033[0m Selected Version: {selected_version}" if selected_version else "\033[1;31mERROR:\033[0m No valid version found.")

fetch = fetch_internal_patch_data()
try:
    internal_signature, internal_patch = fetch or (None, None, None, None)
    internal_signature_backup, internal_patch_backup = fetch or (None, None, None, None)
except Exception as exception:
    print(f"\033[1;31mERROR:\033[0m Error fetching internal patch data: {exception}")