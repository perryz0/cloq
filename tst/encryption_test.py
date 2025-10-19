#!/usr/bin/env python3
"""
Open Source Encryption Test

This test demonstrates how Cloq can transform an open-source project
into a black box deployment while preserving its functionality.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import git
import stat # Add this to your imports

def remove_readonly_and_try_again(func, path, excinfo):
    """
    Error handler for shutil.rmtree.
    If the error is access denied (e.g. read-only file),
    it changes the permission and then retries the removal.
    """
    # Check if the error is due to an access problem
    if func in (os.rmdir, os.remove, os.unlink):
        # Change file permissions to allow write
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # Set to full permissions
        try:
            func(path)
        except Exception:
            # If still fails, reraise the original error
            raise
    else:
        # For other errors, reraise
        raise
# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cloq_cp.crypto_utils import (
    generate_rsa_keypair,
    save_keypair,
    encrypt_file,
    decrypt_file
)

class OpenSourcePackage:
    """Handles cloning and packaging of open source software"""
    
    def __init__(self, repo_url: str, package_name: str):
        self.repo_url = repo_url
        self.package_name = package_name
        self.temp_dir = None
        self.repo_dir = None
    
    # def clone_and_package(self):
    #     """Clone the repository and prepare it for encryption"""
    #     print(f"📦 Cloning repository: {self.repo_url}")
        
    #     # Create temporary directory
    #     self.temp_dir = tempfile.mkdtemp(prefix=f"{self.package_name}_")
    #     self.repo_dir = os.path.join(self.temp_dir, self.package_name)
        
    #     # Clone the repository
    #     git.Repo.clone_from(self.repo_url, self.repo_dir)
    #     print(f"✅ Repository cloned to: {self.repo_dir}")
        
    #     # Remove .git directory to prepare for packaging
    #     git_dir = os.path.join(self.repo_dir, ".git")
    #     if os.path.exists(git_dir):
    #         shutil.rmtree(git_dir)
        
    #     return self.repo_dir

    def clone_and_package(self):
        """Clone the repository and prepare it for encryption"""
        print(f"📦 Cloning repository: {self.repo_url}")
        
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix=f"{self.package_name}_")
        self.repo_dir = os.path.join(self.temp_dir, self.package_name)
        
        # Clone the repository
        # Store the result of clone_from to ensure it completes and no resource is implicitly held
        repo = git.Repo.clone_from(self.repo_url, self.repo_dir)
        repo.close() # Explicitly close the repository object
        
        print(f"✅ Repository cloned to: {self.repo_dir}")
    
        # Remove .git directory to prepare for packaging
        git_dir = os.path.join(self.repo_dir, ".git")
        if os.path.exists(git_dir):
            # Use the onerror handler to fix read-only issues on Windows
            shutil.rmtree(git_dir, onerror=remove_readonly_and_try_again)
        
        return self.repo_dir
    
    def create_tarball(self):
        """Create a tarball of the cloned repository"""
        import tarfile
        
        tarball_path = os.path.join(self.temp_dir, f"{self.package_name}.tar.gz")
        
        with tarfile.open(tarball_path, "w:gz") as tar:
            tar.add(self.repo_dir, arcname=self.package_name)
        
        print(f"📦 Tarball created: {tarball_path}")
        return tarball_path
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up: {self.temp_dir}")

def test_opensource_encryption(repo_url: str):
    """Test encrypting and running an open source project"""
    print("🚀 Cloq Open Source Encryption Test")
    print("=" * 60)
    
    try:
        # === VENDOR SIDE ===
        print("\n🏭 VENDOR SIDE - Packaging Open Source Project")
        print("-" * 60)
        
        # 1. Clone and package the repository
        package_name = repo_url.split('/')[-1].replace('.git', '')
        package = OpenSourcePackage(repo_url, package_name)
        repo_dir = package.clone_and_package()
        tarball_path = package.create_tarball()
        
        # 2. Generate encryption keys
        print("\n🔑 Generating encryption keys...")
        private_key, public_key = generate_rsa_keypair()
        
        keys_dir = "test_keys"
        os.makedirs(keys_dir, exist_ok=True)
        private_key_path = os.path.join(keys_dir, "opensource_private.pem")
        public_key_path = os.path.join(keys_dir, "opensource_public.pem")
        
        save_keypair(private_key, public_key, private_key_path, public_key_path)
        print(f"✅ Keys saved to {keys_dir}/")
        
        # 3. Encrypt the package
        print("\n🔒 Encrypting open source package...")
        encrypted_bundle_path = f"{package_name}.encrypted.clq"
        encrypt_file(tarball_path, public_key_path, encrypted_bundle_path)
        
        print(f"✅ Encrypted package: {encrypted_bundle_path}")
        print(f"📊 Original size: {os.path.getsize(tarball_path)} bytes")
        print(f"📊 Encrypted size: {os.path.getsize(encrypted_bundle_path)} bytes")
        
        # === ENTERPRISE SIDE ===
        print("\n\n🏢 ENTERPRISE SIDE - Deploying Encrypted Package")
        print("-" * 60)
        
        # 4. Decrypt the package
        print("\n🔓 Decrypting package...")
        decrypted_tarball_path = f"{package_name}_decrypted.tar.gz"
        decrypt_file(encrypted_bundle_path, private_key_path, decrypted_tarball_path)
        
        print(f"✅ Decrypted package: {decrypted_tarball_path}")
        
        # 5. Extract the package
        print("\n📂 Extracting package...")
        enterprise_temp_dir = tempfile.mkdtemp(prefix="enterprise_")
        
        import tarfile
        with tarfile.open(decrypted_tarball_path, "r:gz") as tar:
            tar.extractall(enterprise_temp_dir)
        
        extracted_dir = os.path.join(enterprise_temp_dir, package_name)
        print(f"✅ Extracted to: {extracted_dir}")
        
        # ... (inside test_opensource_encryption function, after step 5)

        extracted_dir = os.path.join(enterprise_temp_dir, package_name)
        print(f"✅ Extracted to: {extracted_dir}")
        
        # 6. RUN THE DECRYPTED OPEN SOURCE PACKAGE (The Black Box Execution)
        print("\n\n▶️ RUNNING DECRYPTED BLACK BOX CODE (ENTERPRISE EXECUTION)")
        print("-" * 60)
        
        # Assuming the main execution script is 'Advcalculator.py'
        # For the Advance-Calc-in-python repo, let's assume the entry point is a script named 'calculator.py'
        # NOTE: You MUST check the actual entry point of the repository you cloned.
        main_script_path = os.path.join(extracted_dir, "Advcalculator.py") 
        
        import subprocess
        
        if os.path.exists(main_script_path):
            # FIX 2 & 3: Handle Interactive Input and Encoding
            child_env = os.environ.copy()
            # Set PYTHONIOENCODING for the inner script
            child_env['PYTHONIOENCODING'] = 'utf-8' 
            
            # The program is interactive. We send a sequence of commands to perform 
            # a simple calculation (e.g., '1' for addition) and then exit ('q').
            # NOTE: You may need to adjust this sequence if 'q' is not the exit command.
            # Example sequence: '1' (Addition) + '\n' + '10' + '\n' + '20' + '\n' + 'q' + '\n'
            # Let's try a simple sequence that performs addition and then quits the menu.
            input_sequence = "1\n10\n20\nq\n" # This sequence attempts to run Addition (10+20) and then Quit.
            
            print(f"Sending non-interactive input: {repr(input_sequence.strip().replace('\\n', ', '))} to test functionality and exit.")
            # Run the calculator script using a subprocess
            execution_result = subprocess.run(
                [sys.executable, main_script_path], # sys.executable ensures the script runs in the same environment
                capture_output=True,
                text=True,
                input=input_sequence,
                timeout=15, # Set a timeout just in case
                env=child_env,
                encoding="utf-8"
            )
            
            # Print the output from the execution
            print("\n--- Start Black Box Program Output ---")
            print(execution_result.stdout)
            print("--- End Black Box Program Output ---")
            
            if execution_result.returncode == 0:
                print("\n✅ Decrypted program executed successfully!")
            else:
                print(f"\n❌ Decrypted program failed with return code {execution_result.returncode}. STDERR: {execution_result.stderr}")
                
        else:
            print(f"\n⚠️ WARNING: Could not find main script at {main_script_path}. Execution step skipped.")


        # === CLEANUP ===
        print("\n🧹 Cleaning up test files...")
        package.cleanup()
        
        # Clean up test files
        for file_path in [encrypted_bundle_path, decrypted_tarball_path]:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"  Removed: {file_path}")
        
        if os.path.exists(enterprise_temp_dir):
            shutil.rmtree(enterprise_temp_dir)
            print(f"  Removed: {enterprise_temp_dir}")
        
        print("\n🎉 Open source encryption test completed successfully!")
        print("\n📋 SUMMARY:")
        print("  ✅ Cloned open source project")
        print("  ✅ Package encrypted with hybrid encryption")
        print("  ✅ Enterprise received encrypted package")
        print("  ✅ Package successfully decrypted")
        print("\n🔐 The open source project is now ready for")
        print("   secure deployment as a black box!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Example usage with a small open source project
    REPO_URL = "https://github.com/AdityaRoy999/Advance-Calc-in-python.git"  # Replace with actual repo
    success = test_opensource_encryption(REPO_URL)
    sys.exit(0 if success else 1)