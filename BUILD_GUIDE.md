# Building TinyEncryptor Executables

This guide provides detailed instructions for building standalone executables of TinyEncryptor for distribution.

## Quick Start

### macOS
```bash
# Install PyInstaller
make install-pyinstaller

# Build application
make build-app
 
# Test
open dist/TinyEncryptor.app
```

### Windows
```powershell
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --name="TinyEncryptor" --windowed --onefile src/user_interface.py

# Test
dist\TinyEncryptor.exe
```

## Detailed Build Options

### Using Makefile (macOS/Linux)

**Directory Build (Faster startup)**:
```bash
make build
```
Output: `dist/TinyEncryptor/TinyEncryptor`

**macOS .app Bundle**:
```bash
make build-app
```
Output: `dist/TinyEncryptor.app`

**Single File (Easier distribution)**:
```bash
make build-onefile
```
Output: `dist/TinyEncryptor`

### Using Spec File (Advanced)

For more control over the build process, use the included spec file:

```bash
pyinstaller TinyEncryptor.spec
```

The spec file allows you to:
- Exclude unnecessary packages (reduces size)
- Add hidden imports
- Configure macOS bundle settings
- Customize build behavior

### Manual PyInstaller Commands

**Basic Command**:
```bash
pyinstaller --name="TinyEncryptor" \
    --windowed \
    --onefile \
    src/user_interface.py
```

**With Options**:
```bash
pyinstaller --name="TinyEncryptor" \
    --windowed \
    --onedir \
    --add-data="src:src" \
    --hidden-import="PIL._tkinter_finder" \
    --exclude-module="matplotlib" \
    --exclude-module="pandas" \
    src/user_interface.py
```

## Platform-Specific Instructions

### macOS

#### Requirements
- macOS 10.13+ (High Sierra or later)
- Python 3.13+
- Xcode Command Line Tools (run: `xcode-select --install`)

#### Building
1. Install dependencies:
   ```bash
   make install
   make install-pyinstaller
   ```

2. Build:
   ```bash
   make build-app
   ```

3. Test:
   ```bash
   open dist/TinyEncryptor.app
   ```

#### Code Signing (Optional, for distribution)
```bash
# Sign the app
codesign --deep --force --verify --verbose \
    --sign "Developer ID Application: Your Name" \
    dist/TinyEncryptor.app

# Verify signature
codesign --verify --deep --verbose=4 dist/TinyEncryptor.app
```

#### Creating DMG (Optional)
```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
    --volname "TinyEncryptor" \
    --window-pos 200 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --icon "TinyEncryptor.app" 200 190 \
    --hide-extension "TinyEncryptor.app" \
    --app-drop-link 600 185 \
    "TinyEncryptor-Installer.dmg" \
    "dist/TinyEncryptor.app"
```

### Windows

#### Requirements
- Windows 10+ (64-bit)
- Python 3.13+ (64-bit)
- Microsoft Visual C++ Redistributable

#### Building
1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. Build single executable:
   ```powershell
   pyinstaller --name="TinyEncryptor" `
       --windowed `
       --onefile `
       --add-data="src;src" `
       --hidden-import="PIL._tkinter_finder" `
       src/user_interface.py
   ```

3. Test:
   ```powershell
   dist\TinyEncryptor.exe
   ```

#### Creating Installer (Optional)

**Using Inno Setup**:
1. Download Inno Setup: https://jrsoftware.org/isdl.php
2. Create installer script (see `installer_script.iss` example below)
3. Compile with Inno Setup

**Using NSIS**:
1. Download NSIS: https://nsis.sourceforge.io/
2. Create NSIS script
3. Compile installer

### Linux

#### Building
```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build
pyinstaller --name="TinyEncryptor" \
    --windowed \
    --onefile \
    --add-data="src:src" \
    src/user_interface.py

