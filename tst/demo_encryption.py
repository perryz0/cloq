#!/usr/bin/env python3
"""
Simple Demo Test - Encryption Visualization

This test provides a simplified demonstration of Cloq's encryption capabilities
by showing the before/after states of code encryption and decryption.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cloq_cp.crypto_utils import (
    generate_rsa_keypair, 
    save_keypair, 
    encrypt_file, 
    decrypt_file
)

def demonstrate_encryption():
    """Demonstrate encryption by showing before/after states of a simple calculation"""
    # Initialize all variables and result dictionary
    result = {
        'original': '',
        'encrypted': '',
        'decrypted': ''
    }
    test_file = None
    encrypted_file = None
    decrypted_file = None
    private_key_path = None
    public_key_path = None

    try:
        # Create a simple test calculation
        test_code = '''
def calculate():
    x = 15
    y = 27
    result = x + y
    print(f"Computing {x} + {y} = {result}")
    return result

if __name__ == "__main__":
    calculate()
'''
        # Store original code in result
        result['original'] = test_code

        # Write test code to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_code)
            test_file = f.name

        print("🔑 Generating encryption keys...")
        private_key, public_key = generate_rsa_keypair()
        temp_dir = tempfile.gettempdir()
        private_key_path = os.path.join(temp_dir, "test_demo_private.pem")
        public_key_path = os.path.join(temp_dir, "test_demo_public.pem")
        save_keypair(private_key, public_key, private_key_path, public_key_path)
        print("✅ Keys generated and saved")

        print("\n📝 Original code:")
        print("-" * 40)
        print(test_code.strip())
        print("-" * 40)

        # Encrypt the file
        print("\n🔒 Encrypting code...")
        encrypted_file = os.path.join(temp_dir, "demo.encrypted.clq")
        encrypt_file(test_file, public_key_path, encrypted_file)

        # Show a preview of encrypted content
        with open(encrypted_file, 'rb') as f:
            encrypted = f.read()
            result['encrypted'] = encrypted.hex()[:100] + "..."  # Store first 100 chars of hex
        print("\n🔐 Encrypted form (first 100 bytes in hex):")
        print("-" * 40)
        print(result['encrypted'])
        print("-" * 40)

        # Decrypt to a new file
        print("\n🔓 Decrypting code...")
        decrypted_file = os.path.join(temp_dir, "demo_decrypted.py")
        decrypt_file(encrypted_file, private_key_path, decrypted_file)

        # Show decrypted content
        with open(decrypted_file, 'r', encoding='utf-8') as f:
            decrypted = f.read()
            result['decrypted'] = decrypted
        print("\n📝 Decrypted code:")
        print("-" * 40)
        print(decrypted.strip())
        print("-" * 40)

        print("\n✅ Demonstration completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {str(e)}")
        raise  # Re-raise the exception after printing
    
    finally:
        # Cleanup
        for file in [test_file, encrypted_file, decrypted_file, 
                    private_key_path, public_key_path]:
            if file and os.path.exists(file):
                try:
                    os.remove(file)
                except Exception as e:
                    print(f"Warning: Could not remove {file}: {str(e)}")
    
    return result

if __name__ == "__main__":
    demonstrate_encryption()