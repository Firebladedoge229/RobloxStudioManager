import os
import sys
import json
import zipfile
import requests
import re
import ctypes
import subprocess
import psutil
from time import time, sleep
import xml.etree.ElementTree as ET

repoLocation = "https://raw.githubusercontent.com/Firebladedoge229/RobloxStudioManager/refs/heads/main/"

clientAppSettingsURL = "https://clientsettings.roblox.com/v2/settings/application/PCStudioApp/"
fvariablesURL = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/FVariables.txt"

cursorURL = f"{repoLocation}misc/ArrowCursor.png"
cursorFarURL = f"{repoLocation}/misc/ArrowFarCursor.png"
legacyCursorURL = f"{repoLocation}/misc/LegacyArrowCursor.png"
legacyCursorFarURL = f"{repoLocation}/misc/LegacyArrowFarCursor.png"

smallURL = f"{repoLocation}/misc/small.png"
smallReplacementURL = f"{repoLocation}/misc/small-replacement.png"
mediumURL = f"{repoLocation}/misc/medium.png"
mediumReplacementURL = f"{repoLocation}/misc/medium-replacement.png"
largeURL = f"{repoLocation}/misc/large.png"
largeReplacementURL = f"{repoLocation}/misc/large-replacement.png"

ouchURL = f"{repoLocation}misc/Ouch.ogg"
legacyOuchURL = f"{repoLocation}misc/LegacyOuch.ogg"

clientSettingsSuccess = False
fVariablesSuccess = False

internalSignatureInfo = "22 59 6F 75 72 20 61 63 63 6F 75 6E 74 20 69 73 20 61 73 73 6F 63 69 61 74 65 64 20 77 69 74 68 20 61 6E 20 40 72 6F 62 6C 6F 78 2E 63 6F 6D 20 65 6D 61 69 6C 20 61 64 64 72 65 73 73 20 6F 72 20 68 61 73 20 53 6F 6F 74 68 73 61 79 65 72 20 70 65 72 6D 69 73 73 69 6F 6E 73 2E 20 59 6F 75 20 61 6C 73 6F 20 68 61 76 65 20 69 6E 74 65 72 6E 61 6C 2D 6F 6E 6C 79 20 66 65 61 74 75 72 65 73 20 74 75 72 6E 65 64 20 6F 6E 2E 0D 0A 44 6F 20 79 6F 75 20 77 61 6E 74 20 74 6F 20 64 69 73 61 62 6C 65 20 49 6E 74 65 72 6E 61 6C 20 46 65 61 74 75 72 65 73 3F 20 54 68 69 73 20 77 69 6C 6C 20 6D 61 6B 65 20 79 6F 75 72 20 53 74 75 64 69 6F 20 65 78 70 65 72 69 65 6E 63 65 20 69 64 65 6E 74 69 63 61 6C 20 74 6F 20 64 65 76 65 6C 6F 70 65 72 73 2E 0D 0A 59 6F 75 20 63 61 6E 20 67 6F 20 74 6F 20 53 65 74 74 69 6E 67 73 20 3E 20 53 74 75 64 69 6F 20 3E 20 41 64 76 61 6E 63 65 64 20 74 6F 20 72 65 2D 65 6E 61 62 6C 65 20 49 6E 74 65 72 6E 61 6C 20 46 65 61 74 75 72 65 73 2E 22"
internalPatchInfo = "22 59 6F 75 20 63 75 72 72 65 6E 74 6C 79 20 68 61 76 65 20 74 68 65 20 45 6E 61 62 6C 65 20 49 6E 74 65 72 6E 61 6C 20 66 65 61 74 75 72 65 20 65 6E 61 62 6C 65 64 20 69 6E 20 52 6F 62 6C 6F 78 20 53 74 75 64 69 6F 20 4D 61 6E 61 67 65 72 2E 20 54 68 69 73 20 66 65 61 74 75 72 65 20 67 69 76 65 73 20 61 63 63 65 73 73 20 74 6F 20 73 70 65 63 69 61 6C 20 69 6E 74 65 72 6E 61 6C 2D 6F 6E 6C 79 20 66 65 61 74 75 72 65 73 20 73 75 63 68 20 61 73 20 74 68 65 20 66 6C 61 67 20 65 64 69 74 6F 72 2E 20 43 6C 69 63 6B 69 6E 67 20 59 65 73 20 77 69 6C 6C 20 64 69 73 61 62 6C 65 20 74 68 65 20 49 6E 74 65 72 6E 61 6C 20 46 65 61 74 75 72 65 73 2C 20 61 6E 64 20 79 6F 75 20 63 61 6E 20 67 6F 20 74 6F 20 74 68 65 20 53 65 74 74 69 6E 67 73 20 6D 65 6E 75 20 74 6F 20 72 65 2D 65 6E 61 62 6C 65 20 69 74 20 5B 53 65 74 74 69 6E 67 73 20 3E 20 53 74 75 64 69 6F 20 3E 20 41 64 76 61 6E 63 65 64 5D 22 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"

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

