# Enterprise Module

This module contains tools for enterprise clients to interact with the Cloq control plane.

## Components

### `enterprise_cli.py`
Command-line interface for enterprises to:
- Download encrypted artifacts from Cloq control plane
- Decrypt sealed software bundles using private keys
- Validate artifact integrity
- Manage enterprise credentials and keys

## Usage

```bash
# Download and decrypt an artifact
python -m src.enterprise.enterprise_cli download artifact-123 --private-key enterprise_keys/enterprise_private.pem

# List available artifacts
python -m src.enterprise.enterprise_cli list

# Validate artifact integrity
python -m src.enterprise.enterprise_cli validate artifact.cloq --private-key enterprise_keys/enterprise_private.pem
```

## Workflow

1. **Receive Keys**: Enterprise generates RSA keypair and shares public key with vendors
2. **Download**: Download encrypted artifacts from Cloq control plane
3. **Decrypt**: Use private key to decrypt and extract software bundle
4. **Deploy**: Run the decrypted software in enterprise environment

## Security

- Enterprises keep their private keys secure and never share them
- Only enterprises with the correct private key can decrypt artifacts
- All decryption happens client-side for maximum security
- Artifact integrity is verified during decryption

## Key Management

- **Private Keys**: Must be kept secure and never shared
- **Public Keys**: Shared with vendors for encryption
- **Key Rotation**: Supported through the control plane
- **Backup**: Private keys should be backed up securely
