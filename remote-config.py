from lxml import etree
import requests
import json
import os
import argparse

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
parser.add_argument('-d', '--decompiled-folder', required=True, help='Path to decompiled folder')

args = parser.parse_args()
folder_path = args.decompiled_folder

for strings_path in find_strings_files(folder_path):
    if os.path.exists(strings_path):
        with open(strings_path, 'r') as f:
            xml = etree.parse(f)
        
        google_api_key = get_string_value(xml, 'google_api_key')
        google_app_id = get_string_value(xml, 'google_app_id')
        
        if google_app_id:
            project_id = google_app_id.split(':')[1]
            print('[*] Recovering Firebase Remote Config')
            
            url = f"https://firebaseremoteconfig.googleapis.com/v1/projects/{project_id}/namespaces/firebase:fetch?key={google_api_key}"
            
            headers = {'Content-Type': 'application/json'}
            payload = json.dumps({'appId': google_app_id, 'appInstanceId': 'required_but_unused_value'})
            
            response = requests.post(url, data=payload, headers=headers)
            
            print(response.text)