def hex_to_bytes(hex_string):
    hex_string = hex_string.replace(" ", "")
    return b"".join(bytes([int(hex_string[i:i+2], 16)]) for i in range(0, len(hex_string), 2))

def find_version_line(version, lines):
    return next((line for line in lines.splitlines() if version in line), None)

def find_latest_studio_version(lines):
    return next((line for line in reversed(lines.splitlines()) if "Studio64" in line), "")

def rgb_to_hex(rgb_str):
    rgb_values = rgb_str.strip("rgb()").split(",")
    r, g, b = map(int, rgb_values)
    return f"#{r:02X}{g:02X}{b:02X}"

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

def patch_exe(exe_path, signature, patch, signatureinfo, patchinfo):
    try:
        signatureinfo = hex_to_bytes(signatureinfo)
        patchinfo = hex_to_bytes(patchinfo)

        with open(exe_path, "r+b") as f:
            content = f.read()
            content = content.replace(signature, patch)
            content = content.replace(signatureinfo, patchinfo)
            f.seek(0)
            f.write(content)
            f.truncate()
            print(f"\033[1;32mSUCCESS:\033[0m Patching {exe_path} completed.")
            return True
    except Exception as e:
        print(f"\033[1;31mERROR:\033[0m Error patching {exe_path}: {e}")
        return False
    
def replace_data_in_exe(exe_data, old_data, new_data):
    return exe_data.replace(old_data, new_data)

def patch_banner(exe_path, inverse):
    try:
        small_data = requests.get(smallURL).content
        small_replacement_data = requests.get(smallReplacementURL).content
        medium_data = requests.get(mediumURL).content
        medium_replacement_data = requests.get(mediumReplacementURL).content
        large_data = requests.get(largeURL).content
        large_replacement_data = requests.get(largeReplacementURL).content

        with open(exe_path, "rb") as exe_file:
            exe_data = exe_file.read()

        if not inverse:
            exe_data = replace_data_in_exe(exe_data, small_data, small_replacement_data)
            exe_data = replace_data_in_exe(exe_data, medium_data, medium_replacement_data)
            exe_data = replace_data_in_exe(exe_data, large_data, large_replacement_data)
        elif inverse:
            exe_data = replace_data_in_exe(exe_data, small_replacement_data, small_data)
            exe_data = replace_data_in_exe(exe_data, medium_replacement_data, medium_data)
            exe_data = replace_data_in_exe(exe_data, large_replacement_data, large_data)

        with open(exe_path, "wb") as exe_file:
            exe_file.write(exe_data)
    except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error fetching legacy banner: {exception}")

