# Cloq Tests

This directory contains comprehensive tests for the Cloq system.

## crypto_test.py

A full workflow test that demonstrates:

1. **Vendor Side**:
   - Creates a complete software package (Advanced Calculator)
   - Packages it into a tarball
   - Encrypts the entire package using hybrid encryption (AES + RSA)

2. **Enterprise Side**:
   - Decrypts the encrypted package
   - Extracts and runs the software
   - Verifies that all functionality is preserved

## Usage

```bash
# Run the full workflow test
python tst/crypto_test.py
```

## What It Tests

- **Encryption/Decryption**: Hybrid AES-256-GCM + RSA-4096 encryption
- **Functionality Preservation**: Software runs correctly after encryption/decryption
- **Package Integrity**: All files and data structures are preserved
- **End-to-End Workflow**: Complete vendor → enterprise flow

## Expected Output

The test should show:
- ✅ Package creation and encryption
- ✅ Decryption and extraction
- ✅ Software execution with correct results
- ✅ All calculations verified as correct

This demonstrates that Cloq can securely package software while preserving full functionality.
