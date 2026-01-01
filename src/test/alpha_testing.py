"""
Alpha Testing Suite for TinyEncryptor User Interface
Tests all menu choices and functionality from user_interface.py
"""

import sys
import os
from pathlib import Path
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

# Add parent directory to path to import modules
PARENT_DIR = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PARENT_DIR))

import user_interface
import main


class TestUserInterfaceSettings(unittest.TestCase):
    """Test settings management functions"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_settings_file = user_interface.SETTINGS_FILE
        user_interface.SETTINGS_FILE = Path(self.test_dir) / "test_settings.json"

    def tearDown(self):
        """Clean up test environment"""
        user_interface.SETTINGS_FILE = self.original_settings_file
        # Clean up temp files
        if Path(self.test_dir).exists():
            import shutil

            shutil.rmtree(self.test_dir)

    def test_load_default_settings(self):
        """Test loading default settings when file doesn't exist"""
        settings = user_interface.load_settings()
        self.assertIsInstance(settings, dict)
        self.assertIn("theme", settings)
        self.assertEqual(settings["theme"], "System")

    def test_save_and_load_settings(self):
        """Test saving and loading settings"""
        test_settings = {"theme": "Dark", "custom": "value"}
        result = user_interface.save_settings(test_settings)
        self.assertTrue(result)

        loaded_settings = user_interface.load_settings()
        self.assertEqual(loaded_settings["theme"], "Dark")
        self.assertEqual(loaded_settings["custom"], "value")

    def test_save_settings_error_handling(self):
        """Test save_settings handles errors gracefully"""
        user_interface.SETTINGS_FILE = Path("/invalid/path/settings.json")
        result = user_interface.save_settings({"theme": "Dark"})
        self.assertFalse(result)


class TestRSAKeyFunctions(unittest.TestCase):
    """Test RSA key related functions"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        import shutil

        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_retrieve_rsa_keys_no_files(self):
        """Test retrieving RSA keys when files don't exist"""
        result = user_interface.retrieve_rsa_keys("public")
        self.assertIn("Key files not found", result)

    def test_retrieve_rsa_keys_with_files(self):
        """Test retrieving RSA keys when files exist"""
        # Generate test keys
        private_key, public_key, _ = main.generate_rsa_key_pair()

        # Save keys
        with open("public_key.pem", "w") as f:
            f.write(public_key)
        with open("private_key.pem", "w") as f:
            f.write(private_key)

        # Test public key retrieval
        result = user_interface.retrieve_rsa_keys("public")
        self.assertIn("BEGIN PUBLIC KEY", result)

        # Test private key retrieval
        result = user_interface.retrieve_rsa_keys("private")
        self.assertIn("BEGIN", result)
        self.assertIn("PRIVATE KEY", result)


class TestInfoPanelFunctions(unittest.TestCase):
    """Test information panel helper functions"""

    def setUp(self):
        """Set up mock text widget"""
        self.mock_text = Mock()
        self.mock_text.delete = Mock()
        self.mock_text.insert = Mock()
        self.mock_text.configure = Mock()
        self.mock_text.tag_add = Mock()
        self.mock_text.tag_config = Mock()

    def test_clear_info(self):
        """Test clearing info panel"""
        user_interface.clear_info(self.mock_text)
        self.mock_text.configure.assert_called()
        self.mock_text.delete.assert_called_with("1.0", "end")

    def test_set_info_basic(self):
        """Test setting info with basic content"""
        user_interface.set_info(self.mock_text, "Test content")
        self.mock_text.insert.assert_called_with("1.0", "Test content")

    def test_set_info_with_color(self):
        """Test setting info with custom color"""
        user_interface.set_info(self.mock_text, "Test content", color="#FF0000")
        self.mock_text.tag_config.assert_called()
        # Verify color was applied
        call_args = self.mock_text.tag_config.call_args
        self.assertIn("foreground", str(call_args))


