import os
import re
import argparse
import requests
import urllib.request, urllib.error

class bcolors:
    INFO = '\033[94m'
    ENDC = '\033[0m'
    ERROR = '\033[91m'
    INSECURE_WS = '\033[91m'
    SECURE = '\033[92m'
    OUTPUT_WS = '\033[96m'
    CONNECTIVITY = '\033[93m'

def myPrint(text, type):
    if args.verbose or type in ["INSECURE_WS", "CONNECTIVITY"]:
        color = {
            "INFO": bcolors.INFO,
            "ERROR": bcolors.ERROR,
            "INSECURE_WS": bcolors.INSECURE_WS,
            "SECURE": bcolors.SECURE,
            "OUTPUT_WS": bcolors.OUTPUT_WS,
            "CONNECTIVITY": bcolors.CONNECTIVITY
        }.get(type, bcolors.ENDC)
        
        print(color + text + bcolors.ENDC)

def find_strings_xml(folder_path):
    target_path = os.path.join(folder_path, 'resources', 'res', 'values', 'strings.xml')
    if os.path.exists(target_path):
        return target_path
    return None

def extract_firebase_url(strings_xml_path):
    with open(strings_xml_path, 'r') as f:
        content = f.read()
        match = re.search(r'https://[a-zA-Z0-9-]+\.firebaseio\.com', content)
        if match:
            return match.group(0).split("//")[1].split(".")[0]
    return None

def test_write_access(project):
    print(bcolors.INFO + "\033[1m" + "Checking for Write Access...." + bcolors.ENDC)
    site_url = f"https://{project}.firebaseio.com/users/test.json"
    data = {"Exploit": "Testing", "name": "test_user"}
    response = requests.put(site_url, json=data)
    
    if response.status_code == 200:
        print(bcolors.INSECURE_WS + "Write Access Enabled!!" + bcolors.ENDC)
    elif response.status_code == 401:
        print(bcolors.SECURE + "Write Access Not Enabled!" + bcolors.ENDC)
    elif response.status_code == 404:
        print(bcolors.OUTPUT_WS + "Firebase DB Not Found" + bcolors.ENDC)
    else:
        print(bcolors.OUTPUT_WS + "Unknown Error" + bcolors.ENDC)

def check_firebase_db(firebaseProjectList):
    for project in firebaseProjectList:
        url = 'https://' + project + '.firebaseio.com/.json'
        try:
            response = urllib.request.urlopen(url)
            content = response.read().decode('utf-8')
        except urllib.error.HTTPError as err:
            if err.code == 401:
                myPrint(f"Secure Firebase Instance Found: {project}", "SECURE")
            elif err.code == 404:
                myPrint(f"Project does not exist: {project}", "OUTPUT_WS")
            else:
                myPrint("Unable to identify misconfiguration.", "OUTPUT_WS")
            continue
        except urllib.error.URLError as err:
            myPrint("Facing connectivity issues. Please check the network connectivity and try again.", "CONNECTIVITY")
            continue
        
        myPrint(f"Read Access Enabled For Firebase Database: {project}", "INSECURE_WS")
        
        if args.verbose:
            print(f"Response content: {content}")
        
        if args.write:
            test_write_access(project)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check if Firebase databases are world-readable or writable")
    parser.add_argument('-r', '--read', help='Test for read access', action='store_true')
    parser.add_argument('-w', '--write', help='Test for write access', action='store_true')
    parser.add_argument('-d', '--decompiled-folder', help='Path to a single decompiled folder')
    parser.add_argument('-D', '--decompiled-dir', help='Path to a directory containing multiple decompiled folders')
    parser.add_argument('-v', '--verbose', help='Verbose mode', action='store_true')
    args = parser.parse_args()

    if not args.read and not args.write:
        print("Please specify at least one of the flags --read or --write.")
        exit(1)

    firebaseProjectList = []

    if args.decompiled_folder:
        strings_xml_path = find_strings_xml(args.decompiled_folder)
        if strings_xml_path:
            firebase_url = extract_firebase_url(strings_xml_path)
            if firebase_url:
                firebaseProjectList.append(firebase_url)

    if args.decompiled_dir:
        for folder_name in os.listdir(args.decompiled_dir):
            folder_path = os.path.join(args.decompiled_dir, folder_name)
            if os.path.isdir(folder_path):
                strings_xml_path = find_strings_xml(folder_path)
                if strings_xml_path:
                    firebase_url = extract_firebase_url(strings_xml_path)
                    if firebase_url:
                        firebaseProjectList.append(firebase_url)
                        
    if firebaseProjectList:
        check_firebase_db(firebaseProjectList)
    else:
        print("No Firebase instances found for scanning.")
