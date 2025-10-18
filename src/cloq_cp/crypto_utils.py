#!/usr/bin/env python3
"""
Cloq Crypto Utils - Local encryption SDK for vendors

This module provides cryptographic primitives for the Cloq system:
- RSA keypair generation for vendors and enterprises
- Hybrid encryption (AES + RSA) for file encryption
- Standalone encryption/decryption without control plane dependency

This simulates the local Cloq encryption SDK that vendors can use to
self-encrypt their software before sending it to the control plane.
"""

import os
import json
import base64
import logging
from typing import Tuple, Dict, Any
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CryptoError(Exception):
    """Custom exception for crypto operations"""
    pass


def generate_rsa_keypair(key_size: int = 4096) -> Tuple[bytes, bytes]:
    """
    Generate RSA keypair for vendors or enterprises
    
    Args:
        key_size: RSA key size in bits (default 4096)
        
    Returns:
        Tuple of (private_key_pem, public_key_pem) as bytes
    """
    try:
        logger.info(f"Generating RSA-{key_size} keypair...")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        logger.info("✓ RSA keypair generated successfully")
        return private_pem, public_pem
        
    except Exception as e:
        logger.error(f"Failed to generate RSA keypair: {str(e)}")
        raise CryptoError(f"Failed to generate RSA keypair: {str(e)}")


