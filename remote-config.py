from lxml import etree
import requests
import json
import os
import argparse
from termcolor import colored

def get_string_value(xml, setting_name):
    value = xml.xpath(f"/resources/string[@name='{setting_name}']")
    if value and value[0].text:
        print(f"[+] Found value for '{setting_name}': {value[0].text}")
        return value[0].text
    return None

def find_strings_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        if 'strings.xml' in files:
            yield os.path.join(root, 'strings.xml')

# Argument parser
parser = argparse.ArgumentParser(description='Find and use strings.xml in decompiled APK folders')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-d', '--decompiled-folder', help='Path to a single decompiled folder')
group.add_argument('-D', '--decompiled-parent-folder', help='Path to parent folder containing multiple decompiled folders')

args = parser.parse_args()

if args.decompiled_folder:
    folder_paths = [args.decompiled_folder]
else:
    folder_paths = [os.path.join(args.decompiled_parent_folder, d) for d in os.listdir(args.decompiled_parent_folder) if os.path.isdir(os.path.join(args.decompiled_parent_folder, d))]

for folder_path in folder_paths:
    already_scanned = False  # Initialize flag for each folder path
    already_done = False  # Initialize flag for 'Scanning Done!' for each folder path
    
    for strings_path in find_strings_files(folder_path):
        if os.path.exists(strings_path):
            if not already_scanned:
                print(colored(f"[+] Scanning Folder: {folder_path}", "green"))
                already_scanned = True  # Update the flag
                
            with open(strings_path, 'r') as f:
                xml = etree.parse(f)

            google_api_key = get_string_value(xml, 'google_api_key')
            google_app_id = get_string_value(xml, 'google_app_id')

            if google_app_id and ':' in google_app_id:
                project_id = google_app_id.split(':')[1]
                print(colored(f'[*] Recovering Firebase Remote Config for folder: {folder_path}', "cyan"))

                url = f"https://firebaseremoteconfig.googleapis.com/v1/projects/{project_id}/namespaces/firebase:fetch?key={google_api_key}"

                headers = {'Content-Type': 'application/json'}
                payload = json.dumps({'appId': google_app_id, 'appInstanceId': 'required_but_unused_value'})

                response = requests.post(url, data=payload, headers=headers)
                
                if response.status_code == 200:
                    print(colored(response.text, "green"))
                else:
                    print(colored(response.text, "red"))

    # Moved these two lines outside the inner loop
    if not already_done:
        print(colored("Scanning Done!", "yellow"))
        print(colored("-" * 80, "magenta"))  # Add a separator line
        already_done = True  # Update the flag
