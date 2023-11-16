from lxml import etree as ET
import argparse
import os
import glob
import re
from colorama import Fore, Style, init

init(autoreset=True)

# AndroidManifestAnalyzer class from android_exposure.py
class AndroidManifestAnalyzer:
    def __init__(self, manifest_path):
        parser = ET.XMLParser(recover=True)
        self.tree = ET.parse(manifest_path, parser)
        self.root = self.tree.getroot()

    def get_exported_activities(self):
        activities = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for activity in self.root.findall(".//activity", namespaces=ns):
            exported = activity.get('{http://schemas.android.com/apk/res/android}exported')
            enabled = activity.get('{http://schemas.android.com/apk/res/android}enabled', "true")
            intent_filters = activity.findall(".//intent-filter", namespaces=ns)
            if (exported == "true" or (exported is None and intent_filters)) and enabled != "false":
                name = activity.get('{http://schemas.android.com/apk/res/android}name')
                activities.append(name)
        return activities

    def get_exported_providers(self):
        providers = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for provider in self.root.findall(".//provider", namespaces=ns):
            exported = provider.get('{http://schemas.android.com/apk/res/android}exported')
            enabled = provider.get('{http://schemas.android.com/apk/res/android}enabled', "true")
            if exported == "true" and enabled != "false":
                name = provider.get('{http://schemas.android.com/apk/res/android}name')
                providers.append(name)
        return providers

    def get_exported_services(self):
        services = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for service in self.root.findall(".//service", namespaces=ns):
            exported = service.get('{http://schemas.android.com/apk/res/android}exported')
            enabled = service.get('{http://schemas.android.com/apk/res/android}enabled', "true")
            if exported == "true" and enabled != "false":
                name = service.get('{http://schemas.android.com/apk/res/android}name')
                services.append(name)
        return services

    def get_exported_receivers(self):
        receivers = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for receiver in self.root.findall(".//receiver", namespaces=ns):
            exported = receiver.get('{http://schemas.android.com/apk/res/android}exported')
            enabled = receiver.get('{http://schemas.android.com/apk/res/android}enabled', "true")
            if exported == "true" and enabled != "false":
                name = receiver.get('{http://schemas.android.com/apk/res/android}name')
                receivers.append(name)
        return receivers

# Functions from intent_redirection.py
def check_intent_redirection(file_path, component_full_name, exported_components):
    vulnerability_title = "Intent Redirection"
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()

        source_pattern = re.compile(r'(Intent|android\.content\.Intent)\s+(\w+)\s*=\s*\(\s*\1\s*\)\s*getIntent\(\)\s*\.getParcelableExtra\(')
        sink_patterns = {
            'startActivity': re.compile(r'startActivity\(\s*(\w+)\s*(?:,.*)?\)'),
            'startActivityForResult': re.compile(r'startActivityForResult\(\s*(\w+)\s*(?:,.*)?\)'),
            'sendBroadcast': re.compile(r'sendBroadcast\(\s*(\w+)\s*(?:,.*)?\)'),
            'startService': re.compile(r'startService\(\s*(\w+)\s*(?:,.*)?\)')
        }

        sources = {}
        vulnerabilities = []

        for i, line in enumerate(content):
            source_search = source_pattern.search(line)
            if source_search:
                source_variable = source_search.group(2)
                source_line = i + 1
                sources[source_variable] = {'line': source_line, 'code': line.strip()}

        for i, line in enumerate(content):
            for sink_action, sink_regex in sink_patterns.items():
                sink_search = sink_regex.search(line)
                if sink_search:
                    sink_variable = sink_search.group(1)
                    if sink_variable in sources:
                        source_info = sources[sink_variable]
                        source_line = source_info['line']
                        source_code = source_info['code']
                        sink_line = i + 1
                        vulnerabilities.append({
                            'source': source_code,
                            'source_line': source_line,
                            'sink': line.strip(),
                            'sink_line': sink_line
                        })

        if vulnerabilities:
            formatted_output = f"{Fore.RED}Intent redirection identified in {component_full_name}{Fore.RESET}\n"
            for vulnerability in vulnerabilities:
                formatted_output += f"source: {vulnerability['source']} on line {vulnerability['source_line']}\n"
                formatted_output += f"sink: {vulnerability['sink']} on line {vulnerability['sink_line']}\n"
            return formatted_output
        else:
            return None

    except Exception as e:
        print(f"Error scanning file {file_path}: {e}")
        return None

def find_manifest_file(decompiled_folder):
    for filename in glob.glob(decompiled_folder + '/**/AndroidManifest.xml', recursive=True):
        return filename
    return None

def find_java_files(manifest_directory, component_name):
    expected_file_name = component_name.split('.')[-1] + '.java'
    base_directory = os.path.dirname(manifest_directory)  # Go up one directory level from the manifest file
    search_path = os.path.join(base_directory, 'sources', '**', expected_file_name)
    for filename in glob.glob(search_path, recursive=True):
        return filename
    return None

# Main function
def main(directory, decompiled_directory, verbose):
    manifest_files = []

    if directory:
        manifest_files = glob.glob(os.path.join(directory, '**', 'AndroidManifest.xml'), recursive=True)

    if decompiled_directory:
        print(f"{Fore.MAGENTA}Analyzing all the decompiled APKs in the folder: {decompiled_directory}{Fore.RESET}\n")
        manifest_files += glob.glob(os.path.join(decompiled_directory, '**', 'AndroidManifest.xml'), recursive=True)

    if not manifest_files:
        print(f"{Fore.RED}Error: No AndroidManifest.xml found in the specified directory or its subdirectories.{Fore.RESET}")
        return

    for manifest_path in manifest_files:
        # Print the analyzing statement for each manifest file
        print(f"{Fore.MAGENTA}Analyzing: {manifest_path}{Fore.RESET}")

        analyzer = AndroidManifestAnalyzer(manifest_path)
        exported_activities = analyzer.get_exported_activities()
        exported_providers = analyzer.get_exported_providers()
        exported_services = analyzer.get_exported_services()
        exported_receivers = analyzer.get_exported_receivers()
        exported_components = exported_activities + exported_providers + exported_services + exported_receivers

        for component in exported_components:
            if component is None:
                continue  # Skip processing if the component is None

            file_path = find_java_files(os.path.dirname(manifest_path), component)
            if file_path:
                vulnerabilities_output = check_intent_redirection(file_path, component, exported_components)
                if vulnerabilities_output:
                    print(vulnerabilities_output)
            elif verbose:
                print(f"Source code file not found for component: {component} in directory: {os.path.dirname(manifest_path)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine exported component identification with intent redirection checks.")
    parser.add_argument("-d", "--directory", help="Path to the folder containing or nested with AndroidManifest.xml")
    parser.add_argument("-D", "--decompiled_directory", help="Path to the folder containing multiple decompiled APKs")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose output")
    args = parser.parse_args()
    main(args.directory, args.decompiled_directory, args.verbose)
