# Vendor Module

This module contains tools for vendors to interact with the Cloq control plane.

## Components

### `vendor_cli.py`
Command-line interface for vendors to:
- Encrypt software bundles for enterprise clients
- Upload release bundles to Cloq control plane
- Manage vendor credentials and metadata
- List uploaded artifacts

## Usage

```bash
# Generate enterprise keypair for testing
python -m src.vendor.vendor_cli generate-keys

# Encrypt and upload a file
python -m src.vendor.vendor_cli upload my_software.tar.gz --public-key enterprise_keys/enterprise_public.pem

# List uploaded artifacts
python -m src.vendor.vendor_cli list
```

## Workflow

1. **Prepare Bundle**: Vendor packages their software into a bundle (tar.gz, zip, etc.)
2. **Encrypt**: Use vendor CLI to encrypt bundle with enterprise public key
3. **Upload**: Upload encrypted artifact to Cloq control plane
4. **Track**: Monitor upload status and manage artifacts

## Security

- Vendors never see enterprise private keys
- All encryption happens with enterprise public keys
- Artifacts are sealed and cannot be decrypted by vendors