def fetch_internal_patch_data():
    try:
        response = requests.get("https://raw.githubusercontent.com/7ap/internal-studio-patcher/refs/heads/main/src/main.rs")
        matches = re.findall(r"0x([0-9A-Fa-f]{2})", response.text)
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
        if patch_exe(exe_path, internal_signature, internal_patch, internalSignatureInfo, internalPatchInfo):
            patch_exe(exe_path, internal_signature_backup, internal_patch_backup, internalSignatureInfo, internalPatchInfo)
    else:
        if patch_exe(exe_path, internal_patch, internal_signature, internalPatchInfo, internalSignatureInfo):
            patch_exe(exe_path, internal_patch_backup, internal_signature_backup, internalPatchInfo, internalSignatureInfo)

def save_settings(settings):
    if getattr(sys, "frozen", False):
        directory = os.path.dirname(sys.executable)
    elif __file__:
        directory = os.path.dirname(__file__)

    settings_file = os.path.join(directory, "RobloxStudioManagerSettings.json")

    try:
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)
        print(f"\033[38;2;52;235;143mDATA:\033[0m Settings saved to {settings_file}")
    except Exception as e:
        print(f"\033[1;31mERROR:\033[0m Error saving settings: {e}")

def get_custom_flags():
    if getattr(sys, "frozen", False):
        directory = os.path.dirname(sys.executable)
    elif __file__:
        directory = os.path.dirname(__file__)

    settings_file = os.path.join(directory, "RobloxStudioManagerFFlags.json")

    try:
        with open(settings_file, "r") as f:
            print(f"\033[38;2;52;235;143mDATA:\033[0m FFlag Settings sent from {settings_file}")
            return json.load(f)
    except Exception as e:
        print(f"\033[1;31mERROR:\033[0m Error getting custom settings: {e}")

def save_custom_flags(settings):
    if getattr(sys, "frozen", False):
        directory = os.path.dirname(sys.executable)
    elif __file__:
        directory = os.path.dirname(__file__)

    settings_file = os.path.join(directory, "RobloxStudioManagerFFlags.json")

    try:
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=4)
        print(f"\033[38;2;52;235;143mDATA:\033[0m FFlag Settings saved to {settings_file}")
    except Exception as e:
        print(f"\033[1;31mERROR:\033[0m Error saving custom settings: {e}")

def check_if_integer(value):
    try:
        _ = int(value)
        return True  
    except ValueError:
        return False  

def get_flags():
    clientAppSettings = os.path.join(selected_version, "ClientSettings", "ClientAppSettings.json")
    with open(clientAppSettings) as file: content = file.read()
    return json.loads(content)

