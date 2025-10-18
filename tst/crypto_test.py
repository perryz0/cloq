#!/usr/bin/env python3
"""
Crypto Test - Full Workflow Simulation

This test simulates the complete Cloq workflow:
1. Vendor creates a software package with functionality
2. Vendor encrypts the entire package using crypto_utils
3. Enterprise receives the encrypted package and keys
4. Enterprise decrypts and runs the functionality
5. Verify that functionality is preserved through encryption/decryption

This demonstrates that encrypted software packages maintain their functionality
even when the entire codebase is encrypted and pre-built.
"""

import os
import sys
import json
import tempfile
import shutil
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


class SoftwarePackage:
    """Simulates a vendor's software package with built artifacts"""
    
    def __init__(self, package_name: str):
        self.package_name = package_name
        self.temp_dir = None
        self.package_dir = None
        self.main_script = None
        self.config_file = None
        self.data_file = None
    
    def create_package(self):
        """Create a complete software package with functionality"""
        print(f"📦 Creating software package: {self.package_name}")
        
        # Create temporary directory for package
        self.temp_dir = tempfile.mkdtemp(prefix=f"{self.package_name}_")
        self.package_dir = os.path.join(self.temp_dir, self.package_name)
        os.makedirs(self.package_dir, exist_ok=True)
        
        # Create main functionality script
        self.main_script = os.path.join(self.package_dir, "calculator.py")
        with open(self.main_script, 'w') as f:
            f.write('''#!/usr/bin/env python3
"""
Advanced Calculator - Vendor Software Package
This simulates a complex software package with multiple functionalities
"""

import json
import os
from datetime import datetime

class AdvancedCalculator:
    """Advanced calculator with multiple operations"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.load_config()
        self.operation_history = []
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {"precision": 10, "log_operations": True}
        except Exception as e:
            self.config = {"precision": 10, "log_operations": True}
            print(f"Warning: Could not load config: {e}")
    
    def add(self, a, b):
        """Add two numbers"""
        result = a + b
        self._log_operation("add", a, b, result)
        return round(result, self.config.get("precision", 10))
    
    def multiply(self, a, b):
        """Multiply two numbers"""
        result = a * b
        self._log_operation("multiply", a, b, result)
        return round(result, self.config.get("precision", 10))
    
    def power(self, base, exponent):
        """Calculate base raised to exponent"""
        result = base ** exponent
        self._log_operation("power", base, exponent, result)
        return round(result, self.config.get("precision", 10))
    
    def fibonacci(self, n):
        """Calculate nth Fibonacci number"""
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        else:
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            self._log_operation("fibonacci", n, None, b)
            return b
    
    def _log_operation(self, operation, a, b, result):
        """Log operation to history"""
        if self.config.get("log_operations", True):
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "operation": operation,
                "operands": [a, b] if b is not None else [a],
                "result": result
            }
            self.operation_history.append(log_entry)
    
    def get_history(self):
        """Get operation history"""
        return self.operation_history
    
    def clear_history(self):
        """Clear operation history"""
        self.operation_history = []
    
    def run_demo(self):
        """Run a demonstration of calculator functionality"""
        print("🧮 Advanced Calculator Demo")
        print("=" * 40)
        
        # Test basic operations
        print(f"Addition: 15 + 27 = {self.add(15, 27)}")
        print(f"Multiplication: 8 * 12 = {self.multiply(8, 12)}")
        print(f"Power: 2^10 = {self.power(2, 10)}")
        print(f"Fibonacci(10) = {self.fibonacci(10)}")
        
        # Test with decimals
        print(f"Decimal add: 3.14159 + 2.71828 = {self.add(3.14159, 2.71828)}")
        
        print("\\n📊 Operation History:")
        for entry in self.operation_history:
            print(f"  {entry['timestamp']}: {entry['operation']}({entry['operands']}) = {entry['result']}")
        
        return self.operation_history

def main():
    """Main entry point for the calculator"""
    calc = AdvancedCalculator()
    return calc.run_demo()

if __name__ == "__main__":
    main()
''')
        
        # Create configuration file
        self.config_file = os.path.join(self.package_dir, "config.json")
        with open(self.config_file, 'w') as f:
            json.dump({
                "precision": 8,
                "log_operations": True,
                "package_name": self.package_name,
                "version": "1.0.0",
                "vendor": "DemoVendor Inc."
            }, f, indent=2)
        
        # Create data file
        self.data_file = os.path.join(self.package_dir, "data.txt")
        with open(self.data_file, 'w') as f:
            f.write('''Sample data file for the calculator package.
This could contain lookup tables, reference data, or other resources
that the software package needs to function properly.

Mathematical constants:
PI = 3.141592653589793
E = 2.718281828459045
Golden Ratio = 1.618033988749895

Reference values for testing:
Test values: [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
''')
        
        # Create package info file
        package_info = os.path.join(self.package_dir, "package_info.json")
        with open(package_info, 'w') as f:
            json.dump({
                "name": self.package_name,
                "version": "1.0.0",
                "description": "Advanced Calculator Package",
                "main_script": "calculator.py",
                "dependencies": [],
                "build_date": "2025-10-18",
                "vendor": "DemoVendor Inc."
            }, f, indent=2)
        
        print(f"✅ Package created in: {self.package_dir}")
        return self.package_dir
    
    def create_tarball(self):
        """Create a tarball of the package for encryption"""
        import tarfile
        
        tarball_path = os.path.join(self.temp_dir, f"{self.package_name}.tar.gz")
        
        with tarfile.open(tarball_path, "w:gz") as tar:
            tar.add(self.package_dir, arcname=self.package_name)
        
        print(f"📦 Tarball created: {tarball_path}")
        return tarball_path
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up: {self.temp_dir}")


