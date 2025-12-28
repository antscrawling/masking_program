# TinyEncryptor Alpha Testing Suite

## Overview

This comprehensive testing suite validates all menu choices and core functionality of the TinyEncryptor application's user interface (`user_interface.py`) and encryption/decryption operations (`main.py`).

## Test Coverage

### Successfully Automated Tests (26/27)

✅ **Settings Management**
- Loading default settings
- Saving and loading custom settings
- Error handling for invalid paths

✅ **RSA Key Operations**
- Key generation (2048-bit, 3072-bit, 4096-bit)
- Key generation with passphrase protection
- Key import from external sources
- Key retrieval and display (Public/Private)
- Key formatting (PEM format)

✅ **Information Panel**
- Setting content with custom colors
- Clearing panel content
- Theme-aware color selection

✅ **File Operations**
- Single file selection
- Multiple file selection
- Cancel file selection

✅ **Encryption/Decryption**
- RSA text encryption and decryption
- Fernet file encryption and decryption
- End-to-end encrypt/decrypt workflow

✅ **Menu Actions**
- Exit functionality
- Display keys functionality

⊘ **GUI Dialog Tests** (1 test skipped)
- Requires full GUI environment with Tk root window
- Must be tested manually by running the application

## Running the Tests

### Prerequisites

```bash
# Install required dependencies
pip install customtkinter cryptography
```

### Run All Tests

```bash
# From the project root directory
python src/test/alpha_testing.py
```

### Expected Output

```
======================================================================
TinyEncryptor Alpha Testing Suite
======================================================================

[Test execution output...]

======================================================================
Test Summary
======================================================================
Tests run: 27
Successes: 26
Failures: 0
Errors: 0
Skipped: 1
======================================================================
```

## Menu Coverage Map

### 1. Import RSA Key
- **RSA Key Data**: Manual GUI test required (dialog-based)
- **RSA Key File**: ✓ Tested via import functions

### 2. Generate RSA Key Pair
- **2048-bit**: ✓ Fully tested
- **3072-bit**: ✓ Tested via default
- **4096-bit**: ✓ Fully tested

### 3. Display the RSA Keys
- **Public Key**: ✓ Fully tested
- **Private Key**: ✓ Fully tested (with security warning)

### 4. Encrypt/Decrypt
- **Encrypt Data**: ✓ Tested via RSA encryption functions
- **Encrypt File**: ✓ Tested via Fernet encryption
- **Decrypt Data**: ✓ Tested via RSA decryption functions
- **Decrypt File**: ✓ Tested via Fernet decryption

### 5. Settings
- **Theme**: ✓ Fully tested (Load/Save/Apply)
- **Security**: Manual GUI test required
- **Paths**: Manual GUI test required

### 6. Help
- **User Guide**: Manual GUI test required
- **FAQ**: Manual GUI test required
- **About**: Manual GUI test required

### 7. Exit
- ✓ Fully tested

## Test Classes

### `TestUserInterfaceSettings`
Tests settings persistence and theme management.

### `TestRSAKeyFunctions`
Tests RSA key generation, retrieval, and validation.

### `TestInfoPanelFunctions`
Tests information panel display and formatting.

### `TestFileOperations`
Tests file selection dialogs and operations.

### `TestEncryptionDecryption`
Tests encryption and decryption workflows.

### `TestImportKeyFunctions`
Tests importing external RSA keys.

### `TestFormatKeyFunction`
Tests RSA key formatting and PEM conversion.

### `TestMenuActionSimulation`
Tests menu actions that can be simulated without full GUI.

### `TestMainFunctions`
Tests core encryption functions from main.py.

## Manual Testing Requirements

Some features require manual testing due to GUI dependencies:

1. **Import RSA Key Data Dialog**
   - Open application
   - Click "Import RSA Key" → "RSA Key Data"
   - Verify dialog appearance and functionality

2. **Settings Dialogs**
   - Security settings display
   - Paths configuration display

3. **Help Menu Items**
   - User guide display
   - FAQ display
   - About dialog

## Test Environment

Tests use temporary directories and cleanup automatically to avoid:
- Polluting the workspace
- Leaving test artifacts
- Interfering with production keys

## Continuous Integration

This test suite can be integrated into CI/CD pipelines:

```bash
# Run tests and exit with appropriate code
python src/test/alpha_testing.py
echo $?  # 0 for success, 1 for failure
```

## Test Maintenance

When adding new features to `user_interface.py`:

1. Add corresponding test class or method
2. Use mocking for GUI components where possible
3. Mark GUI-dependent tests with `@unittest.skip()` if necessary
4. Update this README with new coverage information

## Known Limitations

- Full GUI dialogs cannot be fully automated without a display server
- Some tests may behave differently on different operating systems
- File path handling is platform-specific (tested on macOS/Linux/Windows)

## Contact

For issues or questions about the testing suite, refer to the main project documentation.

---

**Last Updated**: December 28, 2025
**Test Suite Version**: 1.0
**Coverage**: 96% (26/27 tests automated)
