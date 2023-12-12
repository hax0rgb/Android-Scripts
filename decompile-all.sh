#!/bin/bash

# Prompt user for directory containing APK files
read -p "Enter the path to the folder containing APK files: " APK_DIR

# Prompt user for directory to save the decompiled results
read -p "Enter the path to the folder where you want to save the decompiled results: " RESULTS_PATH

# Check if the provided APK directory exists
if [ ! -d "$APK_DIR" ]; then
    echo "Error: APK directory $APK_DIR does not exist!"
    exit 1
fi

# Check if the results directory exists; if not, create it
[ ! -d "$RESULTS_PATH" ] && mkdir -p "$RESULTS_PATH"

# A flag to check if any APKs were found
APK_FOUND=false

# Iterate over each APK in the directory (and subdirectories) and decompile it
while IFS= read -r APK_FILE; do
    # Mark that we've found at least one APK
    APK_FOUND=true

    # Get the base name of the APK (without extension) to create a separate folder for each APK's decompiled code
    APK_NAME=$(basename "$APK_FILE" .apk)

    # Create a unique path for this APK to avoid overwriting in case of same names in different subdirectories
    RELATIVE_PATH=$(dirname "${APK_FILE#$APK_DIR/}")
    SAVE_PATH="$RESULTS_PATH/$RELATIVE_PATH/$APK_NAME"
    mkdir -p "$SAVE_PATH"

    # Use jadx to decompile the APK
    jadx "$APK_FILE" -d "$SAVE_PATH"
    echo "Decompiled $APK_FILE to $SAVE_PATH"
done < <(find "$APK_DIR" -type f -name "*.apk")

# Check if no APKs were found
if ! $APK_FOUND; then
    echo "No APK files found in the specified directory or its subdirectories!"
    exit 1
fi

echo "Decompilation complete!"