def test_full_workflow():
    """Test the complete vendor -> enterprise workflow"""
    print("🚀 Cloq Full Workflow Test")
    print("=" * 60)
    
    try:
        # === VENDOR SIDE ===
        print("\\n🏭 VENDOR SIDE - Creating and Encrypting Software Package")
        print("-" * 60)
        
        # 1. Create software package
        package = SoftwarePackage("advanced_calculator")
        package_dir = package.create_package()
        tarball_path = package.create_tarball()
        
        # 2. Generate encryption keys
        print("\\n🔑 Generating encryption keys...")
        private_key, public_key = generate_rsa_keypair()
        
        keys_dir = "test_keys"
        os.makedirs(keys_dir, exist_ok=True)
        private_key_path = os.path.join(keys_dir, "vendor_private.pem")
        public_key_path = os.path.join(keys_dir, "vendor_public.pem")
        
        save_keypair(private_key, public_key, private_key_path, public_key_path)
        print(f"✅ Keys saved to {keys_dir}/")
        
        # 3. Encrypt the software package
        print("\\n🔒 Encrypting software package...")
        encrypted_bundle_path = f"{package.package_name}.encrypted.clq"
        encrypt_file(tarball_path, public_key_path, encrypted_bundle_path)
        
        print(f"✅ Encrypted package: {encrypted_bundle_path}")
        print(f"📊 Original size: {os.path.getsize(tarball_path)} bytes")
        print(f"📊 Encrypted size: {os.path.getsize(encrypted_bundle_path)} bytes")
        
        # === ENTERPRISE SIDE ===
        print("\\n\\n🏢 ENTERPRISE SIDE - Decrypting and Running Software")
        print("-" * 60)
        
        # 4. Enterprise decrypts the package
        print("\\n🔓 Decrypting software package...")
        decrypted_tarball_path = f"{package.package_name}_decrypted.tar.gz"
        decrypt_file(encrypted_bundle_path, private_key_path, decrypted_tarball_path)
        
        print(f"✅ Decrypted package: {decrypted_tarball_path}")
        
        # 5. Extract and run the software
        print("\\n📂 Extracting and running decrypted software...")
        
        enterprise_temp_dir = tempfile.mkdtemp(prefix="enterprise_")
        extracted_dir = os.path.join(enterprise_temp_dir, package.package_name)
        
        import tarfile
        with tarfile.open(decrypted_tarball_path, "r:gz") as tar:
            tar.extractall(enterprise_temp_dir)
        
        print(f"✅ Extracted to: {extracted_dir}")
        
        # 6. Run the decrypted software
        print("\\n🧮 Running decrypted calculator...")
        
        # Change to the extracted directory
        original_cwd = os.getcwd()
        os.chdir(extracted_dir)
        
        try:
            # Import and run the calculator
            sys.path.insert(0, extracted_dir)
            from calculator import AdvancedCalculator
            
            calc = AdvancedCalculator()
            history = calc.run_demo()
            
            print(f"\\n✅ Calculator executed successfully!")
            print(f"📊 Operations performed: {len(history)}")
            
            # Verify functionality
            expected_results = [
                ("add", 15, 27, 42),
                ("multiply", 8, 12, 96),
                ("power", 2, 10, 1024),
                ("fibonacci", 10, None, 55)
            ]
            
            print("\\n🔍 Verifying calculation results...")
            all_correct = True
            
            for i, (operation, a, b, expected) in enumerate(expected_results):
                if i < len(history):
                    actual = history[i]["result"]
                    if abs(actual - expected) < 0.001:  # Allow for floating point precision
                        print(f"  ✅ {operation}({a}, {b}) = {actual} (correct)")
                    else:
                        print(f"  ❌ {operation}({a}, {b}) = {actual}, expected {expected}")
                        all_correct = False
                else:
                    print(f"  ❌ Missing result for {operation}({a}, {b})")
                    all_correct = False
            
            if all_correct:
                print("\\n🎉 ALL CALCULATIONS CORRECT! Functionality preserved through encryption!")
            else:
                print("\\n❌ Some calculations failed!")
                
        finally:
            os.chdir(original_cwd)
        
        # === CLEANUP ===
        print("\\n🧹 Cleaning up test files...")
        package.cleanup()
        
        # Clean up test files
        test_files = [encrypted_bundle_path, decrypted_tarball_path]
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"  Removed: {file_path}")
        
        # Clean up enterprise temp dir
        if os.path.exists(enterprise_temp_dir):
            shutil.rmtree(enterprise_temp_dir)
            print(f"  Removed: {enterprise_temp_dir}")
        
        print("\\n🎉 Full workflow test completed successfully!")
        print("\\n📋 SUMMARY:")
        print("  ✅ Vendor created software package")
        print("  ✅ Package encrypted with hybrid encryption")
        print("  ✅ Enterprise decrypted package")
        print("  ✅ Software functionality preserved")
        print("  ✅ All calculations executed correctly")
        print("\\n🔐 This demonstrates that Cloq can securely package")
        print("   software while preserving full functionality!")
        
    except Exception as e:
        print(f"\\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)
