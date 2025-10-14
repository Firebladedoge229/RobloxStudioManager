import os
import sys
import json
import zipfile
import requests
import re
import ctypes
import subprocess
import psutil
from PIL import Image
from time import time, sleep
import xml.etree.ElementTree as ET

repoLocation = "https://raw.githubusercontent.com/Firebladedoge229/RobloxStudioManager/refs/heads/main/"

clientAppSettingsURL = "https://clientsettings.roblox.com/v2/settings/application/PCStudioApp/"
fvariablesURL = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/roblox/FVariables.txt"

cursorURL = f"{repoLocation}misc/ArrowCursor.png"
cursorFarURL = f"{repoLocation}/misc/ArrowFarCursor.png"
legacyCursorURL = f"{repoLocation}/misc/LegacyArrowCursor.png"
legacyCursorFarURL = f"{repoLocation}/misc/LegacyArrowFarCursor.png"
logoURL = f"{repoLocation}/misc/newlogo.ico"
legacyLogoURL = f"{repoLocation}/misc/legacylogo.ico"

smallURL = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/refs/heads/roblox/QtResources/Logo/StudioLogoAssets/RobloxStudioSplash.png"
mediumURL = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/refs/heads/roblox/QtResources/Logo/StudioLogoAssets/RobloxStudioSplash@2x.png"
largeURL = "https://raw.githubusercontent.com/MaximumADHD/Roblox-Client-Tracker/refs/heads/roblox/QtResources/Logo/StudioLogoAssets/RobloxStudioSplash@3x.png"

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

def rgb_to_hex(rgb_str):
    rgb_values = rgb_str.strip("rgb()").split(",")
    r, g, b = map(int, rgb_values)
    return f"#{r:02X}{g:02X}{b:02X}"

def find_latest_version(base_dir):
    if not "applications" in base_dir.lower():
        selected_version = None
        max_files_count = 0
        os.makedirs(base_dir, exist_ok=True)
        for version in os.listdir(base_dir):
            version_dir = os.path.join(base_dir, version)
            exe_path = os.path.join(version_dir, "RobloxStudioBeta.exe")
            if os.path.exists(exe_path):
                num_files = len(os.listdir(version_dir))
                if num_files > max_files_count:
                    max_files_count = num_files
                    selected_version = version_dir
        return selected_version
    else:
        return base_dir

def patch_exe(exe_path, signature, patch):
    try:
        if ".app" in exe_path.lower():
            exe_path = "/" + os.path.join(selected_version, "Contents", "MacOS", "RobloxStudio")
        with open(exe_path, "r+b") as file:
            content = file.read()
            content = content.replace(signature, patch)
            file.seek(0)
            file.write(content)
            file.truncate()
            print(f"\033[1;32mSUCCESS:\033[0m Patching {exe_path} completed.")
            return True
    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m Error patching {exe_path}: {exception}")
        return False
    
def replace_data_in_exe(exe_data, old_data, new_data):
    return exe_data.replace(old_data, new_data)