def save_keypair(private_key: bytes, public_key: bytes, 
                private_path: str, public_path: str) -> None:
    """Save keypair to files"""
    try:
        logger.info(f"Saving keys to {private_path} and {public_path}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(private_path), exist_ok=True)
        os.makedirs(os.path.dirname(public_path), exist_ok=True)
        
        with open(private_path, 'wb') as f:
            f.write(private_key)
        with open(public_path, 'wb') as f:
            f.write(public_key)
            
        logger.info("✓ Keypair saved successfully")
        
    except Exception as e:
        logger.error(f"Failed to save keypair: {str(e)}")
        raise CryptoError(f"Failed to save keypair: {str(e)}")


def generate_aes_key() -> bytes:
    """Generate random 256-bit AES key"""
    logger.info("Generating random AES-256 key...")
    return os.urandom(32)  # 256 bits


def encrypt_file_aes(file_data: bytes, aes_key: bytes) -> Tuple[bytes, bytes]:
    """
    Encrypt file data using AES-256-GCM
    
    Args:
        file_data: Raw file data to encrypt
        aes_key: 256-bit AES key
        
    Returns:
        Tuple of (encrypted_data_with_tag, iv)
    """
    try:
        logger.info("Encrypting file with AES-256-GCM...")
        
        # Generate random IV
        iv = os.urandom(12)  # 96 bits for GCM mode
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt data
        encrypted_data = encryptor.update(file_data) + encryptor.finalize()
        
        # Return encrypted data with auth tag
        logger.info("✓ File encrypted with AES-256-GCM")
        return encrypted_data + encryptor.tag, iv
        
    except Exception as e:
        logger.error(f"Failed to encrypt file: {str(e)}")
        raise CryptoError(f"Failed to encrypt file: {str(e)}")


def decrypt_file_aes(encrypted_data: bytes, aes_key: bytes, iv: bytes) -> bytes:
    """
    Decrypt file data using AES-256-GCM
    
    Args:
        encrypted_data: Encrypted data with auth tag appended
        aes_key: 256-bit AES key
        iv: Initialization vector
        
    Returns:
        Decrypted file data
    """
    try:
        logger.info("Decrypting file with AES-256-GCM...")
        
        # Split encrypted data and auth tag
        auth_tag = encrypted_data[-16:]  # GCM auth tag is 16 bytes
        ciphertext = encrypted_data[:-16]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(iv, auth_tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt data
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        logger.info("✓ File decrypted with AES-256-GCM")
        return decrypted_data
        
    except Exception as e:
        logger.error(f"Failed to decrypt file: {str(e)}")
        raise CryptoError(f"Failed to decrypt file: {str(e)}")


def encrypt_aes_key_with_rsa(aes_key: bytes, public_key_pem: bytes) -> bytes:
    """
    Encrypt AES key using RSA public key
    
    Args:
        aes_key: 256-bit AES key to encrypt
        public_key_pem: RSA public key in PEM format
        
    Returns:
        Encrypted AES key
    """
    try:
        logger.info("Encrypting AES key with RSA public key...")
        
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem,
            backend=default_backend()
        )
        
        # Encrypt AES key
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        logger.info("✓ AES key encrypted with RSA")
        return encrypted_key
        
    except Exception as e:
        logger.error(f"Failed to encrypt AES key: {str(e)}")
        raise CryptoError(f"Failed to encrypt AES key: {str(e)}")


def decrypt_aes_key_with_rsa(encrypted_aes_key: bytes, private_key_pem: bytes) -> bytes:
    """
    Decrypt AES key using RSA private key
    
    Args:
        encrypted_aes_key: Encrypted AES key
        private_key_pem: RSA private key in PEM format
        
    Returns:
        Decrypted AES key
    """
    try:
        logger.info("Decrypting AES key with RSA private key...")
        
        # Load private key
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        # Decrypt AES key
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        logger.info("✓ AES key decrypted with RSA")
        return aes_key
        
    except Exception as e:
        logger.error(f"Failed to decrypt AES key: {str(e)}")
        raise CryptoError(f"Failed to decrypt AES key: {str(e)}")


def encrypt_file(file_path: str, public_key_path: str, output_path: str) -> str:
    """
    Encrypt a file using hybrid AES + RSA encryption
    
    Args:
        file_path: Path to file to encrypt
        public_key_path: Path to RSA public key
        output_path: Path to save encrypted bundle
        
    Returns:
        Path to saved encrypted bundle
    """
    try:
        logger.info(f"Starting encryption of {file_path}")
        
        # Read input file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        logger.info(f"Read {len(file_data)} bytes from {file_path}")
        
        # Load public key
        with open(public_key_path, 'rb') as f:
            public_key_pem = f.read()
        
        # Generate random AES key
        aes_key = generate_aes_key()
        
        # Encrypt file with AES
        encrypted_file, iv = encrypt_file_aes(file_data, aes_key)
        
        # Encrypt AES key with RSA
        encrypted_aes_key = encrypt_aes_key_with_rsa(aes_key, public_key_pem)
        
        # Create encrypted bundle
        bundle = {
            'metadata': {
                'original_filename': os.path.basename(file_path),
                'original_size': len(file_data),
                'encrypted_size': len(encrypted_file),
                'algorithm': 'AES-256-GCM + RSA-4096',
                'created_by': 'cloq_crypto_utils'
            },
            'encrypted_file': base64.b64encode(encrypted_file).decode('utf-8'),
            'encrypted_aes_key': base64.b64encode(encrypted_aes_key).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8')
        }
        
        # Save bundle
        output_dir = os.path.dirname(output_path)
        if output_dir:  # Only create directory if there's a directory path
            os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(bundle, f, indent=2)
        
        logger.info(f"✓ Encrypted bundle saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to encrypt file: {str(e)}")
        raise CryptoError(f"Failed to encrypt file: {str(e)}")


def decrypt_file(encrypted_bundle_path: str, private_key_path: str, output_path: str) -> str:
    """
    Decrypt a file from encrypted bundle
    
    Args:
        encrypted_bundle_path: Path to encrypted bundle
        private_key_path: Path to RSA private key
        output_path: Path to save decrypted file
        
    Returns:
        Path to saved decrypted file
    """
    try:
        logger.info(f"Starting decryption of {encrypted_bundle_path}")
        
        # Load encrypted bundle
        with open(encrypted_bundle_path, 'r') as f:
            bundle = json.load(f)
        
        # Load private key
        with open(private_key_path, 'rb') as f:
            private_key_pem = f.read()
        
        # Decode base64 components
        encrypted_file = base64.b64decode(bundle['encrypted_file'])
        encrypted_aes_key = base64.b64decode(bundle['encrypted_aes_key'])
        iv = base64.b64decode(bundle['iv'])
        
        # Decrypt AES key
        aes_key = decrypt_aes_key_with_rsa(encrypted_aes_key, private_key_pem)
        
        # Decrypt file
        decrypted_file = decrypt_file_aes(encrypted_file, aes_key, iv)
        
        # Save decrypted file
        output_dir = os.path.dirname(output_path)
        if output_dir:  # Only create directory if there's a directory path
            os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(decrypted_file)
        
        logger.info(f"✓ Decrypted file saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to decrypt file: {str(e)}")
        raise CryptoError(f"Failed to decrypt file: {str(e)}")


if __name__ == "__main__":
    """
    Demo end-to-end encryption/decryption workflow
    """
    print("🔐 Cloq Crypto Utils - Demo")
    print("=" * 50)
    
    try:
        # Create demo directory
        demo_dir = "demo_crypto"
        os.makedirs(demo_dir, exist_ok=True)
        
        # 1. Generate keypair
        print("\n1️⃣ Generating RSA keypair...")
        private_key, public_key = generate_rsa_keypair()
        
        private_path = os.path.join(demo_dir, "demo_private.pem")
        public_path = os.path.join(demo_dir, "demo_public.pem")
        save_keypair(private_key, public_key, private_path, public_path)
        
        # 2. Create sample file
        print("\n2️⃣ Creating sample file...")
        sample_content = "Hello, this is a secret software bundle that needs to be encrypted!\nIt contains sensitive code and configuration data.\n"
        sample_file = os.path.join(demo_dir, "sample_software.txt")
        
        with open(sample_file, 'w') as f:
            f.write(sample_content)
        
        print(f"✓ Created sample file: {sample_file}")
        
        # 3. Encrypt file
        print("\n3️⃣ Encrypting file...")
        encrypted_bundle = os.path.join(demo_dir, "sample_software.clq")
        encrypt_file(sample_file, public_path, encrypted_bundle)
        
        # 4. Decrypt file
        print("\n4️⃣ Decrypting file...")
        decrypted_file = os.path.join(demo_dir, "decrypted_software.txt")
        decrypt_file(encrypted_bundle, private_path, decrypted_file)
        
        # 5. Verify content matches
        print("\n5️⃣ Verifying decryption...")
        with open(decrypted_file, 'r') as f:
            decrypted_content = f.read()
        
        if decrypted_content == sample_content:
            print("✅ SUCCESS: Decrypted content matches original!")
        else:
            print("❌ FAILURE: Decrypted content does not match original!")
            print(f"Original length: {len(sample_content)}")
            print(f"Decrypted length: {len(decrypted_content)}")
        
        # 6. Show bundle structure
        print("\n6️⃣ Encrypted bundle structure:")
        with open(encrypted_bundle, 'r') as f:
            bundle_data = json.load(f)
        
        print(f"  - Original filename: {bundle_data['metadata']['original_filename']}")
        print(f"  - Original size: {bundle_data['metadata']['original_size']} bytes")
        print(f"  - Encrypted size: {bundle_data['metadata']['encrypted_size']} bytes")
        print(f"  - Algorithm: {bundle_data['metadata']['algorithm']}")
        print(f"  - Bundle size: {os.path.getsize(encrypted_bundle)} bytes")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"📁 Demo files created in: {demo_dir}/")
        print(f"🔑 Keys: demo_private.pem, demo_public.pem")
        print(f"📦 Bundle: sample_software.clq")
        print(f"🔓 Decrypted: decrypted_software.txt")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        raise
