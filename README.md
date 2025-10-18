# Cloq - Software Black Boxes Between Enterprises

A control-plane service that securely packages third-party software into encrypted black boxes deployable by enterprise clients.

## 🏗️ Architecture

Cloq provides a secure intermediary system with three main components:

### 📦 **Vendor Layer** (`src/vendor/`)
- **Vendor CLI**: Encrypt and upload software bundles
- **Key Management**: Generate enterprise keypairs for testing
- **Bundle Processing**: Package software into encrypted artifacts

### 🎛️ **Control Plane** (`src/cloq-cp/`)
- **FastAPI Backend**: REST API for vendors and enterprises
- **Crypto Utils**: RSA + AES encryption/decryption primitives
- **Storage**: Local artifact storage with metadata tracking
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

### 4. Vendor: Encrypt and Upload
```bash
python -m src.vendor.vendor_cli upload my_software.tar.gz --public-key enterprise_keys/enterprise_public.pem
```

### 5. Enterprise: Download and Decrypt
```bash
python -m src.enterprise.enterprise_cli download <artifact-id> --private-key enterprise_keys/enterprise_private.pem
```

## 📁 Project Structure

```
cloq/
├── src/
│   ├── vendor/           # Vendor tools and CLI
│   ├── cloq-cp/         # Control plane backend
│   │   ├── storage/     # Storage abstraction
│   │   ├── main.py      # FastAPI application
│   │   └── crypto_utils.py  # Cryptographic primitives
│   └── enterprise/      # Enterprise tools and CLI
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 API Endpoints

### Vendor API
- `POST /vendor/upload` - Upload encrypted bundle
- `GET /vendor/list` - List vendor artifacts

### Enterprise API  
- `GET /enterprise/download/{id}` - Download encrypted artifact
- `POST /enterprise/decrypt` - Decrypt artifact

### Metadata API
- `GET /metadata/artifacts` - List all artifacts
- `GET /metadata/artifacts/{id}` - Get artifact details

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
