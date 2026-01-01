#!/usr/bin/env python3
"""
Test script to verify that keys can be saved to a writable directory
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import main


def test_keys_directory():
    """Test that the keys directory is writable"""
    print("Testing keys directory setup...")

    # Get the keys directory
    keys_dir = main.get_keys_directory()
    print(f"✓ Keys directory: {keys_dir}")

    # Verify it exists
    assert keys_dir.exists(), f"Keys directory doesn't exist: {keys_dir}"
    print(f"✓ Directory exists")

    # Test writing a file
    test_file = keys_dir / "test_write.txt"
    try:
        with open(test_file, "w") as f:
            f.write("Test write successful")
        print(f"✓ Can write to directory")

        # Clean up test file
        test_file.unlink()
        print(f"✓ Test file cleaned up")
    except Exception as e:
        print(f"✗ Failed to write to directory: {e}")
        return False

    print("\n✅ All tests passed! Keys will be saved to:")
    print(f"   {keys_dir}")
    print("\nYour generated/imported RSA keys will be stored here,")
    print("which is writable even when running as an executable.")
    return True


if __name__ == "__main__":
    success = test_keys_directory()
    sys.exit(0 if success else 1)
