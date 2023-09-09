import xml.etree.ElementTree as ET
import argparse
import os
from colorama import Fore, Style, init
import glob
from collections import defaultdict

init(autoreset=True)

class AndroidManifestAnalyzer:
    def __init__(self, manifest_path):
        self.tree = ET.parse(manifest_path)
        self.root = self.tree.getroot()

    def get_exported_activities(self):
        activities = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for activity in self.root.findall(".//activity", namespaces=ns):
            exported = activity.get('{http://schemas.android.com/apk/res/android}exported')
            intent_filters = activity.findall(".//intent-filter", namespaces=ns)
            if exported == "true" or (exported is None and intent_filters):
                name = activity.get('{http://schemas.android.com/apk/res/android}name')
                activities.append(name)
        return activities

    def get_exported_providers(self):
        providers = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for provider in self.root.findall(".//provider", namespaces=ns):
            exported = provider.get('{http://schemas.android.com/apk/res/android}exported')
            if exported == "true":
                name = provider.get('{http://schemas.android.com/apk/res/android}name')
                providers.append(name)
        return providers

    def get_exported_services(self):
        services = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for service in self.root.findall(".//service", namespaces=ns):
            exported = service.get('{http://schemas.android.com/apk/res/android}exported')
            if exported == "true":
                name = service.get('{http://schemas.android.com/apk/res/android}name')
                services.append(name)
        return services

    def get_exported_receivers(self):
        receivers = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for receiver in self.root.findall(".//receiver", namespaces=ns):
            exported = receiver.get('{http://schemas.android.com/apk/res/android}exported')
            if exported == "true":
                name = receiver.get('{http://schemas.android.com/apk/res/android}name')
                receivers.append(name)
        return receivers

    def get_deeplinks(self):
        deeplinks = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for activity in self.root.findall(".//activity", namespaces=ns):
            for intent_filter in activity.findall(".//intent-filter", namespaces=ns):
                actions = intent_filter.findall(".//action", namespaces=ns)
                data_elements = intent_filter.findall(".//data", namespaces=ns)

                if actions and data_elements:
                    for data in data_elements:
                        scheme = data.get('{http://schemas.android.com/apk/res/android}scheme')
                        host = data.get('{http://schemas.android.com/apk/res/android}host')
                        path = data.get('{http://schemas.android.com/apk/res/android}path')
                        path_prefix = data.get('{http://schemas.android.com/apk/res/android}pathPrefix')
                        if scheme and host:
                            deeplink = f"{scheme}://{host}"
                            if path:
                                deeplink += path
                            elif path_prefix:
                                deeplink += path_prefix
                            deeplinks.append(deeplink)
                            
        return deeplinks



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze AndroidManifest.xml to find exported components and deeplinks.")
    parser.add_argument("-d", "--directory", help="Path to the folder containing or nested with AndroidManifest.xml")
    parser.add_argument("-D", "--decompiled_directory", help="Path to the folder containing multiple decompiled APKs")

    args = parser.parse_args()

    manifest_files = {}  # Change to a dictionary

    if args.directory:
        for f in glob.glob(os.path.join(args.directory, '**', 'AndroidManifest.xml'), recursive=True):
            manifest_files[f] = False  # False means verbose output

    if args.decompiled_directory:
        print(f"{Fore.MAGENTA}Analyzing all the decompiled APKs in the folder: {args.decompiled_directory}{Fore.RESET}")  # Print the summary message for -D option
        for f in glob.glob(os.path.join(args.decompiled_directory, '**', 'AndroidManifest.xml'), recursive=True):
            manifest_files[f] = True  # True means compact output

    if not manifest_files:
        print(f"{Fore.RED}Error: No AndroidManifest.xml found in the specified directory or its subdirectories.{Fore.RESET}")
    else:
        summary = defaultdict(list)

        for manifest_path, compact_output in manifest_files.items():
            if not compact_output:
                print(f"{Fore.MAGENTA}Analyzing: {manifest_path}{Fore.RESET}")

            analyzer = AndroidManifestAnalyzer(manifest_path)
            
            activities = analyzer.get_exported_activities()
            summary["Exported Activities"] += activities

            providers = analyzer.get_exported_providers()
            summary["Exported Providers"] += providers

            services = analyzer.get_exported_services()
            summary["Exported Services"] += services

            receivers = analyzer.get_exported_receivers()
            summary["Exported Receivers"] += receivers

            deeplinks = analyzer.get_deeplinks()
            summary["Deeplinks"] += deeplinks

        print(f"{Fore.MAGENTA} {Fore.RESET}")
        for key, values in summary.items():
            print(f"{Fore.YELLOW}[+] {key}{Fore.RESET}")
            for value in sorted(set(filter(None, values))):  # Filter out None values
                print(f"{Fore.GREEN}{value}{Fore.RESET}")
            print()