def resize_image_to_match(source_path, target_path):
    print(f"\033[1;36mINFO:\033[0m Source Path: {source_path}")
    print(f"\033[1;36mINFO:\033[0m Target Path: {target_path}")

    image1_size = os.path.getsize(source_path)
    image2_size = os.path.getsize(target_path)

    print(f"\033[1;36mINFO:\033[0m Original size of source image: {image1_size} bytes")
    print(f"\033[1;36mINFO:\033[0m Original size of target image: {image2_size} bytes")

    try:
        with Image.open(source_path) as img1, Image.open(target_path) as img2:
            print(f"\033[1;36mINFO:\033[0m Source image size: {img1.size}")
            print(f"\033[1;36mINFO:\033[0m Target image size: {img2.size}")

            target_aspect = img2.width / img2.height
            canvas_width, canvas_height = img1.size

            if canvas_width / canvas_height > target_aspect:
                new_height = canvas_height
                new_width = int(new_height * target_aspect)
            else:
                new_width = canvas_width
                new_height = int(new_width / target_aspect)

            resized_img2 = img2.resize((new_width, new_height), Image.LANCZOS)

            if resized_img2.mode != "RGBA":
                resized_img2 = resized_img2.convert("RGBA")

            canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
            offset_x = (canvas_width - new_width) // 2
            offset_y = (canvas_height - new_height) // 2
            canvas.paste(resized_img2, (offset_x, offset_y), resized_img2)

            print("\033[1;32mSUCCESS:\033[0m Target image resized")

            canvas.save(target_path, optimize=True)
            print(f"\033[1;32mSUCCESS:\033[0m Resized target image saved to: {target_path}")

    except Image.UnidentifiedImageError:
        print(f"\033[1;31mERROR:\033[0m Could not identify image file: {target_path}")
        return

    image2_size = os.path.getsize(target_path)
    print(f"\033[1;36mINFO:\033[0m Size after initial resize and save: {image2_size} bytes")

    if image2_size > image1_size:
        print(f"\033[1;36mINFO:\033[0m Target image is larger than source after resize. Applying palette conversion..")
        with Image.open(target_path) as resized_img:
            img2_pal = resized_img.convert("P", palette=Image.ADAPTIVE)
            img2_pal.save(target_path, optimize=True)
        image2_size = os.path.getsize(target_path)
        print(f"\033[1;36mINFO:\033[0m Size after palette conversion: {image2_size} bytes")

    if image2_size < image1_size:
        padding_size = image1_size - image2_size
        print(f"\033[1;36mINFO:\033[0m Target image is smaller than source. Padding with {padding_size} bytes..")
        with open(target_path, "ab") as file:
            file.write(b"\x00" * padding_size)
        print(f"\033[1;36mINFO:\033[0m Target image size after padding: {os.path.getsize(target_path)} bytes")

    if os.path.getsize(target_path) == image1_size:
        with open(target_path, "rb") as target_file:
            new_data = target_file.read()

        with open(source_path, "wb") as source_file:
            source_file.write(new_data)
        print("\033[1;32mSUCCESS:\033[0m Perfect match after resize.")
    else:
        print(f"\033[1;31mERROR:\033[0m Final size mismatch. Source: {image1_size}, Target: {os.path.getsize(target_path)}")

def patch_banner(exe_path, option):
    try:
        if ".app" in exe_path.lower():
            exe_path = "/" + os.path.join(selected_version, "Contents", "MacOS", "RobloxStudio")

        if not os.path.exists(os.path.join(selected_version, "MediumSplash.bak")):
            small_data = requests.get(smallURL).content
            medium_data = requests.get(mediumURL).content
            large_data = requests.get(largeURL).content
        else: 
            with open(os.path.join(selected_version, "SmallSplash.bak"), "rb") as file:
                small_data = file.read()
            with open(os.path.join(selected_version, "MediumSplash.bak"), "rb") as file:
                medium_data = file.read()
            with open(os.path.join(selected_version, "LargeSplash.bak"), "rb") as file:
                large_data = file.read()
        replacement_data = requests.get(f"https://raw.githubusercontent.com/Firebladedoge229/RobloxStudioManager/refs/heads/main/misc/splash/{requests.utils.quote(option)}.png").content

        small_location = os.path.join(os.environ["TEMP"], "tempSmallData.png")
        medium_location = os.path.join(os.environ["TEMP"], "tempMediumData.png")
        large_location = os.path.join(os.environ["TEMP"], "tempLargeData.png")
        replacement_location = os.path.join(os.environ["TEMP"], "tempReplacementData.png")

        with open(small_location, "wb") as file:
            file.write(small_data)
        with open(medium_location, "wb") as file:
            file.write(medium_data)
        with open(large_location, "wb") as file:
            file.write(large_data)
        with open(replacement_location, "wb") as file:
            file.write(replacement_data)

        resize_image_to_match(small_location, replacement_location)
        resize_image_to_match(medium_location, replacement_location)
        resize_image_to_match(large_location, replacement_location)

        with open(small_location, "rb") as file:
            small_replacement_data = file.read()
        with open(medium_location, "rb") as file:
            medium_replacement_data = file.read()
        with open(large_location, "rb") as file:
            large_replacement_data = file.read()

        with open(exe_path, "rb") as exe_file:
            exe_data = exe_file.read()

        exe_data = replace_data_in_exe(exe_data, small_data, small_replacement_data)
        exe_data = replace_data_in_exe(exe_data, medium_data, medium_replacement_data)
        exe_data = replace_data_in_exe(exe_data, large_data, large_replacement_data)

        with open(os.path.join(selected_version, "SmallSplash.bak"), "wb") as file:
            file.write(small_replacement_data)

        with open(os.path.join(selected_version, "MediumSplash.bak"), "wb") as file:
            file.write(medium_replacement_data)
            
        with open(os.path.join(selected_version, "LargeSplash.bak"), "wb") as file:
            file.write(large_replacement_data)

        try:
            os.remove(small_location)
            os.remove(medium_location)
            os.remove(large_location)
            os.remove(replacement_location)
            pass
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error removing temporary files: {exception}")

        with open(exe_path, "wb") as exe_file:
            exe_file.write(exe_data)

        print("\033[1;32mSUCCESS:\033[0m Banner patched successfully.")

    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m Error fetching legacy banner: {exception}")