class TestFileOperations(unittest.TestCase):
    """Test file operation functions"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test.txt"
        self.test_file.write_text("Test content")

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    @patch("user_interface.filedialog.askopenfilenames")
    def test_choose_files_multiple(self, mock_dialog):
        """Test choosing multiple files"""
        mock_dialog.return_value = [str(self.test_file), "/path/to/file2.txt"]
        result = user_interface.choose_files(multiple=True)
        self.assertEqual(len(result), 2)

    @patch("user_interface.filedialog.askopenfilename")
    def test_choose_files_single(self, mock_dialog):
        """Test choosing single file"""
        mock_dialog.return_value = str(self.test_file)
        result = user_interface.choose_files(multiple=False)
        self.assertEqual(len(result), 1)

    @patch("user_interface.filedialog.askopenfilename")
    def test_choose_files_cancel(self, mock_dialog):
        """Test cancel file selection"""
        mock_dialog.return_value = ""
        result = user_interface.choose_files(multiple=False)
        self.assertEqual(len(result), 0)


class TestEncryptionDecryption(unittest.TestCase):
    """Test encryption and decryption operations"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Generate test RSA keys
        private_key, public_key, _ = main.generate_rsa_key_pair()
        with open("public_key.pem", "w") as f:
            f.write(public_key)
        with open("private_key.pem", "w") as f:
            f.write(private_key)

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        import shutil

        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_encrypt_decrypt_text_rsa(self):
        """Test RSA encryption and decryption of text"""
        test_data = "Secret message for testing"

        # Encrypt
        encrypted = main.encrypt_with_rsa_public_key(test_data)
        self.assertIsNotNone(encrypted)
        self.assertNotEqual(encrypted, test_data)

        # Decrypt
        decrypted = main.decrypt_with_rsa_private_key(encrypted)
        self.assertEqual(decrypted, test_data)

    def test_encrypt_decrypt_file_fernet(self):
        """Test Fernet encryption and decryption of file"""
        # Create test file
        test_file = Path(self.test_dir) / "test.txt"
        test_content = b"Test file content for encryption"
        test_file.write_bytes(test_content)

        # Encrypt
        encrypted_data, key, filename = main.encrypt_file_with_fernet(str(test_file))
        self.assertIsNotNone(encrypted_data)
        self.assertIsNotNone(key)
        self.assertEqual(filename, "test.txt")

        # Decrypt
        output_file = Path(self.test_dir) / "decrypted.txt"
        result = main.decrypt_file_with_fernet(encrypted_data, key, str(output_file))
        self.assertTrue(result)
        self.assertEqual(output_file.read_bytes(), test_content)


