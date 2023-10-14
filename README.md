# Android-Scripts

## Usage:

### Firebase Database Checker:

The following checks for read and write permissions:

For a single Decompiled app:

```
python3 firebase-database-checker.py -d /Users/bgaurang/Android-pentest/Research-apps/Hackerone/Public-Decompiled -r -w
```

For Multiple Decompiled Apps:

```
python3 firebase-database-checker.py -D /Users/bgaurang/Android-pentest/Research-apps/Hackerone/Public-Decompiled -r -w
```

### Deepsecrets

```
deepsecrets --target-dir <source-path> --outfile deepsecrets.json
```
