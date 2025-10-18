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

## control_plane_test.py

A control plane API test that demonstrates:

1. **Basic API Functionality**:
   - Upload files via POST /upload
   - Download files via GET /download/{artifact_id}
   - Verify file integrity through the control plane

2. **Complete Encrypted Workflow**:
   - Vendor encrypts software package
   - Upload encrypted bundle to control plane
   - Enterprise downloads encrypted bundle
   - Enterprise decrypts and verifies functionality

## Usage

```bash
# Run the crypto workflow test (standalone)
python tst/crypto_test.py

# Run the control plane API tests (requires running server)
python -m src.cloq_cp.main  # Start control plane in another terminal
python tst/control_plane_test.py
```

## What It Tests

### crypto_test.py
- **Encryption/Decryption**: Hybrid AES-256-GCM + RSA-4096 encryption
- **Functionality Preservation**: Software runs correctly after encryption/decryption
- **Package Integrity**: All files and data structures are preserved
- **End-to-End Workflow**: Complete vendor → enterprise flow

### control_plane_test.py
- **API Endpoints**: Upload and download functionality
- **File Storage**: UUID-based artifact storage
- **Encrypted Workflow**: Complete vendor → control plane → enterprise flow
- **Neutral Pass-through**: Control plane acts as neutral intermediary

## Expected Output

Both tests should show:
- ✅ Package creation and encryption
- ✅ Upload to control plane
- ✅ Download from control plane
- ✅ Decryption and verification
- ✅ All functionality preserved

This demonstrates that Cloq can securely package software while preserving full functionality through a neutral control plane intermediary.
