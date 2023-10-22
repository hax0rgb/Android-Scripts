import os
import subprocess
import argparse

def is_potentially_minified(filename):
    """Determine if a file could be minified based on its name."""
    return filename == "index.android.bundle" or filename.endswith(".min.js") or filename.endswith(".js")

def beautify_js_file(file_path):
    """Use js-beautify to convert potentially minified JS into pretty format."""
    if file_path.endswith("index.android.bundle"):
        pretty_file_path = file_path.replace("index.android.bundle", "index.android.beautified.js")
    elif file_path.endswith(".min.js"):
        pretty_file_path = file_path.replace(".min.js", ".js")
    else:
        pretty_file_path = file_path.replace(".js", ".beautified.js")
    
    cmd = ['js-beautify', '-o', pretty_file_path, file_path]
    subprocess.run(cmd)
    if os.path.exists(pretty_file_path):  # Ensure the beautified file exists before deleting the original
        os.remove(file_path)
        print(f"Beautified: {pretty_file_path}")
    else:
        print(f"Error beautifying: {file_path}")

def main(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if is_potentially_minified(filename):
                file_path = os.path.join(dirpath, filename)
                beautify_js_file(file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Beautify potentially minified JS files in decompiled Android folder.')
    parser.add_argument('-d', '--directory', required=True, help='Path to the decompiled Android folder.')

    args = parser.parse_args()
    
    main(args.directory)
