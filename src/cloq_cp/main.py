#!/usr/bin/env python3
"""
Cloq Control Plane - FastAPI Backend

This is the main FastAPI application that provides:
- REST API endpoints for vendors and enterprises
- Artifact storage and management
- Cryptographic operations coordination
- Metadata tracking and serving
"""

import sys
import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cloq_cp.crypto_utils import ArtifactBundler, KeyManager


# Pydantic models
class ArtifactMetadata(BaseModel):
    """Artifact metadata model"""
    id: str
    vendor_id: str
    name: str
    version: str
    upload_date: str
    encrypted_size: int
    status: str
    metadata: Dict[str, Any]


class UploadResponse(BaseModel):
    """Upload response model"""
    artifact_id: str
    status: str
    message: str


class DownloadRequest(BaseModel):
    """Download request model"""
    artifact_id: str
    enterprise_id: str


# Initialize FastAPI app
app = FastAPI(
    title="Cloq Control Plane API",
    description="Secure software packaging control plane",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for MVP (replace with database later)
artifacts_db: Dict[str, ArtifactMetadata] = {}
artifact_files: Dict[str, str] = {}  # artifact_id -> file_path


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Cloq Control Plane",
        "version": "0.1.0",
        "description": "Secure software packaging control plane",
        "endpoints": {
            "vendor": ["/vendor/upload", "/vendor/list"],
            "enterprise": ["/enterprise/download/{id}", "/enterprise/decrypt"],
            "metadata": ["/metadata/artifacts", "/metadata/artifacts/{id}"]
        }
    }


# Vendor endpoints
@app.post("/vendor/upload", response_model=UploadResponse)
async def vendor_upload(
    file: UploadFile = File(...),
    vendor_id: str = Form(...),
    name: str = Form(...),
    version: str = Form(...),
    metadata: str = Form(default="{}")
):
    """
    Upload and encrypt a vendor bundle
    
    Args:
        file: Bundle file to upload
        vendor_id: Vendor identifier
        name: Bundle name
        version: Bundle version
        metadata: JSON metadata string
        
    Returns:
        Upload response with artifact ID
    """
    try:
        # Generate artifact ID
        artifact_id = str(uuid.uuid4())
        
        # Read file data
        file_data = await file.read()
        
        # Parse metadata
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError:
            parsed_metadata = {}
        
        # Add additional metadata
        parsed_metadata.update({
            "original_filename": file.filename,
            "original_size": len(file_data),
            "upload_date": datetime.now().isoformat(),
            "vendor_id": vendor_id
        })
        
        # TODO: Encrypt with enterprise public key
        # For now, store the file data directly
        print(f"📦 Processing upload: {file.filename} from vendor {vendor_id}")
        
        # Store artifact metadata
        artifact_metadata = ArtifactMetadata(
            id=artifact_id,
            vendor_id=vendor_id,
            name=name,
            version=version,
            upload_date=datetime.now().isoformat(),
            encrypted_size=len(file_data),
            status="uploaded",
            metadata=parsed_metadata
        )
        
        artifacts_db[artifact_id] = artifact_metadata
        
        # Store file (in production, this would be encrypted and stored securely)
        artifacts_dir = Path("artifacts")
        artifacts_dir.mkdir(exist_ok=True)
        
        file_path = artifacts_dir / f"{artifact_id}.cloq"
        with open(file_path, "wb") as f:
            f.write(file_data)
        
        artifact_files[artifact_id] = str(file_path)
        
        return UploadResponse(
            artifact_id=artifact_id,
            status="success",
            message=f"Bundle uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/vendor/list")
async def vendor_list(vendor_id: str):
    """
    List uploaded bundles for a vendor
    
    Args:
        vendor_id: Vendor identifier
        
    Returns:
        List of vendor's artifacts
    """
    vendor_artifacts = [
        artifact for artifact in artifacts_db.values()
        if artifact.vendor_id == vendor_id
    ]
    
    return {
        "vendor_id": vendor_id,
        "artifacts": vendor_artifacts,
        "count": len(vendor_artifacts)
    }


# Enterprise endpoints
@app.get("/enterprise/download/{artifact_id}")
async def enterprise_download(artifact_id: str):
    """
    Download encrypted artifact
    
    Args:
        artifact_id: Artifact identifier
        
    Returns:
        Encrypted artifact file
    """
    if artifact_id not in artifacts_db:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    if artifact_id not in artifact_files:
        raise HTTPException(status_code=404, detail="Artifact file not found")
    
    file_path = artifact_files[artifact_id]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Artifact file not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=f"{artifacts_db[artifact_id].name}.cloq",
        media_type="application/octet-stream"
    )


@app.post("/enterprise/decrypt")
async def enterprise_decrypt(
    artifact_id: str = Form(...),
    private_key: UploadFile = File(...)
):
    """
    Decrypt artifact (placeholder - actual decryption happens client-side)
    
    Args:
        artifact_id: Artifact identifier
        private_key: Enterprise private key
        
    Returns:
        Decryption status
    """
    if artifact_id not in artifacts_db:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    # In a real implementation, this would handle server-side decryption
    # For MVP, decryption happens client-side with the enterprise CLI
    
    return {
        "artifact_id": artifact_id,
        "status": "decrypt_client_side",
        "message": "Use enterprise CLI to decrypt artifact with your private key"
    }


# Metadata endpoints (for dashboard)
@app.get("/metadata/artifacts")
async def metadata_artifacts():
    """
    Get all artifacts metadata for dashboard
    
    Returns:
        List of all artifacts with metadata
    """
    return {
        "artifacts": list(artifacts_db.values()),
        "count": len(artifacts_db),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/metadata/artifacts/{artifact_id}")
async def metadata_artifact(artifact_id: str):
    """
    Get specific artifact metadata
    
    Args:
        artifact_id: Artifact identifier
        
    Returns:
        Artifact metadata
    """
    if artifact_id not in artifacts_db:
        raise HTTPException(status_code=404, detail="Artifact not found")
    
    return artifacts_db[artifact_id]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "artifacts_count": len(artifacts_db)
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Cloq Control Plane...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "src.cloq_cp.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
