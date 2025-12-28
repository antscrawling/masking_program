# TinyEncryptor

A comprehensive encryption application with a modern GUI interface for managing RSA and Fernet encryption. TinyEncryptor provides secure encryption and decryption capabilities for both text data and files, with user-friendly key management.

## Features

### Core Functionality
- **RSA Encryption**: Asymmetric encryption for secure key exchange
  - Support for 2048-bit, 3072-bit, and 4096-bit key pairs
  - Optional passphrase protection for private keys
  - Import/Export RSA keys in PEM format
  
- **Fernet Encryption**: Symmetric encryption for fast file encryption
  - Secure key generation
  - Support for multiple file encryption
  
- **Data Encryption**: Encrypt and decrypt text data directly
- **File Encryption**: Encrypt and decrypt files with automatic naming
  - Encrypted files: `filename<encrypted>.ext`
  - Decrypted files: `filename.ext` (restored original name)

### User Interface Features
- **Modern GUI**: Built with CustomTkinter for a sleek, modern look
- **Theme Support**: Light, Dark, and System theme options
  - Theme preferences automatically saved to `settings.json`
  - Persistent theme selection across application restarts
  
- **Settings Management**:
  - **Theme**: Configure application appearance
  - **Security**: View security best practices and guidelines
  - **Paths**: View application directory paths and open root directory
  
- **Information Panel**: Real-time feedback and detailed operation results
- **Key Management**: Generate, import, display, and manage encryption keys

## Installation