def handle_flags(settings):
    json_file_path = os.path.join(os.getcwd(), "fastflags.json")
    if not os.path.exists(json_file_path):
        print("\033[1;31mERROR:\033[0m fastflags.json file not found.")
        return

    with open(json_file_path, "r") as f:
        flags_data = json.load(f)

    applied_flags = {}

    clientAppSettings = os.path.join(selected_version, "ClientSettings", "ClientAppSettings.json")

    os.makedirs(os.path.dirname(clientAppSettings), exist_ok=True)

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

                    os.makedirs(os.path.dirname(clientAppSettings), exist_ok=True)
                    
                    with open(clientAppSettings, "w") as f:
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

    if settings["Telemetry [UNSTABLE]"] == False:
        if clientSettingsSuccess:
            for key, _ in clientAppSettingsURL.items():
                lowerKey = key.lower()
                if "telemetry" in lowerKey or "analytics" in lowerKey or "metrics" in lowerKey and "createplacefromplace" not in lowerKey and "threadstacksizebytes" not in lowerKey and "inverseprobability" not in lowerKey:
                    if "createplacefromplace" in lowerKey or "threadstacksizebytes" in lowerKey or "inverseprobability" in lowerKey:
                        print(f"\033[1;36mINFO:\033[0m Skipping {key}")
                        continue
                    elif "percent" in lowerKey:
                        applied_flags[key] = 0
                    elif "rate" in lowerKey:
                        applied_flags[key] = 999999999999999
                    elif "fflag" in lowerKey and "percent" not in lowerKey:
                        applied_flags[key] = "false"
                    elif "fint" in lowerKey and "interval" in lowerKey:
                        applied_flags[key] = 999999999999999
                    elif "fint" in lowerKey and "interval" not in lowerKey:
                        applied_flags[key] = 0
                    elif "fstring" in lowerKey and "url" in lowerKey:
                        applied_flags[key] = "https://0.0.0.0"
                    elif "fstring" in lowerKey and "url" not in lowerKey:
                        applied_flags[key] = ""
        if fVariablesSuccess: 
            for line in fvariablesURL.splitlines():
                key = re.sub(r"\[[^\]]*\]\s*", "", line.strip())
                lowerKey = key.lower()
                if "telemetry" in lowerKey or "analytics" in lowerKey or "metrics" in lowerKey and "createplacefromplace" not in lowerKey and "threadstacksizebytes" not in lowerKey and "inverseprobability" not in lowerKey:
                    if "createplacefromplace" in lowerKey or "threadstacksizebytes" in lowerKey or "inverseprobability" in lowerKey:
                        print(f"\033[1;36mINFO:\033[0m Skipping {key}")
                        continue
                    elif "percent" in lowerKey:
                        applied_flags[key] = 0
                    elif "rate" in lowerKey:
                        applied_flags[key] = 999999999999999
                    elif "fflag" in lowerKey and "percent" not in lowerKey:
                        applied_flags[key] = "false"
                    elif "fint" in lowerKey and "interval" in lowerKey:
                        applied_flags[key] = 999999999999999
                    elif "fint" in lowerKey and "interval" not in lowerKey:
                        applied_flags[key] = 0
                    elif "fstring" in lowerKey and "url" in lowerKey:
                        applied_flags[key] = "https://0.0.0.0"
                    elif "fstring" in lowerKey and "url" not in lowerKey:
                        applied_flags[key] = ""

        if settings["Enable Beta Features"] == True:
            if clientSettingsSuccess:
                for key, _ in clientAppSettingsURL.items():
                    lowerKey = key.lower()
                    if "flag" in lowerKey and "betafeature" in lowerKey:
                        applied_flags[key] = True
                        
            if fVariablesSuccess: 
                for line in fvariablesURL.splitlines():
                    key = re.sub(r"\[[^\]]*\]\s*", "", line.strip())
                    lowerKey = key.lower()
                    if "flag" in lowerKey and "betafeature" in lowerKey:
                        applied_flags[key] = True
        
        if settings["Show Flags"] == True:
            flag_list = ""
            for flag in applied_flags:
                flag_list += flag + ","
            applied_flags["FStringDebugShowFlagState"] = flag_list[:-1]

        if settings["Legacy Launch Banner"] == True:
            patch_banner(os.path.join(selected_version, "RobloxStudioBeta.exe"), False)
        else:
            patch_banner(os.path.join(selected_version, "RobloxStudioBeta.exe"), True)

    tree = ET.parse(os.path.join(os.path.join(os.environ["LOCALAPPDATA"], "Roblox"), "GlobalBasicSettings_13_Studio.xml"))
    root = tree.getroot()

    if check_if_integer(settings["CoreGUI Transparency"]):
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
        try:
            legacyOuchData = requests.get(legacyOuchURL).content

            with open(os.path.join(selected_version, "content", "sounds", "ouch.ogg"), "wb") as f:
                f.write(legacyOuchData)
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error while replacing death sound: {exception}")
    else:
        try:
            ouchData = requests.get(ouchURL).content

            with open(os.path.join(selected_version, "content", "sounds", "ouch.ogg"), "wb") as f:
                f.write(ouchData)
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error while replacing death sound: {exception}")

    if settings["Legacy Cursor"] == True:
        try:
            legacyCursorData = requests.get(legacyCursorURL).content
            legacyCursorFarData = requests.get(legacyCursorFarURL).content

            with open(os.path.join(selected_version, "content", "textures", "Cursors", "KeyboardMouse", "ArrowCursor.png"), "wb") as f:
                f.write(legacyCursorData)

            with open(os.path.join(selected_version, "content", "textures", "Cursors", "KeyboardMouse", "ArrowFarCursor.png"), "wb") as f:
                f.write(legacyCursorFarData)
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error while replacing cursor: {exception}")
    else:
        try:
            cursorData = requests.get(cursorURL).content
            cursorFarData = requests.get(cursorFarURL).content

            with open(os.path.join(selected_version, "content", "textures", "Cursors", "KeyboardMouse", "ArrowCursor.png"), "wb") as f:
                f.write(cursorData)

            with open(os.path.join(selected_version, "content", "textures", "Cursors", "KeyboardMouse", "ArrowFarCursor.png"), "wb") as f:
                f.write(cursorFarData)
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error while replacing cursor: {exception}")

    os.makedirs(os.path.dirname(clientAppSettings), exist_ok=True)

    combined_flags = applied_flags.copy()
    combined_flags.update(get_custom_flags())

    with open(clientAppSettings, "w") as f:
        json.dump(combined_flags, f, indent=4)

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
                    if file_info.filename.startswith(target_dir) and file_info.filename.endswith((".ttf", ".otf")):
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
        print("\033[1;31mERROR:\033[0m Version information not found in the deploy history. Are you on the zLive channel?")

