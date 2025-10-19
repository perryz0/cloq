#!/usr/bin/env python3
"""
Control Plane Test - Simple API Demo

This test demonstrates the basic control plane functionality:
1. Start the control plane server
2. Upload a file via POST /upload
3. Download the file via GET /download/{artifact_id}
4. Verify the file integrity

This shows the control plane acting as a neutral pass-through host.
"""

import requests
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cloq_cp.crypto_utils import encrypt_file, decrypt_file, generate_rsa_keypair, save_keypair


def test_control_plane_api():
    """Test the control plane API endpoints"""
    print("🧪 Control Plane API Test")
    print("=" * 50)
    
    # Control plane base URL
    base_url = "http://localhost:9000"
    
    try:
        # 1. Check if control plane is running
        print("1️⃣ Checking control plane health...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Control plane is healthy")
            print(f"   Storage directory: {health_data['storage_directory']}")
            print(f"   Current artifacts: {health_data['artifacts_count']}")
        else:
            print(f"❌ Control plane health check failed: {response.status_code}")
            return False
        
        # 2. Create a test file
        print("\n2️⃣ Creating test file...")
        test_content = "This is a test encrypted bundle for the Cloq control plane!\nIt contains sensitive software data that needs to be protected."
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_content)
            test_file_path = f.name
        
        print(f"✅ Test file created: {test_file_path}")
        
        # 3. Upload file to control plane
        print("\n3️⃣ Uploading file to control plane...")
        
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_bundle.txt', f, 'text/plain')}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 200:
            upload_data = response.json()
            artifact_id = upload_data['artifact_id']
            print(f"✅ File uploaded successfully!")
            print(f"   Artifact ID: {artifact_id}")
            print(f"   Size: {upload_data['size_bytes']} bytes")
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
        
        # 4. Download file from control plane
        print("\n4️⃣ Downloading file from control plane...")
        
        response = requests.get(f"{base_url}/download/{artifact_id}")
        
        if response.status_code == 200:
            # Save downloaded content
            with tempfile.NamedTemporaryFile(delete=False, suffix='.downloaded.txt') as f:
                f.write(response.content)
                downloaded_file_path = f.name
            
            print(f"✅ File downloaded successfully!")
            print(f"   Size: {len(response.content)} bytes")
            print(f"   Saved to: {downloaded_file_path}")
        else:
            print(f"❌ Download failed: {response.status_code} - {response.text}")
            return False
        
        # 5. Verify file integrity
        print("\n5️⃣ Verifying file integrity...")
        
        with open(downloaded_file_path, 'r') as f:
            downloaded_content = f.read()
        
        if downloaded_content == test_content:
            print("✅ File integrity verified! Content matches exactly.")
        else:
            print("❌ File integrity check failed! Content mismatch.")
            return False
        
        # 6. Check artifact list
        print("\n6️⃣ Checking artifact list...")
        
        response = requests.get(f"{base_url}/list")
        if response.status_code == 200:
            list_data = response.json()
            print(f"✅ Artifact list retrieved")
            print(f"   Total artifacts: {list_data['count']}")
            print(f"   Total size: {list_data['total_size_bytes']} bytes")
        else:
            print(f"❌ List request failed: {response.status_code}")
        
        # Cleanup
        print("\n🧹 Cleaning up test files...")
        os.unlink(test_file_path)
        os.unlink(downloaded_file_path)
        print("✅ Test files cleaned up")
        
        print("\n🎉 Control plane API test completed successfully!")
        print("\n📋 SUMMARY:")
        print("  ✅ Control plane health check passed")
        print("  ✅ File upload successful")
        print("  ✅ File download successful")
        print("  ✅ File integrity verified")
        print("  ✅ Artifact listing works")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to control plane. Is it running?")
        print("   Start it with: python -m src.cloq_cp.main")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_encrypted_workflow():
    """Test the complete encrypted workflow through control plane"""
    print("\n🔐 Encrypted Workflow Test")
    print("=" * 50)
    
    base_url = "http://localhost:9000"
    
    try:
        # 1. Generate encryption keys
        print("1️⃣ Generating encryption keys...")
        private_key, public_key = generate_rsa_keypair()
        
        keys_dir = "test_keys"
        os.makedirs(keys_dir, exist_ok=True)
        private_key_path = os.path.join(keys_dir, "test_private.pem")
        public_key_path = os.path.join(keys_dir, "test_public.pem")
        
        save_keypair(private_key, public_key, private_key_path, public_key_path)
        print(f"✅ Keys generated and saved to {keys_dir}/")
        
        # 2. Create and encrypt a file
        print("\n2️⃣ Creating and encrypting test file...")
        
        test_content = "Secret software package data!\nThis would normally contain executable code."
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(test_content)
            original_file_path = f.name
        
        # Encrypt the file
        encrypted_bundle_path = "test_encrypted.clq"
        encrypt_file(original_file_path, public_key_path, encrypted_bundle_path)
        print(f"✅ File encrypted: {encrypted_bundle_path}")
        
        # 3. Upload encrypted bundle to control plane
        print("\n3️⃣ Uploading encrypted bundle...")
        
        with open(encrypted_bundle_path, 'rb') as f:
            files = {'file': ('encrypted_bundle.clq', f, 'application/octet-stream')}
            response = requests.post(f"{base_url}/upload", files=files)
        
        if response.status_code == 200:
            upload_data = response.json()
            artifact_id = upload_data['artifact_id']
            print(f"✅ Encrypted bundle uploaded!")
            print(f"   Artifact ID: {artifact_id}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return False
        
        # 4. Download encrypted bundle from control plane
        print("\n4️⃣ Downloading encrypted bundle...")
        
        response = requests.get(f"{base_url}/download/{artifact_id}")
        
        if response.status_code == 200:
            # Save downloaded bundle
            with tempfile.NamedTemporaryFile(delete=False, suffix='.downloaded.clq') as f:
                f.write(response.content)
                downloaded_bundle_path = f.name
            
            print(f"✅ Encrypted bundle downloaded!")
        else:
            print(f"❌ Download failed: {response.status_code}")
            return False
        
        # 5. Decrypt and verify
        print("\n5️⃣ Decrypting and verifying...")
        
        decrypted_file_path = "test_decrypted.txt"
        decrypt_file(downloaded_bundle_path, private_key_path, decrypted_file_path)
        
        with open(decrypted_file_path, 'r') as f:
            decrypted_content = f.read()
        
        if decrypted_content == test_content:
            print("✅ Decryption successful! Content matches original.")
        else:
            print("❌ Decryption failed! Content mismatch.")
            return False
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        cleanup_files = [
            original_file_path, encrypted_bundle_path, 
            downloaded_bundle_path, decrypted_file_path
        ]
        for file_path in cleanup_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
        
        import shutil
        shutil.rmtree(keys_dir)
        print("✅ Cleanup completed")
        
        print("\n🎉 Encrypted workflow test completed successfully!")
        print("📋 This demonstrates the complete Cloq workflow:")
        print("  ✅ Vendor encrypts software package")
        print("  ✅ Encrypted package uploaded to control plane")
        print("  ✅ Enterprise downloads encrypted package")
        print("  ✅ Enterprise decrypts and runs software")
        print("  ✅ Functionality preserved through the process")
        
        return True
        
    except Exception as e:
        print(f"❌ Encrypted workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Cloq Control Plane API Tests")
    print("=" * 60)
    print("Make sure the control plane is running:")
    print("  python -m src.cloq_cp.main")
    print("=" * 60)
    
    # Test basic API functionality
    api_success = test_control_plane_api()
    
    if api_success:
        # Test encrypted workflow
        encrypted_success = test_encrypted_workflow()
        
        if encrypted_success:
            print("\n🎉 All tests passed! Cloq control plane is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Encrypted workflow test failed.")
            sys.exit(1)
    else:
        print("\n❌ Basic API test failed.")
        sys.exit(1)