def fetch_internal_patch_data():
    try:
        response = requests.get("https://raw.githubusercontent.com/Firebladedoge229/internal-studio-patcher-reversed/refs/heads/main/hex.txt")
        hex_string = response.text.strip()
        hex_bytes = hex_string.split()

        if len(hex_bytes) >= 8:
            original = b"".join(bytes.fromhex(b) for b in hex_bytes[:8])

            for i in range(len(hex_bytes) - 1):
                if hex_bytes[i:i+2] == ["74", "05"]:
                    hex_bytes[i:i+2] = ["90", "90"]
                    break

            patch = b"".join(bytes.fromhex(b) for b in hex_bytes[:8])

            return (original, patch)
        else:
            print("\033[1;31mERROR:\033[0m Not enough bytes in response [need at least 8].")
            return None
    except Exception as e:
        print(f"\033[1;31mERROR:\033[0m Error fetching hex data: {e}")
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
    if getattr(sys, "frozen", False):
        directory = os.path.dirname(sys.executable)
    elif __file__:
        directory = os.path.dirname(__file__)

    settings_file = os.path.join(directory, "RobloxStudioManagerSettings.json")

    try:
        with open(settings_file, "w") as file:
            json.dump(settings, file, indent=4)
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
        with open(settings_file, "r") as file:
            print(f"\033[38;2;52;235;143mDATA:\033[0m FFlag Settings sent from {settings_file}")
            return json.load(file)
    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m Error getting custom settings: {exception}. Have you modified any FastFlags?")
        return {}

def save_custom_flags(settings):
    if getattr(sys, "frozen", False):
        directory = os.path.dirname(sys.executable)
    elif __file__:
        directory = os.path.dirname(__file__)

    settings_file = os.path.join(directory, "RobloxStudioManagerFFlags.json")

    try:
        with open(settings_file, "w") as file:
            json.dump(settings, file, indent=4)
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
    if os.name == "nt":
        clientAppSettings = os.path.join(selected_version, "ClientSettings", "ClientAppSettings.json")
    elif os.name == "posix":
        clientAppSettings = os.path.join(os.environ["HOME"], "Library", "Roblox", "StudioAppSettings.json")
    with open(clientAppSettings) as file: content = file.read()
    return json.loads(content)

