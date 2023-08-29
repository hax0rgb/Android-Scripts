import os
import subprocess

# Ask user for the directory containing APK files
APK_DIR = input("Please enter the directory path where the APK files are located: ")

# Check if the provided directory path exists
if not os.path.isdir(APK_DIR):
    print("The provided directory does not exist. Exiting.")
    exit(1)

# Ensure the directory path ends with a '/'
if not APK_DIR.endswith('/'):
    APK_DIR += '/'

# List all files in the directory
for filename in os.listdir(APK_DIR):
    if filename.endswith('.apk'):
        apk_file_path = os.path.join(APK_DIR, filename)
        print(f"Installing {apk_file_path}...")
        
        # Run adb install command
        subprocess.run(["adb", "install", apk_file_path])
