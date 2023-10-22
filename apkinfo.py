import os
import hashlib
import xml.etree.ElementTree as ET
import argparse
from colorama import Fore, Style, init

init(autoreset=True)  # Automatically reset colors back to normal after each print


def read_manifest(manifest_path):
    """Read and parse the AndroidManifest.xml."""
    namespace = {'android': 'http://schemas.android.com/apk/res/android'}
    
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    
    version_name = root.attrib.get(f'{{{namespace["android"]}}}versionName', 'N/A')
    min_sdk_version = 'N/A'
    target_sdk_version = 'N/A'
    
    for elem in root.findall('uses-sdk', namespace):
        min_sdk_version = elem.attrib.get(f'{{{namespace["android"]}}}minSdkVersion', 'N/A')
        target_sdk_version = elem.attrib.get(f'{{{namespace["android"]}}}targetSdkVersion', 'N/A')
        break
    
    return version_name, min_sdk_version, target_sdk_version

def guess_technology(decompiled_folder):
    """Guess the technology used based on file types and folder structure."""
    for root, _, files in os.walk(decompiled_folder):
        if 'index.android.bundle' in files:
            return 'React Native'
        if 'assemblies.manifest' in files:
            return 'Xamarin'
        if any(f.endswith('.kt') for f in files):
            return 'Kotlin'
        if any(f.endswith('.java') for f in files):
            return 'Java'
        if 'www' in root:
            return 'Cordova'
    
    return 'Unknown'

def find_manifest(decompiled_folder):
    for root, _, files in os.walk(decompiled_folder):
        if 'AndroidManifest.xml' in files:
            return os.path.join(root, 'AndroidManifest.xml')
    return None

def main():
    parser = argparse.ArgumentParser(description='Extract basic information from a decompiled APK folder.')
    parser.add_argument('-d', '--decompiled-folder', required=True, help='Path to the decompiled APK folder.')
    args = parser.parse_args()

    decompiled_folder = args.decompiled_folder
    
    if not os.path.exists(decompiled_folder):
        print("Decompiled folder doesn't exist.")
        return
    
    manifest_path = find_manifest(decompiled_folder)
    if manifest_path is None:
        print("AndroidManifest.xml is missing in the decompiled folder.")
        return
    
    version_name, min_sdk_version, target_sdk_version = read_manifest(manifest_path)
    
    technology = guess_technology(decompiled_folder)
    
    
    print(f"{Fore.MAGENTA}\nApp Information:")
    print(f"{Fore.GREEN}Version Name: {Style.RESET_ALL}{version_name}")
    print(f"{Fore.GREEN}Minimum SDK Version: {Style.RESET_ALL}{min_sdk_version}")
    print(f"{Fore.GREEN}Target SDK Version: {Style.RESET_ALL}{target_sdk_version}")
    print(f"{Fore.GREEN}Technology: {Style.RESET_ALL}{technology}")

if __name__ == "__main__":
    main()