def handle_flags(settings):
    json_file_path = os.path.join(os.getcwd(), "fastflags.json")
    if not os.path.exists(json_file_path):
        print("\033[1;31mERROR:\033[0m fastflags.json file not found. Downloading..")
        try:
            response = requests.get("https://raw.githubusercontent.com/Firebladedoge229/RobloxStudioManager/refs/heads/main/data/fastflags.json")
            if response:
                with open("fastflags.json", "w") as file:
                    file.write(response.text)
                print("\033[1;32mSUCCESS:\033[0m fastflags.json downloaded successfully.")
        except Exception as exception:
            print(f"\033[1;31mDATA ERROR:\033[0m Error while downloading fastflags.json: {exception}")
            return

    with open(json_file_path, "r") as file:
        flags_data = json.load(file)

    applied_flags = {}

    if os.name == "nt":
        clientAppSettings = os.path.join(selected_version, "ClientSettings", "ClientAppSettings.json")
    elif os.name == "posix":
        clientAppSettings = os.path.join(os.environ["HOME"], "Library", "Roblox", "StudioAppSettings.json")

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
                    
                    with open(clientAppSettings, "w") as file:
                        json.dump(applied_flags, file, indent=4)
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
                    if "flag" in lowerKey and "betafeature" in lowerKey and "nextgen" not in lowerKey and "assistant" not in lowerKey:
                        applied_flags[key] = True
                        
            if fVariablesSuccess: 
                for line in fvariablesURL.splitlines():
                    key = re.sub(r"\[[^\]]*\]\s*", "", line.strip())
                    lowerKey = key.lower()
                    if "flag" in lowerKey and "betafeature" in lowerKey:
                        applied_flags[key] = True
        
        if settings["Rename Friends to Connections"] == False:
            if clientSettingsSuccess:
                for key, _ in clientAppSettingsURL.items():
                    lowerKey = key.lower()
                    if "rename" in lowerKey and "friend" in lowerKey and "connection" in lowerKey:
                        applied_flags[key] = False
                        
            if fVariablesSuccess: 
                for line in fvariablesURL.splitlines():
                    key = re.sub(r"\[[^\]]*\]\s*", "", line.strip())
                    lowerKey = key.lower()
                    if "rename" in lowerKey and "friend" in lowerKey and "connection" in lowerKey:
                        applied_flags[key] = false

        if settings["Show Flags"] == True:
            flag_list = ""
            for flag in applied_flags:
                flag_list += flag + ","
            applied_flags["FStringDebugShowFlagState"] = flag_list[:-1]

        if not ".app" in selected_version.lower():
            patch_banner(os.path.join(selected_version, "RobloxStudioBeta.exe"), settings["Splash Screen Version"])
        else:
            patch_banner(os.path.join(selected_version), settings["Splash Screen Version"])
            
    if os.name == "nt":
        treePath = os.path.join(os.environ["LOCALAPPDATA"], "Roblox", "GlobalBasicSettings_13_Studio.xml")
    elif os.name == "posix":
        treePath = "/" + os.path.join(os.environ["HOME"], "Library", "Roblox", "GlobalBasicSettings_13_Studio.xml")
    tree = ET.parse(treePath)        
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

    tree.write(treePath, encoding="utf-8", xml_declaration=True)

    if settings["Classic Death Sound"] == True:
        try:
            ouchData = requests.get(legacyOuchURL).content
        except:
            pass
    else:
        try:
            ouchData = requests.get(ouchURL).content
        except:
            pass

    try:
        if os.name == "nt":
            defaultLocation = os.path.join(selected_version, "content", "sounds", "ouch.ogg")
        elif os.name == "posix":
            defaultLocation = "/" + os.path.join(selected_version, "Contents", "Resources", "content", "sounds", "ouch.ogg")

        with open(defaultLocation, "wb") as file:
            file.write(ouchData)
    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m Error while replacing death sound: {exception}")

    if settings["Legacy Cursor"] == True:
        try:
            cursorData = requests.get(legacyCursorURL).content
            cursorFarData = requests.get(legacyCursorFarURL).content
        except:
            pass
    else:
        try:
            cursorData = requests.get(cursorURL).content
            cursorFarData = requests.get(cursorFarURL).content
        except:
            pass

    try:
        if os.name == "nt":
            defaultLocation = os.path.join(selected_version, "content", "textures", "Cursors", "KeyboardMouse")
        elif os.name == "posix":
            defaultLocation = "/" + os.path.join(selected_version, "Contents", "Resources", "content", "textures", "Cursors", "KeyboardMouse")

        with open(defaultLocation + os.path.sep + "ArrowCursor.png", "wb") as file:
            file.write(cursorData)

        with open(defaultLocation + os.path.sep + "ArrowFarCursor.png", "wb") as file:
            file.write(cursorFarData)

    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m Error while replacing cursor: {exception}")

    os.makedirs(os.path.dirname(clientAppSettings), exist_ok=True)

    combined_flags = applied_flags.copy()
    combined_flags.update(get_custom_flags())

    with open(clientAppSettings, "w") as file:
        json.dump(combined_flags, file, indent=4)

    print(f"\033[1;32mSUCCESS:\033[0m Flags have been set in {clientAppSettings}")

