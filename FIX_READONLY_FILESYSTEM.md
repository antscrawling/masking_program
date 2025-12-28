# Fix for "Read-only file system" Error

## Problem
When running TinyEncryptor as an executable (packaged with PyInstaller), the app failed with:
```
Failed to save keys to files: [Errno 30] Read-only file system: 'private_key.pem'
```

This occurred because the executable was trying to save key files to the current working directory, which is read-only when running as a packaged application.

## Solution
Updated the application to save RSA keys to a user-writable directory instead of the current working directory.

### Changes Made

1. **Created `get_keys_directory()` function** (in both `main.py` and `user_interface.py`):
   - Returns `~/Documents/TinyEncryptor_Keys/` as the keys storage location
   - Automatically creates the directory if it doesn't exist
   - Falls back to `~/.tinyencryptor_keys` if Documents is inaccessible
   - This directory is always writable, even when running as an executable

2. **Updated all key file operations** to use the writable directory:
   - `generate_rsa_key_pair()` - saves generated keys to the keys directory
   - `retrieve_rsa_keys()` - reads keys from the keys directory
   - `import_external_rsa_keys()` - saves imported keys to the keys directory
   - `import_keys_from_file()` - saves keys to the keys directory
   - `encrypt_with_rsa_public_key()` - reads public key from keys directory
   - `decrypt_with_rsa_private_key()` - reads private key from keys directory

3. **Updated UI displays**:
   - Security settings now show the correct keys location
   - Path settings display updated to show the keys directory
   - Added "Open Keys Directory" button in the Paths dialog
   - Key generation success messages now show where keys were saved

## Key Storage Location

**macOS/Linux**: `~/Documents/TinyEncryptor_Keys/`  
**Windows**: `%USERPROFILE%\Documents\TinyEncryptor_Keys\`

This location:
- ✅ Is always writable by the user
- ✅ Works in both script mode and as a packaged executable
- ✅ Is easy for users to find and backup
- ✅ Persists across application updates
- ✅ Follows platform conventions for user data

## Files Modified
- `src/main.py` - Added `get_keys_directory()` and updated all key file operations
- `src/user_interface.py` - Added `get_keys_directory()` and updated UI displays

## Testing
Run `test_keys_directory.py` to verify the keys directory is writable:
```bash
python test_keys_directory.py
```

## Next Steps
After rebuilding your executable with these changes:
1. The app will automatically create the keys directory on first use
2. All generated or imported keys will be saved to `~/Documents/TinyEncryptor_Keys/`
3. Users can easily find and backup their keys from this location
4. The "Open Keys Directory" button in Settings → Paths provides quick access

## Migration Note
If you had keys in the old location (application directory), you can:
1. Copy them to the new location: `~/Documents/TinyEncryptor_Keys/`
2. Or re-import/regenerate your keys using the application
