# Cloq - Software Black Boxes Between Enterprises

A control-plane service that securely packages third-party software into encrypted black boxes deployable by enterprise clients.

## 🏗️ Architecture

Cloq provides a secure intermediary system with three main components:

### 📦 **Vendor Layer** (`src/vendor/`)
- **Vendor CLI**: Encrypt and upload software bundles
- **Key Management**: Generate enterprise keypairs for testing
- **Bundle Processing**: Package software into encrypted artifacts

### 🎛️ **Control Plane** (`src/cloq_cp/`)
- **FastAPI Backend**: Simple REST API for file upload/download
- **Crypto Utils**: RSA + AES encryption/decryption primitives
- **Storage**: Local file storage with UUID-based artifact IDs
- **Zero-Knowledge**: Cannot decrypt artifacts, only manages them

### 🏢 **Enterprise Layer** (`src/enterprise/`)
- **Enterprise CLI**: Download and decrypt artifacts
- **Client-Side Decryption**: Private keys never leave enterprise environment
- **Validation**: Verify artifact integrity and authenticity

## 🔐 Security Model

**Hybrid Encryption Strategy:**
- **AES-256-GCM**: Fast, authenticated encryption for content
- **RSA-4096**: Secure key exchange using OAEP padding
- **Zero-Knowledge**: Control plane cannot access unencrypted content

**Key Separation:**
- Vendors encrypt with enterprise **public keys**
- Enterprises decrypt with their **private keys**
- Control plane never has access to private keys

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Control Plane
```bash
python -m src.cloq_cp.main
```
API available at: http://localhost:8000

### 3. Generate Enterprise Keys
```bash
python -m src.vendor.vendor_cli generate-keys
```

### 4. Test the Crypto Workflow
```bash
# Test standalone encryption/decryption
python tst/crypto_test.py

# Test control plane API (requires running server)
python tst/control_plane_test.py
```

### 5. Generate Keys and Test Encryption
```bash
# Generate enterprise keys
python -m src.vendor.vendor_cli generate-keys

# Encrypt a file using crypto_utils
python -c "
from src.cloq_cp.crypto_utils import encrypt_file
encrypt_file('test_file.txt', 'enterprise_keys/enterprise_public.pem', 'encrypted.clq')
"
```

## 📁 Project Structure

```
cloq/
├── src/
│   ├── vendor/           # Vendor tools and CLI
│   ├── cloq_cp/         # Control plane backend
│   │   ├── storage/     # Artifact storage directory
│   │   ├── main.py      # Simple FastAPI application
│   │   └── crypto_utils.py  # Cryptographic primitives
│   └── enterprise/      # Enterprise tools and CLI
├── tst/                 # Test suite
│   ├── crypto_test.py   # Standalone crypto workflow test
│   └── control_plane_test.py  # Control plane API test
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 API Endpoints (Simple MVP)

### Core Endpoints
- `POST /upload` - Upload encrypted bundle (multipart/form-data)
- `GET /download/{artifact_id}` - Download encrypted bundle by UUID
- `GET /health` - Health check with storage statistics
- `GET /list` - List all stored artifacts (for debugging)

### Example Usage
```bash
# Upload a file
curl -X POST -F "file=@encrypted_bundle.clq" http://localhost:8000/upload

# Download a file
curl http://localhost:8000/download/{artifact_id} -o downloaded.clq

# Check health
curl http://localhost:8000/health
```

## 🧪 Testing

The project includes comprehensive tests to demonstrate the complete workflow:

### Standalone Crypto Test
```bash
python tst/crypto_test.py
```
- Creates a complete software package (Advanced Calculator)
- Encrypts the entire package using hybrid encryption
- Decrypts and runs the software to verify functionality preservation

### Control Plane API Test
```bash
# Start control plane first
python -m src.cloq_cp.main

# Run API tests (in another terminal)
python tst/control_plane_test.py
```
- Tests file upload/download through the control plane
- Demonstrates complete encrypted workflow
- Verifies the control plane acts as neutral intermediary

## 🎯 Use Cases

- **Software Vendors**: Securely distribute software to enterprise clients
- **Enterprise IT**: Deploy third-party software without exposing internal systems
- **Compliance**: Meet security requirements for software distribution
- **Audit Trail**: Track all software deployments and access

## 🔮 Roadmap

- [ ] Web dashboard for artifact visualization
- [ ] Cloud storage integration (S3, Azure Blob)
- [ ] Authentication and authorization
- [ ] Rate limiting and quotas
- [ ] Multi-tenant support
- [ ] Audit logging and compliance reporting

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