def download_and_apply_font(selected_version):
    if os.name == "nt":
        zip_path = os.path.join(selected_version, "content", "fonts", "GothamFont.zip")
    elif os.name == "posix":
        zip_path = "/" + os.path.join(selected_version, "Contents", "Resources", "content", "fonts", "GothamFont.zip")

    try:
        response = requests.get("https://github.com/Firebladedoge229/GothamFont/archive/refs/heads/main.zip", stream=True)
        with open(zip_path, "wb") as output:
            output.write(response.content)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            target_dir = next((file_info.filename for file_info in zip_ref.infolist() if file_info.is_dir()), None)
            if target_dir:
                for file_info in zip_ref.infolist():
                    if file_info.filename.startswith(target_dir) and file_info.filename.endswith((".ttf", ".otf")):
                        if os.name == "nt":
                            dest_path = os.path.join(selected_version, "content", "fonts", os.path.basename(file_info.filename))
                        elif os.name == "posix":
                            dest_path = "/" + os.path.join(selected_version, "Contents", "Resources", "content", "fonts", os.path.basename(file_info.filename))
                        with zip_ref.open(file_info) as source, open(dest_path, "wb") as target:
                            target.write(source.read())

        os.remove(zip_path)
    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m Error Downloading and Applying Font: {exception}")

def get_product_version(exe_path):
    if os.name == "nt":
        command = [
            "powershell",
            "-Command",
            f"(Get-Item '{exe_path}').VersionInfo.ProductVersion"
        ]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        result = stdout.strip().replace(", ", ".")
    elif os.name == "posix":
        regex = re.compile(r"engineversion=.(\d)\.(\d{2,})\.(\d)\.(\d{2,}).")
        executable = "/" + os.path.join(selected_version, "Contents", "MacOS", "RobloxStudio")
        with open(executable, "rb") as file:
            data = file.read()
        data = data.decode("utf-8", errors = "ignore")
        match = regex.search(data)
        if match:
            result = match.group().strip()[15:]
    print(f"\033[1;36mINFO:\033[0m Product Version: {result}")
    return result