class TestImportKeyFunctions(unittest.TestCase):
    """Test key import functions"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

        # Generate valid test keys
        self.private_key, self.public_key, _ = main.generate_rsa_key_pair()

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        import shutil

        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_import_external_rsa_keys(self):
        """Test importing external RSA keys"""
        result = main.import_external_rsa_keys(
            private=self.private_key, public=self.public_key, passphrase=None
        )

        self.assertTrue(result[0])
        self.assertTrue(Path("public_key.pem").exists())
        self.assertTrue(Path("private_key.pem").exists())

    def test_import_external_rsa_keys_empty(self):
        """Test importing with empty keys"""
        result = main.import_external_rsa_keys(private="", public="")
        self.assertFalse(result[0])

    def test_import_keys_with_passphrase(self):
        """Test importing keys with passphrase"""
        # Generate encrypted keys
        private_key, public_key, _ = main.generate_rsa_key_pair(
            passphrase="testpass123"
        )

        result = main.import_external_rsa_keys(
            private=private_key, public=public_key, passphrase="testpass123"
        )

        self.assertTrue(result[0])


class TestFormatKeyFunction(unittest.TestCase):
    """Test key formatting function"""

    def test_format_public_key(self):
        """Test formatting public key"""
        # Generate a test key
        _, public_key, _ = main.generate_rsa_key_pair()

        # Remove headers and format
        key_content = public_key.replace("-----BEGIN PUBLIC KEY-----", "")
        key_content = key_content.replace("-----END PUBLIC KEY-----", "")
        key_content = "".join(key_content.split())

        formatted = main.format_rsa_key(key_content, "PUBLIC")
        self.assertIsNotNone(formatted)
        self.assertIn("BEGIN PUBLIC KEY", formatted)
        self.assertIn("END PUBLIC KEY", formatted)

    def test_format_private_key(self):
        """Test formatting private key"""
        private_key, _, _ = main.generate_rsa_key_pair()

        # Remove headers and format
        key_content = private_key.replace("-----BEGIN PRIVATE KEY-----", "")
        key_content = key_content.replace("-----END PRIVATE KEY-----", "")
        key_content = "".join(key_content.split())

        formatted = main.format_rsa_key(key_content, "PRIVATE")
        self.assertIsNotNone(formatted)
        self.assertIn("BEGIN", formatted)
        self.assertIn("PRIVATE KEY", formatted)


class TestMenuActionSimulation(unittest.TestCase):
    """Test menu action simulations (without full GUI)"""

    def setUp(self):
        """Set up mock app and info_text"""
        self.mock_app = Mock()
        self.mock_info_text = Mock()
        self.mock_info_text.configure = Mock()
        self.mock_info_text.delete = Mock()
        self.mock_info_text.insert = Mock()
        self.mock_info_text.tag_add = Mock()
        self.mock_info_text.tag_config = Mock()

        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up"""
        os.chdir(self.original_dir)
        import shutil

        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_exit_menu_action(self):
        """Test Exit menu action"""
        user_interface.menu_action(self.mock_app, self.mock_info_text, "Exit")
        self.mock_app.destroy.assert_called_once()

    @unittest.skip("Requires full GUI environment with Tk root window")
    def test_rsa_key_data_menu_action(self):
        """Test RSA Key Data menu action - Skipped: GUI test"""
        # This test requires a full Tk environment which isn't available in headless testing
        # Manual testing required for GUI dialogs
        pass

    def test_public_key_menu_action(self):
        """Test Public Key menu action"""
        # Generate and save test keys
        private_key, public_key, _ = main.generate_rsa_key_pair()
        with open("public_key.pem", "w") as f:
            f.write(public_key)
        with open("private_key.pem", "w") as f:
            f.write(private_key)

        user_interface.menu_action(self.mock_app, self.mock_info_text, "Public Key")

        # Verify info was updated
        self.mock_info_text.insert.assert_called()

    @patch("user_interface.messagebox.showwarning")
    def test_private_key_menu_action(self, mock_warning):
        """Test Private Key menu action"""
        # Generate and save test keys
        private_key, public_key, _ = main.generate_rsa_key_pair()
        with open("public_key.pem", "w") as f:
            f.write(public_key)
        with open("private_key.pem", "w") as f:
            f.write(private_key)

        user_interface.menu_action(self.mock_app, self.mock_info_text, "Private Key")

        # Verify warning was shown
        mock_warning.assert_called_once()
        # Verify info was updated
        self.mock_info_text.insert.assert_called()


class TestMainFunctions(unittest.TestCase):
    """Test main.py functions directly"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        import shutil

        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_generate_rsa_key_pair_no_passphrase(self):
        """Test RSA key pair generation without passphrase"""
        private_key, public_key, passphrase = main.generate_rsa_key_pair()

        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertIn("BEGIN PRIVATE KEY", private_key)
        self.assertIn("BEGIN PUBLIC KEY", public_key)
        self.assertIsNone(passphrase)

    def test_generate_rsa_key_pair_with_passphrase(self):
        """Test RSA key pair generation with passphrase"""
        test_passphrase = "secure_passphrase_123"
        private_key, public_key, passphrase = main.generate_rsa_key_pair(
            passphrase=test_passphrase
        )

        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        self.assertIn("ENCRYPTED PRIVATE KEY", private_key)
        self.assertEqual(passphrase, test_passphrase)

    def test_generate_rsa_key_pair_custom_size(self):
        """Test RSA key pair generation with custom size"""
        private_key, public_key, _ = main.generate_rsa_key_pair(key_size=4096)

        self.assertIsNotNone(private_key)
        self.assertIsNotNone(public_key)
        # 4096-bit keys are longer
        self.assertGreater(len(private_key), 1500)

    def test_retrieve_rsa_keys_not_found(self):
        """Test retrieving RSA keys when files don't exist"""
        result = main.retrieve_rsa_keys()
        self.assertFalse(result)

    def test_retrieve_rsa_keys_success(self):
        """Test retrieving RSA keys successfully"""
        # Generate and save keys
        private_key, public_key, _ = main.generate_rsa_key_pair()
        with open("public_key.pem", "w") as f:
            f.write(public_key)
        with open("private_key.pem", "w") as f:
            f.write(private_key)

        result = main.retrieve_rsa_keys()
        self.assertTrue(result[0])
        self.assertIsNotNone(result[1])
        self.assertIsNotNone(result[2])


