import os
import requests
import zipfile
import hashlib
import subprocess

try:
    locations = requests.get("https://raw.githubusercontent.com/MaximumADHD/Roblox-Studio-Mod-Manager/cd3a3444ce36a03b5cf03113ed1a18bd93bb3823/Config/KnownRoots.json").json()
except Exception as exception:
    print(f"\033[1;31mERROR:\033[0m Error fetching install directories {exception}")

appSettings = """<?xml version="1.0" encoding="UTF-8"?>
<Settings>
	<ContentFolder>content</ContentFolder>
	<BaseUrl>http://www.roblox.com</BaseUrl>
</Settings>"""

def fetch_version(channel):
    if channel:
        url = f"https://setup.rbxcdn.com/channel/{channel}/versionQTStudio"
    else:
        url = "https://setup.rbxcdn.com/versionQTStudio"
    response = requests.get(url)
    response.raise_for_status()
    return response.text.strip()

def fetch_manifest(version, channel):
    if channel:
        url = f"https://setup.rbxcdn.com/channel/{channel}/{version}-rbxPkgManifest.txt"
    else:
        url = f"https://setup.rbxcdn.com/{version}-rbxPkgManifest.txt"
    print(f"\033[1;36mINFO:\033[0m Fetching Manifest: {url}")
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

def validate_md5(file_path, expected_md5):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest() == expected_md5

def download_file(url, output_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))
    downloaded_size = 0
    with open(output_path, "wb") as file:
        for chunk in response.iter_content(1024):
            file.write(chunk)
            downloaded_size += len(chunk)
            if total_size:
                percent = (downloaded_size / total_size) * 100
                print(f"\r{output_path}: {percent:.2f}% complete", end="")
    print()

def extract_zip(file_path, extract_to):
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def capitalize_after_z(channel):
    new_channel = ""
    i = 0
    while i < len(channel) - 1:
        new_channel += channel[i]
        if channel[i] == "z":
            new_channel += channel[i + 1].upper()
            i += 1
        i += 1
    if i < len(channel):
        new_channel += channel[i]
    return new_channel


def download_and_extract(version, file_name, file_md5, channel, selected_folder, locations):
    formatted_channel = capitalize_after_z(channel) if channel else ""
    folder_name = f"{formatted_channel}-{version}" if channel else version
    output_path = os.path.join(selected_folder, folder_name, file_name)
    url = f"https://setup.rbxcdn.com/channel/{channel}/{version}-{file_name}" if channel else f"https://setup.rbxcdn.com/{version}-{file_name}"
    download_file(url, output_path)
    if not validate_md5(output_path, file_md5):
        print(f"\033[1;31mDATA ERROR:\033[0m Checksum Mismatch for {file_name}.")
        return
    else:
        print(f"\033[1;32mSUCCESS:\033[0m Checksum Validated for {file_name}.")
    location_info = locations.get(file_name.replace(".zip", ""), None)
    if location_info and "ExtractTo" in location_info:
        extract_to = os.path.join(selected_folder, folder_name, location_info["ExtractTo"])
        os.makedirs(extract_to, exist_ok=True)
        extract_zip(output_path, extract_to)
        os.remove(output_path)
        print(f"\033[38;2;52;235;143mDATA:\033[0m Deleted Zip File: {output_path}")
    else:
        print(f"\033[1;31mDATA ERROR:\033[0m No valid location found for {file_name}. Skipping extraction.")


def download(selected_folder, channel):
    channel = channel
    print("\033[1;36mINFO:\033[0m Download Clicked")
    selected_version = fetch_version(channel)
    print(f"\033[1;36mINFO:\033[0m Selected Version: {selected_version}")
    manifest = fetch_manifest(selected_version, channel)
    formatted_channel = capitalize_after_z(channel) if channel else ""
    folder_name = f"{formatted_channel}-{selected_version}" if channel else selected_version
    os.makedirs(os.path.join(selected_folder, folder_name), exist_ok=True)
    i = 0
    while i < len(manifest):
        file_name = manifest[i].strip()
        if file_name.endswith(".zip"):
            file_md5 = manifest[i + 1].strip() if i + 1 < len(manifest) else ""
            print(f"\033[1;36mINFO:\033[0m Processing {file_name}")
            download_and_extract(selected_version, file_name, file_md5, channel, selected_folder, locations)
            i += 4
        else:
            i += 1
    with open(os.path.join(selected_folder, folder_name, "AppSettings.xml"), "w") as f:
        f.write(appSettings)
    print("\033[1;32mSUCCESS\033[0m Download Complete")
    from ui_components import endDownload
    endDownload()
    subprocess.Popen(["explorer", os.path.join(selected_folder, folder_name)])