def disable_updates(disable, selected_version):
    if os.name == "nt":
        exe_path = os.path.join(selected_version, "RobloxStudioBeta.exe")
        installer = os.path.join(selected_version, "RobloxStudioInstaller.exe")
    elif os.name == "posix":
        exe_path = "/" + os.path.join(selected_version, "Contents", "MacOS", "RobloxStudio")
        installer = "/" + os.path.join(selected_version, "Contents", "MacOS", "RobloxStudioInstaller")

    version = get_product_version(exe_path)

    if not version:
        print("\033[1;31mERROR:\033[0m Unable to get version information.")
        return
    
    print(f"\033[1;36mINFO:\033[0m Version: {version}")   
    latest = re.sub(r"[^\s\.]", "9", version)

    print(f"\033[1;36mINFO:\033[0m Latest: {latest}")  

    if latest:
        try:
            result_bytes = bytes.fromhex("".join(format(ord(c), "02X") for c in version))
            patch_bytes = bytes.fromhex("".join(format(ord(c), "02X") for c in latest))

            with open(exe_path, "r+b") as file:
                if not disable:
                    new_result = patch_bytes
                    new_patch = result_bytes
                    patch_bytes = new_patch
                    result_bytes = new_result
                content = file.read()
                index = content.find(result_bytes)

                if index != -1:
                    file.seek(index)
                    file.write(patch_bytes)
                    print("\033[1;32mSUCCESS:\033[0m Version bytes patched.")
                    if os.path.exists(installer):
                        if os.name == "nt":
                            os.rename(installer, os.path.join(selected_version, "RobloxStudioInstaller-ModManager.exe"))
                        elif os.name == "posix":
                            os.rename(installer, os.path.join(selected_version, "Contents", "MacOS", "RobloxStudioInstaller-ModManager"))
                        print("\033[1;32mSUCCESS:\033[0m Installer renamed successfully.")
                else:
                    print("\033[1;31mERROR:\033[0m Version bytes not found in file.")
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Exception: {exception}")
    else:
        print("\033[1;31mERROR:\033[0m Unable to find version information.")

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
        else:
            print("\033[1;36mINFO:\033[0m User chose not to force quit Roblox Studio.")
            return

    handle_flags(settings)

    if settings.get("Classic Font"):
        download_and_apply_font(selected_version)

    if settings.get("Disable Updates"):
        disable_updates(True, selected_version)
    else:
        disable_updates(False, selected_version)

    if settings.get("Disable Crash Handler"):
        handler = "https://github.com/Firebladedoge229/Uploads/raw/refs/heads/main/RobloxCrashHandler.exe"
        try:
            response = requests.get(handler)
            with open(os.path.join(selected_version, "RobloxCrashHandler.exe"), "wb") as file:
                file.write(response.content)
            print("\033[1;32mSUCCESS:\033[0m Crash Handler disabled.")
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error disabling Crash Handler: {exception}")

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

    try:
        legacyLogoData = requests.get(f"https://raw.githubusercontent.com/Firebladedoge229/RobloxStudioManager/refs/heads/main/misc/icons/{settings.get("Logo Version")}.ico").content

        with open(os.path.join(selected_version, "IDI_ICON1.ico"), "wb") as file:
            file.write(legacyLogoData)
    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m Error while downloading logo: {exception}")
    
    if os.name == "nt":
        try:
            resource = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ResourceHacker.exe")
            response = subprocess.Popen([resource, "-open", os.path.join(selected_version, "RobloxStudioBeta.exe"), "-save", os.path.join(selected_version, "RobloxStudioBeta.exe"), "-action", "addoverwrite", "-res", os.path.join(selected_version, "IDI_ICON1.ico"), "-mask", "ICONGROUP,IDI_ICON1,ICON,1,,ICON,2,,ICON,3,,ICON,4,"])
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Error while replacing logo: {exception}")

def open_browser(url):
    subprocess.Popen(["open", "-u", url])

def reset_configuration():
    if os.name == "nt":
        clientPath = os.path.join(selected_version, "ClientSettings", "ClientAppSettings.json")
    elif os.name == "posix":
        clientPath = os.path.join(os.environ["HOME"], "Library", "Roblox", "StudioAppSettings.json")
    if os.path.exists(clientPath):
        os.remove(clientPath)
        print("\033[1;36mINFO:\033[0m Configuration reset")
    else:
        print("\033[1;31mERROR:\033[0m The file does not exist")
    print("\033[1;36mINFO:\033[0m Reset Configuration clicked")

def open_installation_folder():
    if os.name == "nt":
        subprocess.Popen(["explorer", selected_version])
    elif os.name == "posix":
        subprocess.Popen(["open", "/" + selected_version + "/Contents"])
    print("\033[1;36mINFO:\033[0m Installation Folder clicked")

