# Cloq Control Plane

The core backend service that manages the secure software packaging system.

## Components

### `main.py`
FastAPI application providing REST API endpoints:
- **Vendor endpoints**: `/vendor/upload`, `/vendor/list`
- **Enterprise endpoints**: `/enterprise/download/{id}`, `/enterprise/decrypt`
- **Metadata endpoints**: `/metadata/artifacts`, `/metadata/artifacts/{id}`

### `crypto_utils.py`
Cryptographic utilities for:
- RSA keypair generation
- AES file encryption/decryption
- Hybrid encryption (AES + RSA)
- Artifact bundling and extraction

### `storage/`
Storage abstraction layer:
- **`local_storage.py`**: Local file system storage (MVP)
- Future cloud storage integration (S3, etc.)

## API Endpoints

### Vendor API
- `POST /vendor/upload` - Upload and encrypt software bundle
- `GET /vendor/list` - List vendor's uploaded artifacts

### Enterprise API
- `GET /enterprise/download/{id}` - Download encrypted artifact
- `POST /enterprise/decrypt` - Decrypt artifact (client-side)

### Metadata API
- `GET /metadata/artifacts` - List all artifacts (dashboard)
- `GET /metadata/artifacts/{id}` - Get specific artifact metadata

## Usage

```bash
# Start the control plane server
python -m src.cloq_cp.main

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

## Architecture

The control plane acts as a secure intermediary:
1. **Receives** encrypted bundles from vendors
2. **Stores** artifacts securely with metadata
3. **Serves** encrypted artifacts to enterprises
4. **Never** has access to unencrypted content or private keys

## Security Model

- **Hybrid Encryption**: AES-256-GCM for content, RSA-4096 for key exchange
- **Zero-Knowledge**: Control plane cannot decrypt artifacts
- **Authenticated Encryption**: All data includes integrity verification
- **Key Separation**: Vendors and enterprises have separate key pairs