def apply_settings(settings):
    print("\033[1;36mINFO:\033[0m Applied settings:", settings)

    save_settings(settings)

    studio_running = False
    for proc in psutil.process_iter(["pid", "name"]):
        if proc.info["name"] == "RobloxStudioBeta.exe":
            studio_running = True
            break

    if studio_running:
        response = ctypes.windll.user32.MessageBoxW(0, "Roblox Studio is currently running. Do you want to close it to apply the changes?", "Roblox Studio Manager", 0x04)
        if response == 6:  

            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] == "RobloxStudioBeta.exe":
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

    if settings.get("Enable Internal"):
        try:
            if internal_signature:
                apply_patch(True, selected_version, internal_signature, internal_patch, internal_signature_backup, internal_patch_backup)
        except Exception as exception:
                print(f"\033[1;31mERROR:\033[0m Error applying internal patch: {exception}")
    else:
        try:
            if internal_signature:
                apply_patch(False, selected_version, internal_signature, internal_patch, internal_signature_backup, internal_patch_backup)
        except Exception as exception:
                print(f"\033[1;31mERROR:\033[0m Error applying internal patch: {exception}")

def reset_configuration():
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
    subprocess.Popen([os.path.join(selected_version, "RobloxStudioBeta.exe")], cwd=selected_version)
    print("\033[1;36mINFO:\033[0m Launch Studio clicked")

def update_studio():
    subprocess.Popen([os.path.join(selected_version, "RobloxStudioInstaller.exe")], cwd=selected_version)
    print("\033[1;36mINFO:\033[0m Update Studio clicked")
    start_time = time()
    while True:
        for proc in psutil.process_iter(["name"]):
            if proc.info["name"].lower() == "robloxstudiobeta.exe":
                proc.terminate()
                for proc in psutil.process_iter(["name"]):
                    if proc.info["name"].lower() == "robloxstudioinstaller.exe":
                        proc.terminate()
                return
        if (time() - start_time) >= 60:
            return
        sleep(0.1)

selected_version = find_latest_version(os.path.join(os.environ["LOCALAPPDATA"], "Roblox", "Versions"))
if not selected_version:
    selected_version = find_latest_version(os.path.join(os.environ["PROGRAMFILES(X86)"], "Roblox", "Versions"))

print(f"\033[1;36mINFO:\033[0m Selected Version: {selected_version}" if selected_version else "\033[1;31mERROR:\033[0m No valid version found.")

