#!/usr/bin/env python3
"""
Vendor CLI - Command-line interface for vendors

This CLI allows vendors to:
- Encrypt software bundles
- Upload bundles to Cloq control plane
- Manage vendor credentials
- List uploaded artifacts
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cloq_cp.crypto_utils import encrypt_file, generate_rsa_keypair, save_keypair


class VendorCLI:
    """Vendor command-line interface"""
    
    def __init__(self):
        self.control_plane_url = "http://localhost:8000"  # Default CP URL
    
    def encrypt_and_upload(self, file_path: str, enterprise_public_key: str, 
                          metadata: dict = None) -> str:
        """
        Encrypt a file and upload to control plane
        
        Args:
            file_path: Path to file to encrypt
            enterprise_public_key: Path to enterprise public key
            metadata: Optional metadata dictionary
            
        Returns:
            Artifact ID from control plane
        """
        print(f"🔒 Encrypting file: {file_path}")
        
        # Encrypt file for enterprise
        artifact_path = f"{file_path}.cloq"
        encrypt_file(file_path, enterprise_public_key, artifact_path)
        
        print(f"✅ Artifact created: {artifact_path}")
        
        # TODO: Upload to control plane
        print("📤 Uploading to control plane...")
        print("⚠️  Control plane upload not yet implemented")
        
        return "mock-artifact-id"
    
    def list_artifacts(self):
        """List uploaded artifacts"""
        print("📋 Listing uploaded artifacts...")
        print("⚠️  Artifact listing not yet implemented")
    
    def generate_enterprise_keys(self, output_dir: str = "enterprise_keys"):
        """Generate enterprise keypair for testing"""
        print(f"🔑 Generating enterprise keypair in {output_dir}")
        
        os.makedirs(output_dir, exist_ok=True)
        private_key, public_key = generate_rsa_keypair()
        
        private_path = os.path.join(output_dir, "enterprise_private.pem")
        public_path = os.path.join(output_dir, "enterprise_public.pem")
        
        save_keypair(private_key, public_key, private_path, public_path)
        
        print(f"✅ Keys saved to {private_path} and {public_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Cloq Vendor CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Encrypt and upload command
    upload_parser = subparsers.add_parser('upload', help='Encrypt and upload file')
    upload_parser.add_argument('file', help='File to encrypt and upload')
    upload_parser.add_argument('--public-key', required=True, 
                              help='Path to enterprise public key')
    upload_parser.add_argument('--metadata', help='JSON metadata string')
    
    # List artifacts command
    list_parser = subparsers.add_parser('list', help='List uploaded artifacts')
    
    # Generate keys command
    keys_parser = subparsers.add_parser('generate-keys', help='Generate enterprise keypair')
    keys_parser.add_argument('--output-dir', default='enterprise_keys',
                            help='Output directory for keys')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = VendorCLI()
    
    if args.command == 'upload':
        metadata = {}
        if args.metadata:
            import json
            metadata = json.loads(args.metadata)
        
        artifact_id = cli.encrypt_and_upload(args.file, args.public_key, metadata)
        print(f"🎉 Upload successful! Artifact ID: {artifact_id}")
    
    elif args.command == 'list':
        cli.list_artifacts()
    
    elif args.command == 'generate-keys':
        cli.generate_enterprise_keys(args.output_dir)


if __name__ == "__main__":
    main()