def launch_studio():
    if os.name == "nt":
        try:
            subprocess.Popen([os.path.join(selected_version, "RobloxStudioBeta.exe")], cwd=selected_version)
        except PermissionError as exception:
            if "used by another process" in str(exception):
                response = ctypes.windll.user32.MessageBoxW(0, "Roblox studio appears to be in use by another process. Do you want to force close it in order to perform this action?", "Roblox Studio Manager", 0x04)
                if response == 6:          
                    for proc in psutil.process_iter(["pid", "name"]):
                        if proc.info["name"] == "RobloxStudioBeta.exe":
                            proc.terminate()
                            print("\033[1;36mINFO:\033[0m Roblox Studio has been forcefully terminated.")
                    subprocess.Popen([os.path.join(selected_version, "RobloxStudioBeta.exe")], cwd=selected_version)
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m Good luck fixing this error: {exception}")
            
    elif os.name == "posix":
        subprocess.Popen(["open", "/" + selected_version], cwd=selected_version)
    print("\033[1;36mINFO:\033[0m Launch Studio clicked")

def update_studio():
    if os.name == "nt":
        exe_path = os.path.join(selected_version, "RobloxStudioInstaller.exe")
    elif os.name == "posix":
        exe_path = os.path.join("/" + selected_version, "Contents", "MacOS", "RobloxStudioInstaller.app")
    if os.path.exists(exe_path):
        subprocess.Popen([exe_path], cwd=selected_version)
    else:
        try:
            subprocess.Popen([os.path.join(selected_version, "RobloxStudioInstaller-ModManager.exe")], cwd=selected_version)
        except Exception as exception:
            print("\033[1;31mERROR:\033[0m The Roblox Studio Installer executable could not be found.")
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

if os.name == "nt":
    selected_version = find_latest_version(os.path.join(os.environ["LOCALAPPDATA"], "Roblox", "Versions"))
    if not selected_version:
        selected_version = find_latest_version(os.path.join(os.environ["PROGRAMFILES(X86)"], "Roblox", "Versions"))
elif os.name == "posix":
    selected_version = find_latest_version(os.path.join("Applications", "RobloxStudio.app"))
    if not selected_version:
        selected_version = find_latest_version(os.path.join(os.environ["HOME"], "Applications", "RobloxStudio.app"))
    if selected_version:
        os.makedirs(os.path.join(selected_version, "Contents", "MacOS"), exist_ok=True)

print(f"\033[1;36mINFO:\033[0m Selected Version: {selected_version}" if selected_version else "\033[1;31mERROR:\033[0m No valid version found.")

def patch_studio_for_themes():
    def patch_studio():
        if os.name == "nt":
            file_path = os.path.join(selected_version, "RobloxStudioBeta.exe")
        elif os.name == "posix":
            file_path = "/" + os.path.join(selected_version, "Contents", "MacOS", "RobloxStudio")

        with open(file_path, "rb") as file:
            file_data = file.read()

        print("\033[1;36mINFO:\033[0m Searching for bytes..")
        patch_done = False
        for i in range(len(file_data) - 3):
            if file_data[i:i+4] == b":/Pl":
                file_data = file_data[:i] + b"./Pl" + file_data[i+4:]
                patch_done = True

        patched_file_path = os.path.join(selected_version, "RobloxStudioBeta.exe")
        with open(patched_file_path, "wb") as file:
            file.write(file_data)

        if not patch_done:
            print("\033[1;36mINFO:\033[0m No bytes found.")
            return

        print("\033[1;32mSUCCESS:\033[0m Successfully patched Roblox Studio for theme use.")
    
    patch_studio()