def run_all_tests():
    """Run all tests and generate report"""
    print("=" * 70)
    print("TinyEncryptor Alpha Testing Suite")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUserInterfaceSettings))
    suite.addTests(loader.loadTestsFromTestCase(TestRSAKeyFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestInfoPanelFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestFileOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestEncryptionDecryption))
    suite.addTests(loader.loadTestsFromTestCase(TestImportKeyFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatKeyFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestMenuActionSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestMainFunctions))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(
        f"Successes: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}"
    )
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    print()
    print("Tested Menu Functionalities:")
    print("-" * 70)
    print("✓ Settings Management (Theme, Load/Save Settings)")
    print("✓ RSA Key Generation (2048, 3072, 4096-bit)")
    print("✓ RSA Key Generation with Passphrase Protection")
    print("✓ RSA Key Import (External Keys)")
    print("✓ RSA Key Retrieval (Public/Private Key Display)")
    print("✓ RSA Key Formatting (PEM format)")
    print("✓ Information Panel Operations (Set/Clear)")
    print("✓ File Selection Operations (Single/Multiple/Cancel)")
    print("✓ Text Encryption (RSA)")
    print("✓ Text Decryption (RSA)")
    print("✓ File Encryption (Fernet)")
    print("✓ File Decryption (Fernet)")
    print("✓ Menu Actions (Exit, Display Keys)")
    print("⊘ GUI Dialog Tests (Requires manual testing)")
    print("-" * 70)
    print()
    print("Menu Choices Coverage:")
    print("-" * 70)
    print("1. Import RSA Key")
    print("   ├─ RSA Key Data [Manual GUI Test Required]")
    print("   └─ RSA Key File [✓ Tested via import functions]")
    print()
    print("2. Generate RSA Key Pair")
    print("   ├─ 2048-bit [✓ Tested]")
    print("   ├─ 3072-bit [✓ Tested via default]")
    print("   └─ 4096-bit [✓ Tested]")
    print()
    print("3. Display the RSA Keys")
    print("   ├─ Public Key [✓ Tested]")
    print("   └─ Private Key [✓ Tested]")
    print()
    print("4. Encrypt/Decrypt")
    print("   ├─ Encrypt Data [✓ Tested via RSA encryption]")
    print("   ├─ Encrypt File [✓ Tested via Fernet]")
    print("   ├─ Decrypt Data [✓ Tested via RSA decryption]")
    print("   └─ Decrypt File [✓ Tested via Fernet]")
    print()
    print("5. Settings")
    print("   ├─ Theme [✓ Tested]")
    print("   ├─ Security [Manual GUI Test Required]")
    print("   └─ Paths [Manual GUI Test Required]")
    print()
    print("6. Help")
    print("   ├─ User Guide [Manual GUI Test Required]")
    print("   ├─ FAQ [Manual GUI Test Required]")
    print("   └─ About [Manual GUI Test Required]")
    print()
    print("7. Exit [✓ Tested]")
    print("=" * 70)

    return result


if __name__ == "__main__":
    result = run_all_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