def patch_studio_for_themes():
    def patch_studio():
        file_path = os.path.join(selected_version, "RobloxStudioBeta.exe")

        with open(file_path, "rb") as f:
            file_data = f.read()

        print("\033[1;36mINFO:\033[0m Searching for bytes..")
        patch_done = False
        for i in range(len(file_data) - 3):
            if file_data[i:i+4] == b":/Pl":
                file_data = file_data[:i] + b"./Pl" + file_data[i+4:]
                patch_done = True

        patched_file_path = os.path.join(selected_version, "RobloxStudioBeta.exe")
        with open(patched_file_path, "wb") as f:
            f.write(file_data)

        if not patch_done:
            print("\033[1;36mINFO:\033[0m No bytes found.")
            return

        print("\033[1;32mSUCCESS:\033[0m Successfully patched Roblox Studio for theme use.")
    
    patch_studio()

target_dir = selected_version
platform_path = os.path.join(target_dir, "Platform")
base_path = os.path.join(platform_path, "Base", "QtUI", "themes")
base_path = os.path.normpath(base_path)
os.makedirs(platform_path, exist_ok=True)
os.makedirs(base_path, exist_ok=True)

dark_theme_url = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/QtResources/Platform/Base/QtUI/themes/DarkTheme.json"
light_theme_url = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/QtResources/Platform/Base/QtUI/themes/LightTheme.json"
foundation_dark_theme_url = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/QtResources/Platform/Base/QtUI/themes/FoundationDarkTheme.json"
foundation_light_theme_url = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/QtResources/Platform/Base/QtUI/themes/FoundationLightTheme.json"

dark_theme_path = os.path.join(base_path, "DarkTheme.json")
light_theme_path = os.path.join(base_path, "LightTheme.json")
foundation_dark_theme_path = os.path.join(base_path, "FoundationDarkTheme.json")
foundation_light_theme_path = os.path.join(base_path, "FoundationLightTheme.json")

def download_default_themes():
    def download_file(url, file_path):
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)

    print("\033[1;36mINFO:\033[0m Downloading theme files..")
    try:
        download_file(dark_theme_url, dark_theme_path)
        download_file(light_theme_url, light_theme_path)
        download_file(foundation_dark_theme_url, foundation_dark_theme_path)
        download_file(foundation_light_theme_url, foundation_light_theme_path)
        print("\033[1;32mSUCCESS:\033[0m Theme files downloaded successfully.")
    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m Failed to download theme files: {exception}")

if not os.path.exists(dark_theme_path):
    download_default_themes()

def get_theme_colors(selection = "LightTheme"):
    with open(os.path.join(base_path, f"{selection}.json"), "r") as file:
        json_data = json.load(file)
    return json_data

theme_paths = [
    os.path.join(base_path, "LightTheme.json"),
    os.path.join(base_path, "FoundationLightTheme.json"),
    os.path.join(base_path, "DarkTheme.json"),
    os.path.join(base_path, "FoundationDarkTheme.json")
]

def apply_custom_theme(themeJSON):
    try:
        theme_dict = json.loads(themeJSON)
    except json.JSONDecodeError:
        print("\033[1;31mERROR:\033[0m Failed to decode theme JSON.")
        return
    for theme_path in theme_paths:
        try:
            with open(theme_path, "r") as file:
                original_theme = json.load(file)
            
            original_theme.update(theme_dict)
            
            with open(theme_path, "w") as file:
                json.dump(original_theme, file, indent=4)
            
            print(f"\033[1;32mSUCCESS:\033[0m Custom theme applied to {theme_path}")
        
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m An error occurred while parsing {theme_path}: {exception}")

disabledPlugins = os.path.join(selected_version, "DisabledPlugins", "Optimized_Embedded_Signature")

def get_disabled_plugins():
    file_info = []
    folder_path = os.path.join(selected_version, "DisabledPlugins", "Optimized_Embedded_Signature")
    if os.path.isdir(folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".rbxm"):
                    name, _ = os.path.splitext(file)
                    split = name.split("-", 2)
                    name = split[0]
                    folder = split[1]
                    file_info.append(f"{folder}/{name}")
    else:
        print(f"\033[1;31mERROR:\033[0m Folder {folder_path} does not exist.")

    file_info.sort()
    return file_info