# Test
./dist/TinyEncryptor
```

#### Creating AppImage (Optional)
Use `appimage-builder` or `linuxdeploy` to create an AppImage for easy distribution.

## Optimization Tips

### Reducing Executable Size

1. **Exclude unnecessary modules**:
   Edit `TinyEncryptor.spec` and add to `excludes`:
   ```python
   excludes=[
       'matplotlib',
       'numpy',
       'pandas',
       'scipy',
       'PyQt5',
       'PyQt6',
   ]
   ```

2. **Use UPX compression** (already enabled in spec file):
   ```bash
   # Install UPX
   # macOS:
   brew install upx
   # Windows: Download from https://upx.github.io/
   ```

3. **Use --onedir instead of --onefile**:
   - Faster startup time
   - Can exclude duplicates
   - Easier to debug

### Improving Startup Time

1. Use `--onedir` instead of `--onefile`
2. Remove debug options
3. Use lazy imports in your code
4. Consider using `--strip` on Linux/macOS

## Testing Builds

### Pre-Release Checklist

- [ ] Application launches without errors
- [ ] All menu options work correctly
- [ ] File encryption/decryption works
- [ ] Theme switching works
- [ ] Settings persist across restarts
- [ ] Can generate RSA keys
- [ ] Can import RSA keys
- [ ] Verify on fresh system (no Python installed)
- [ ] Check executable size (should be reasonable)
- [ ] Test with different file types

### Testing on Clean System

**macOS**:
- Test on a Mac without Python installed
- Test on different macOS versions (if possible)
- Verify codesigning (if signed)

**Windows**:
- Test on Windows 10 and 11
- Test on system without Python
- Check for antivirus false positives

## Troubleshooting

### Common Issues

**"Failed to execute script" error**:
- Run from terminal to see full error message
- Check for missing dependencies
- Verify all data files are included

**"Module not found" error**:
- Add missing module to `hiddenimports` in spec file
- Or add `--hidden-import=module_name` to build command

**Antivirus blocks executable**:
- This is common with PyInstaller builds
- Code sign your application (macOS/Windows)
- Submit to antivirus vendors for whitelisting

**Large executable size**:
- Use spec file to exclude unnecessary modules
- Use UPX compression
- Consider --onedir format

**Application won't start on other machines**:
- Ensure target machines meet minimum OS requirements
- Include Visual C++ Redistributable (Windows)
- Check for architecture mismatch (32-bit vs 64-bit)

### Debug Mode

Build with console window to see errors:
```bash
# Remove --windowed flag
pyinstaller --name="TinyEncryptor" \
    --onefile \
    src/user_interface.py
```

### Getting Help

- Check PyInstaller documentation: https://pyinstaller.org/
- Search PyInstaller issues: https://github.com/pyinstaller/pyinstaller/issues
- Test with `--debug all` flag for detailed logging

## Distribution

### Before Distribution

1. **Test thoroughly** on target platforms
2. **Create installer** (optional but recommended)
3. **Sign your application** (macOS/Windows)
4. **Create README** or quick start guide
5. **Prepare license** (already have MIT License)
6. **Create release notes**

### Distribution Platforms

- **GitHub Releases**: Attach executables to releases
- **Website**: Host downloads on your website
- **Mac App Store**: Requires Apple Developer account
- **Microsoft Store**: Requires Microsoft Developer account

### File Naming Convention

```
TinyEncryptor-v0.1.0-macos-intel.app
TinyEncryptor-v0.1.0-macos-arm64.app
TinyEncryptor-v0.1.0-windows-x64.exe
TinyEncryptor-v0.1.0-linux-x86_64
```

## Automation

### GitHub Actions (CI/CD)

Create `.github/workflows/build.yml` to automatically build on commits:

```yaml
name: Build Executables

on: [push, pull_request]

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: pyinstaller TinyEncryptor.spec
      - uses: actions/upload-artifact@v3
        with:
          name: TinyEncryptor-macOS
          path: dist/TinyEncryptor.app

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: pip install pyinstaller
      - run: pyinstaller --onefile --windowed src/user_interface.py
      - uses: actions/upload-artifact@v3
        with:
          name: TinyEncryptor-Windows
          path: dist/TinyEncryptor.exe
```

## Clean Build

To start fresh:
```bash
make clean-build
rm -rf __pycache__ src/__pycache__
make build
```

## Additional Resources

- PyInstaller Manual: https://pyinstaller.org/en/stable/
- CustomTkinter Packaging: https://customtkinter.tomschimansky.com/documentation/packaging
- macOS Code Signing: https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution
- Windows Code Signing: https://docs.microsoft.com/en-us/windows/win32/seccrypto/signtool
