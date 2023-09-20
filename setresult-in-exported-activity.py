import xml.etree.ElementTree as ET
import argparse
import os
from glob import glob
from colorama import Fore, Style
from xml.etree.ElementTree import ParseError

class AndroidManifestAnalyzer:
    def __init__(self, manifest_path):
        try:
            self.tree = ET.parse(manifest_path)
            self.root = self.tree.getroot()
        except ET.ParseError:  # Notice the change here, added ET. before ParseError
            print(f"{Fore.RED}Could not parse {manifest_path}. Skipping.{Style.RESET_ALL}")
            self.root = None


    def get_exported_activities(self):
        activities = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for activity in self.root.findall(".//activity", namespaces=ns):
            exported = activity.get('{http://schemas.android.com/apk/res/android}exported')
            enabled = activity.get('{http://schemas.android.com/apk/res/android}enabled', "true")
            intent_filters = activity.findall(".//intent-filter", namespaces=ns)
            if (exported == "true" or (exported is None and intent_filters)) and enabled == "true":
                name = activity.get('{http://schemas.android.com/apk/res/android}name')
                activities.append(name)
        return activities

def scan_java_file_for_setResult(java_file_path):
    with open(java_file_path, 'r') as f:
        lines = f.readlines()
        for idx, line in enumerate(lines):
            if "setResult(" in line:
                print(f"{Fore.RED}setResult found in exported activity:{Style.RESET_ALL} {Fore.MAGENTA}{java_file_path}{Style.RESET_ALL} \nline {idx + 1}: {Fore.YELLOW}{line.strip()}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan AndroidManifest.xml and Java source files for vulnerabilities.")
    parser.add_argument("-d", "--directory", help="Path to a single decompiled APK folder")
    parser.add_argument("-D", "--directories", help="Path to multiple decompiled APK folders")
    args = parser.parse_args()

    directories_to_search = []

    if args.directory:
        directories_to_search.append(args.directory)

    if args.directories:
        directories_to_search.extend(glob(f"{args.directories}/*"))

    for directory in directories_to_search:
        manifest_path = glob(os.path.join(directory, "**", "AndroidManifest.xml"), recursive=True)
        manifest_path = manifest_path[0] if manifest_path else None  # Get first element or default to None
        if manifest_path:
            analyzer = AndroidManifestAnalyzer(manifest_path)
            if analyzer.root is None:  # Skip if XML could not be parsed
                continue
            exported_activities = analyzer.get_exported_activities()
            for activity_name in exported_activities:
                search_path = os.path.join(directory, '**', activity_name.split('.')[-1] + ".java")
                for java_file_path in glob(search_path, recursive=True):
                    scan_java_file_for_setResult(java_file_path)