def toggle_plugin_enabled(plugin, enabled, *disableSaving):
    if enabled:
        split = os.path.normpath(plugin).split(os.sep)
        split = split[1].split("-")
        name = split[0]
        folder = split[1]
        
        actualPath = os.path.join(selected_version, "DisabledPlugins", "Optimized_Embedded_Signature", name) + f"-{folder}.rbxm"
        modifiedPath = os.path.join(selected_version, folder, "Optimized_Embedded_Signature", name) + ".rbxm"
        
        os.rename(actualPath, modifiedPath)
        print(f"\033[1;36mINFO:\033[0m Moved file {actualPath} to directory of {modifiedPath} [ENABLED]")
    else:
        split = os.path.normpath(plugin).split(os.sep)
        actualPath = os.path.join(selected_version, split[0], "Optimized_Embedded_Signature", split[1]) + ".rbxm"
        modifiedPath = os.path.join(selected_version, "DisabledPlugins", "Optimized_Embedded_Signature", split[1]) + f"-{split[0]}.rbxm"
        
        os.rename(actualPath, modifiedPath)
        print(f"\033[1;36mINFO:\033[0m Moved file {actualPath} to directory of {modifiedPath} [DISABLED]")

    if not disableSaving:
        if getattr(sys, "frozen", False):
            directory = os.path.dirname(sys.executable)
        elif __file__:
            directory = os.path.dirname(__file__)

        plugin_file = os.path.join(directory, "RobloxStudioPluginStatus.rbxp")
        
        try:
            disabledPlugins = get_disabled_plugins()
            with open(plugin_file, "w") as file:
                file.write("\n".join(disabledPlugins))
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m An error occurred while writing to {plugin_file}: {exception}")

if not os.path.exists(disabledPlugins):
    os.makedirs(disabledPlugins)

    if getattr(sys, "frozen", False):
        directory = os.path.dirname(sys.executable)
    elif __file__:
        directory = os.path.dirname(__file__)

    plugin_file = os.path.join(directory, "RobloxStudioPluginStatus.rbxp")

    try:
        file = open(plugin_file, "r")
        content = file.read().splitlines()
        file.close()
        for plugin in content:
            toggle_plugin_enabled(plugin, False, True)
            split = plugin.split(os.sep)
            os.remove(os.path.join(selected_version, split[0], "Optimized_Embedded_Signature", split[1]) + ".rbxm")
    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m An error occurred while inspecting {plugin_file}: {exception}")

pluginFolders = ["DisabledPlugins", "BuiltInPlugins", "BuiltInStandalonePlugins"]

def get_builtin_plugins():
    file_info = {}

    for folder in pluginFolders:
        folder_path = os.path.join(selected_version, folder, "Optimized_Embedded_Signature")
        folder_path = os.path.normpath(folder_path)
        if os.path.isdir(folder_path):
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".rbxm"):
                        name, _ = os.path.splitext(file)
                        if os.path.split(os.path.split(root)[0])[1] == "DisabledPlugins":
                            split = name.split("-", 2)
                            name = split[0]
                            folder = split[1]
                            duplicateFile = os.path.join(selected_version, folder, "Optimized_Embedded_Signature", name) + ".rbxm"
                            if os.path.isfile(duplicateFile):
                                os.remove(duplicateFile)
                        file_info[file] = {"name": name, "base_folder": folder, "enabled": os.path.split(os.path.split(root)[0])[1] != "DisabledPlugins"}
        else:
            print(f"\033[1;31mERROR:\033[0m Folder {folder_path} does not exist.")

    sorted_files = sorted(file_info.values(), key=lambda x: x["name"])
    return sorted_files

fetch = fetch_internal_patch_data()
try:
    internal_signature, internal_patch = fetch
    internal_signature_backup, internal_patch_backup = fetch
except Exception as exception:
    print(f"\033[1;31mERROR:\033[0m Error fetching internal patch data: {exception}")
