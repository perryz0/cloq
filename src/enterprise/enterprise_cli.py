#!/usr/bin/env python3
"""
Enterprise CLI - Command-line interface for enterprise clients

This CLI allows enterprise clients to:
- Download encrypted artifacts from Cloq
- Decrypt sealed software bundles
- Manage enterprise credentials and keys
- Validate artifact integrity
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cloq_cp.crypto_utils import decrypt_artifact_for_enterprise


class EnterpriseCLI:
    """Enterprise command-line interface"""
    
    def __init__(self):
        self.control_plane_url = "http://localhost:8000"  # Default CP URL
    
    def download_and_decrypt(self, artifact_id: str, private_key_path: str, 
                           output_path: str = None) -> str:
        """
        Download artifact from control plane and decrypt
        
        Args:
            artifact_id: Artifact ID to download
            private_key_path: Path to enterprise private key
            output_path: Path to save decrypted file
            
        Returns:
            Path to decrypted file
        """
        print(f"📥 Downloading artifact: {artifact_id}")
        
        # TODO: Download from control plane
        print("⚠️  Control plane download not yet implemented")
        print("📁 Using local artifact file for demo...")
        
        # For demo purposes, assume artifact file exists locally
        artifact_path = f"artifacts/{artifact_id}.cloq"
        
        if not os.path.exists(artifact_path):
            print(f"❌ Artifact file not found: {artifact_path}")
            return None
        
        print(f"🔓 Decrypting artifact: {artifact_path}")
        
        # Decrypt artifact
        decrypted_path = decrypt_artifact_for_enterprise(
            artifact_path,
            private_key_path,
            output_path
        )
        
        print(f"✅ File decrypted: {decrypted_path}")
        return decrypted_path
    
    def list_available_artifacts(self):
        """List available artifacts for download"""
        print("📋 Listing available artifacts...")
        print("⚠️  Artifact listing not yet implemented")
    
    def validate_artifact(self, artifact_path: str, private_key_path: str) -> bool:
        """
        Validate artifact integrity
        
        Args:
            artifact_path: Path to artifact file
            private_key_path: Path to enterprise private key
            
        Returns:
            True if artifact is valid
        """
        print(f"🔍 Validating artifact: {artifact_path}")
        
        try:
            # Try to decrypt and validate
            temp_path = decrypt_artifact_for_enterprise(
                artifact_path,
                private_key_path,
                "temp_validation_file"
            )
            
            # Check if decryption was successful
            is_valid = os.path.exists(temp_path)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if is_valid:
                print("✅ Artifact validation successful")
            else:
                print("❌ Artifact validation failed")
            
            return is_valid
            
        except Exception as e:
            print(f"❌ Artifact validation failed: {str(e)}")
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Cloq Enterprise CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Download and decrypt command
    download_parser = subparsers.add_parser('download', help='Download and decrypt artifact')
    download_parser.add_argument('artifact_id', help='Artifact ID to download')
    download_parser.add_argument('--private-key', required=True,
                                help='Path to enterprise private key')
    download_parser.add_argument('--output', help='Output path for decrypted file')
    
    # List artifacts command
    list_parser = subparsers.add_parser('list', help='List available artifacts')
    
    # Validate artifact command
    validate_parser = subparsers.add_parser('validate', help='Validate artifact integrity')
    validate_parser.add_argument('artifact_path', help='Path to artifact file')
    validate_parser.add_argument('--private-key', required=True,
                                help='Path to enterprise private key')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = EnterpriseCLI()
    
    if args.command == 'download':
        decrypted_path = cli.download_and_decrypt(
            args.artifact_id, 
            args.private_key, 
            args.output
        )
        if decrypted_path:
            print(f"🎉 Download and decrypt successful! File: {decrypted_path}")
    
    elif args.command == 'list':
        cli.list_available_artifacts()
    
    elif args.command == 'validate':
        is_valid = cli.validate_artifact(args.artifact_path, args.private_key)
        if is_valid:
            print("🎉 Artifact validation successful!")
        else:
            print("❌ Artifact validation failed!")
            sys.exit(1)


if __name__ == "__main__":
    main()