### Prerequisites
- macOS (with Homebrew)
- Python 3.13 or higher
- pyenv (optional, recommended)
- uv (optional, for faster dependency management)

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd masking_program
   ```

2. **Install dependencies using Makefile**:
   ```bash
   # Install pyenv (if not already installed)
   make brew
   
   # Install Python 3.13.4 via pyenv
   make pyenv
   
   # Create virtual environment
   make venv
   
   # Install dependencies
   make install
   # OR use uv for faster installation
   make sync
   ```

3. **Run the application**:
   ```bash
   make run
   ```

## Makefile Commands

### Setup Commands
| Command | Description |
|---------|-------------|
| `make help` | Display all available commands |
| `make brew` | Install Homebrew prerequisites (pyenv) |
| `make pyenv` | Install Python 3.13.4 via pyenv |
| `make venv` | Create virtual environment with Python 3.13.4 |
| `make install` | Install dependencies from requirements.txt |
| `make sync` | Sync dependencies using uv (faster alternative) |
| `make upgrade` | Upgrade all dependencies to latest versions |

### Application Commands
| Command | Description |
|---------|-------------|
| `make run` | Run the GUI application (user_interface.py) |
| `make main` | Run the main.py module directly |

### Development Commands
| Command | Description |
|---------|-------------|
| `make format` | Format code with ruff |
| `make lint` | Lint code with ruff |
| `make check` | Run both format and lint checks |

### Testing Commands
| Command | Description |
|---------|-------------|
| `make test` | Run tests (if available) |

### Build Commands
| Command | Description |
|---------|-------------|
| `make install-pyinstaller` | Install PyInstaller for building executables |
| `make build` | Build executable for current platform (directory format) |
| `make build-app` | Build macOS .app bundle |
| `make build-onefile` | Build single-file executable |
| `make clean-build` | Remove build artifacts and dist folders |

### Maintenance Commands
| Command | Description |
|---------|-------------|
| `make freeze` | Regenerate requirements.txt from current venv |
| `make clean` | Remove virtual env and cache files |
| `make clean-keys` | Remove generated key files (⚠️ use with caution!) |
| `make clean-all` | Remove everything (venv, cache, keys, settings) |

## Building Executables

TinyEncryptor can be packaged as a standalone executable for distribution on macOS and Windows.

### Prerequisites for Building

Install PyInstaller:
```bash
make install-pyinstaller
```

### Building on macOS

**Option 1: Standard Build (Recommended)**
```bash
make build
```
Creates a directory-based application in `dist/TinyEncryptor/` with all dependencies included.

**Option 2: macOS .app Bundle**
```bash
make build-app
```
Creates `dist/TinyEncryptor.app` that can be dragged to Applications folder.

**Option 3: Single File**
```bash
make build-onefile
```
Creates a single executable file (slower startup, but easier to distribute).

### Building on Windows

1. Install Python 3.13+ and dependencies on Windows
2. Open Command Prompt or PowerShell in the project directory
3. Run:
   ```bash
   python -m pip install pyinstaller
   python -m PyInstaller --name="TinyEncryptor" --windowed --onefile src/user_interface.py
   ```
4. Executable will be in `dist/TinyEncryptor.exe`

### Cross-Platform Build Notes

**Important**: Executables must be built on each target platform:
- Build on macOS to create macOS executables (.app or executable)
- Build on Windows to create Windows executables (.exe)
- PyInstaller cannot cross-compile

**Build Output Locations**:
- `dist/TinyEncryptor/` - Directory-based build
- `dist/TinyEncryptor.app` - macOS application bundle
- `dist/TinyEncryptor` - Single-file executable (Unix/macOS)
- `dist/TinyEncryptor.exe` - Single-file executable (Windows)

### Distribution

After building:

**macOS**:
1. Test the application: `open dist/TinyEncryptor.app`
2. Create a DMG file for distribution (optional):
   ```bash
   # Install create-dmg if needed
   brew install create-dmg
   
   # Create DMG
   create-dmg 'dist/TinyEncryptor.app' dist/
   ```

**Windows**:
1. Test the executable: `dist\TinyEncryptor.exe`
2. Consider creating an installer with NSIS or Inno Setup
3. Or zip the `dist/TinyEncryptor/` folder for distribution

### Troubleshooting Builds

**Missing modules error**:
Add hidden imports to the build command:
```bash
python -m PyInstaller --hidden-import=module_name ...
```

**Application won't start**:
- Run from terminal to see error messages
- Check that all data files are included with `--add-data`

**Large executable size**:
- Use `--onedir` instead of `--onefile` for faster startup
- Consider excluding unnecessary packages

**Clean build artifacts**:
```bash
make clean-build
```

## Usage

### Starting the Application

```bash
make run
```

The application will launch with a GUI interface showing the main menu.

### Basic Workflow

1. **Generate or Import RSA Keys**:
   - Click "Generate RSA Key Pair" to create new keys (choose key size: 2048, 3072, or 4096 bits)
   - OR click "Import RSA Key" to import existing keys
   - Optionally protect private key with a passphrase

2. **Encrypt Data or Files**:
   - Click "Encrypt/Decrypt" → "Encrypt Data" for text encryption
   - Click "Encrypt/Decrypt" → "Encrypt File" for file encryption
   - Save the encryption key securely

3. **Decrypt Data or Files**:
   - Click "Encrypt/Decrypt" → "Decrypt Data" for text decryption
   - Click "Encrypt/Decrypt" → "Decrypt File" for file decryption
   - Provide the correct encryption key

4. **Configure Settings**:
   - Click "Settings" to access theme, security, and path options
   - Theme changes are automatically saved

### Key Management

#### Generating Keys
- Navigate to "Generate RSA Key Pair"
- Select key size (2048, 3072, or 4096 bits)
- Optionally enter a passphrase for private key encryption
- Keys are saved as `public_key.pem` and `private_key.pem`

#### Importing Keys
- Navigate to "Import RSA Key" → "RSA Key Data"
- Paste your public and private keys (PEM format)
- If private key is encrypted, provide the passphrase
- Keys are validated and saved

#### Displaying Keys
- Navigate to "Display the RSA Keys"
- Select "Public Key" or "Private Key" to view

## Project Structure

```
masking_program/
├── src/
│   ├── main.py                    # Core encryption/decryption functions
│   ├── user_interface.py          # GUI application
│   ├── settings.json              # User settings (auto-generated)
│   ├── public_key.pem            # RSA public key (generated)
│   ├── private_key.pem           # RSA private key (generated)
│   ├── fernet_encryption_key.txt # Fernet key (generated)
│   └── __pycache__/              # Python cache
├── Makefile                       # Build and run commands
├── pyproject.toml                 # Project configuration
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Main Modules

### user_interface.py

The main GUI application built with CustomTkinter. Features include:

- **App Class**: Main application window with dropdown menus
- **Theme Management**: Load/save theme preferences
- **Menu Actions**: Handlers for all menu operations
  - RSA key import (from data or file)
  - RSA key generation (2048/3072/4096 bit)
  - RSA key display
  - Data/File encryption and decryption
  - Settings (Theme, Security, Paths)
  