try:
    target_dir = selected_version
    platform_path = os.path.join(target_dir, "Platform")
    if os.name == "nt":
        base_path = os.path.join(platform_path, "Base", "QtUI", "themes")
    elif os.name == "posix":
        base_path = "/" + os.path.join(target_dir, "Contents", "Resources", "Platform", "Base", "QtUI", "themes")
        response = subprocess.Popen(f"mkdir -p {base_path}", shell=True)
    base_path = os.path.normpath(base_path)
    os.makedirs(platform_path, exist_ok=True)
    os.makedirs(base_path, exist_ok=True)
except:
    print("\033[1;36mINFO:\033[0m No valid Roblox Studio version was found. You will not be able to make any modifications.")
    pass

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
        print(foundation_light_theme_path)
        print("\033[1;32mSUCCESS:\033[0m Theme files downloaded successfully.")
    except Exception as exception:
        print(f"\033[1;31mERROR:\033[0m Failed to download theme files: {exception}")

if not os.path.exists(light_theme_path) and not os.path.exists(dark_theme_path):
    download_default_themes()

def get_theme_colors(selection = "LightTheme"):
    if not os.path.exists(light_theme_path) and not os.path.exists(dark_theme_path):
        download_default_themes()
    if os.name == "posix":
        if not os.path.exists(base_path):
            subprocess.Popen(["mkdir", "-p", base_path])
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

if os.name == "nt":
    disabledPlugins = os.path.join(selected_version, "DisabledPlugins", "Optimized_Embedded_Signature")
elif os.name == "posix":
    disabledPlugins = "/" + os.path.join(selected_version, "Contents", "Resources", "DisabledPlugins", "Optimized_Embedded_Signature")

def get_disabled_plugins():
    file_info = []
    if os.path.isdir(disabledPlugins):
        for root, _, files in os.walk(disabledPlugins):
            for file in files:
                if file.endswith(".rbxm"):
                    name, _ = os.path.splitext(file)
                    split = name.split("-", 2)
                    name = split[0]
                    folder = split[1]
                    file_info.append(f"{folder}/{name}")
    else:
        print(f"\033[1;31mERROR:\033[0m Folder {disabledPlugins} does not exist.")
        subprocess.Popen(["mkdir", "-p", disabledPlugins])
        try:
            os.makedirs(disabledPlugins, exist_ok = True)
        except Exception as exception:
            print(f"\033[1;31mERROR:\033[0m An error occured when creating {disabledPlugins}: {exception}")

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
        if os.name == "nt":
            folder_path = os.path.join(selected_version, folder, "Optimized_Embedded_Signature")
            folder_path = os.path.normpath(folder_path)
        elif os.name == "posix":
            folder_path = "/" + os.path.join(selected_version, "Contents", "Resources", folder, "Optimized_Embedded_Signature")
        if os.path.isdir(folder_path):
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".rbxm"):
                        name, _ = os.path.splitext(file)
                        if os.path.split(os.path.split(root)[0])[1] == "DisabledPlugins":
                            split = name.split("-", 2)
                            name = split[0]
                            folder = split[1]
                            duplicateFile = os.path.join(folder_path, name) + ".rbxm"
                            if os.path.isfile(duplicateFile):
                                os.remove(duplicateFile)
                        file_info[file] = {"name": name, "base_folder": folder, "enabled": os.path.split(os.path.split(root)[0])[1] != "DisabledPlugins"}
        else:
            print(f"\033[1;31mERROR:\033[0m Folder {folder_path} does not exist.")
            try:
                os.makedirs(folder_path, exist_ok = True)
                subprocess.Popen(["mkdir", "-p", folder_path])
            except Exception as exception:
                print(f"\033[1;31mERROR:\033[0m An error occured when creating {folder_path}: {exception}")

    sorted_files = sorted(file_info.values(), key=lambda x: x["name"])
    return sorted_files

fetch = fetch_internal_patch_data()
try:
    internal_signature, internal_patch = fetch
    internal_signature_backup, internal_patch_backup = fetch
except Exception as exception:
    print(f"\033[1;31mERROR:\033[0m Error fetching internal patch data: {exception}")
