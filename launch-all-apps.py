import subprocess
import time

# Get the list of installed packages
result = subprocess.run(['adb', 'shell', 'pm', 'list', 'packages', '-f'], stdout=subprocess.PIPE, text=True)
pkg_list = result.stdout.split('\n')

# Loop through each package and launch it
for pkg_line in pkg_list:
    if pkg_line:
        pkg = pkg_line.split('=')[-1].strip()
        print(f"Launching {pkg}...")
        subprocess.run(['adb', 'shell', 'monkey', '-p', pkg, '-c', 'android.intent.category.LAUNCHER', '1'])
        time.sleep(10)  # Sleep for 5 seconds between launching apps
