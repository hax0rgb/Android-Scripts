import xml.etree.ElementTree as ET
import argparse
import os
import re
import glob

# ANSI escape code for red color
RED_COLOR = "\033[91m"
RESET_COLOR = "\033[0m"

class AndroidManifestAnalyzer:
    def __init__(self, manifest_path):
        self.tree = ET.parse(manifest_path)
        self.root = self.tree.getroot()

    def get_exported_components(self):
        components = []
        ns = {'android': 'http://schemas.android.com/apk/res/android'}
        for component in self.root.findall(".//*", namespaces=ns):
            exported = component.get('{http://schemas.android.com/apk/res/android}exported')
            enabled = component.get('{http://schemas.android.com/apk/res/android}enabled', "true")
            intent_filters = component.findall(".//intent-filter", namespaces=ns)
            if (exported == "true" or (exported is None and intent_filters)) and enabled == "true":
                name = component.get('{http://schemas.android.com/apk/res/android}name')
                components.append(name)
        return components

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
            formatted_output = f"{RED_COLOR}Intent redirection identified in {component_full_name}{RESET_COLOR}\n"
            for vulnerability in vulnerabilities:
                formatted_output += f"source: {vulnerability['source']} on line {vulnerability['source_line']}\n"
                formatted_output += f"sink: {vulnerability['sink']} on line {vulnerability['sink_line']}\n"
            return formatted_output
        else:
            return None

    except Exception as e:
        print(f"Error scanning file {file_path}: {e}")
        return None

    except Exception as e:
        print(f"Error scanning file {file_path}: {e}")
        return None

def find_manifest_file(decompiled_folder):
    for filename in glob.glob(decompiled_folder + '/**/AndroidManifest.xml', recursive=True):
        return filename
    return None

def find_java_files(decompiled_folder, component_name):
    expected_file_name = component_name.split('.')[-1] + '.java'
    for filename in glob.glob(decompiled_folder + '/**/' + expected_file_name, recursive=True):
        return filename
    return None

def main(decompiled_folder):
    manifest_path = find_manifest_file(decompiled_folder)
    analyzer = AndroidManifestAnalyzer(manifest_path)
    exported_components = analyzer.get_exported_components()

    for component in exported_components:
        file_path = find_java_files(decompiled_folder, component)

        if file_path:
            vulnerabilities_output = check_intent_redirection(file_path, component, exported_components)
            if vulnerabilities_output:
                print(vulnerabilities_output)
        else:
            print(f"Source code file not found for component: {component}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for intent redirection vulnerabilities in a decompiled Android app.")
    parser.add_argument('folder', help="Path to the decompiled app folder")
    args = parser.parse_args()
    main(args.folder)