- **Helper Functions**:
  - `set_info()`: Display information with theme-aware colors
  - `clear_info()`: Clear information panel
  - `choose_files()`: File selection dialog
  - `retrieve_rsa_keys()`: Load saved RSA keys
  - `import_keys()`: Import external RSA keys

### main.py

Core encryption/decryption engine. Key functions:

#### RSA Operations
- `generate_rsa_key_pair(passphrase, key_size)`: Generate RSA key pairs
- `retrieve_rsa_keys()`: Retrieve saved RSA keys from files
- `import_external_rsa_keys(private, public, passphrase)`: Import external keys
- `format_rsa_key(key_content, key_type)`: Format RSA keys with proper headers
- `encrypt_with_rsa_public_key(data, public_key_path)`: RSA encryption
- `decrypt_with_rsa_private_key(encrypted_data, private_key_path, passphrase)`: RSA decryption

#### Fernet Operations
- `encrypt_data_not_binary(data)`: Encrypt text data with Fernet
- `decrypt_data_not_binary(orig, key)`: Decrypt text data with Fernet
- `encrypt_file_with_fernet(file_path)`: Encrypt files with Fernet
- `decrypt_file_with_fernet(encrypted_data, key, output_filename)`: Decrypt files

#### File Operations
- `open_file(file_path)`: Load JSON data from file
- `write_file(file_path, data)`: Save data to JSON file
- `show_file_menu(prompt)`: Display file selection menu

## Dependencies

Key dependencies include:

- **customtkinter**: Modern UI framework
- **cryptography**: Encryption library (RSA, Fernet)
- **tkinter**: Standard Python GUI toolkit

See [requirements.txt](requirements.txt) for complete list.

## Security Best Practices

### Key Storage
- Store private keys in secure locations
- Use strong passphrases for key encryption
- Never share private keys via insecure channels
- Regularly backup keys to secure locations

### Key Management
- Rotate keys periodically for high-security applications
- Use different key pairs for different purposes
- Delete old keys securely when no longer needed
- Use 4096-bit RSA keys for maximum security

### File Security
- Encrypted files are stored with `<encrypted>` suffix
- Key files are stored locally in the application directory
- Always maintain backup copies of important data
- For production use, consider hardware security modules (HSM)

## File Naming Conventions

- **Encrypted files**: `filename<encrypted>.ext`
- **Decrypted files**: `filename.ext` (original name restored)
- **Key files**: `*_key.pem` format
- **Settings**: `settings.json`
- **Encrypted data storage**: `encrypted_data.json`

## Themes

The application supports three theme modes:

1. **Light**: Light background with dark text
2. **Dark**: Dark background with light text
3. **System**: Automatically matches system preferences

Theme selection is saved to `settings.json` and persists across sessions.

## Troubleshooting

### Common Issues

**Application won't start**:
```bash
# Ensure dependencies are installed
make install

# Or try using uv
make sync
```

**Key generation fails**:
- Ensure you have write permissions in the application directory
- Check that no existing key files are locked

**Decryption fails**:
- Verify you're using the correct encryption key
- Check that the encrypted data hasn't been corrupted
- Ensure passphrase is correct (if private key is encrypted)

**Theme not persisting**:
- Check that `settings.json` is writable
- Ensure the application has permission to write to the src directory

## Development

### Code Formatting
```bash
make format
```

### Linting
```bash
make lint
```

### Run Both Checks
```bash
make check
```

## Contributing

When contributing:
1. Format code with `make format`
2. Run linting with `make lint`
3. Test all encryption/decryption operations
4. Verify theme switching works correctly
5. Check that settings persist properly

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that allows you to:
- ✅ Use the software for commercial purposes
- ✅ Modify the software
- ✅ Distribute the software
- ✅ Use the software privately
- ✅ Sublicense the software

The only requirement is that you include the original copyright and license notice in any copy of the software.

## Author

[Jose D. Ibay Jr., email : ourcatisfat@gmail.com 28-Dec-2025]

## Version

Version 1.0.0

---

**Note**: This is an educational/personal encryption tool. For production environments requiring high-security standards, consider using established enterprise-grade encryption solutions and hardware security modules (HSM). 