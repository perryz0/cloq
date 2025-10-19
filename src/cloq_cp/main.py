#!/usr/bin/env python3
"""
Cloq Control Plane - Simple MVP API

A minimal control plane that acts as a neutral pass-through host for encrypted bundles.
No authentication, no database - just file storage with UUID-based artifact IDs.

This demonstrates the core concept of Cloq as a neutral intermediary for encrypted
software distribution between vendors and enterprises.
"""

import os
import uuid
import logging
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Cloq Control Plane - MVP",
    description="Simple pass-through host for encrypted software bundles",
    version="0.1.0"
)

# Storage configuration
STORAGE_DIR = Path("src/cloq_cp/storage")
STORAGE_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "service": "Cloq Control Plane - MVP",
        "version": "0.1.0",
        "description": "Simple pass-through host for encrypted software bundles",
        "endpoints": {
            "upload": "POST /upload - Upload encrypted bundle",
            "download": "GET /download/{artifact_id} - Download encrypted bundle"
        }
    }


@app.post("/upload")
async def upload_artifact(file: UploadFile = File(...)) -> Dict[str, str]:
    """
    Upload an encrypted software bundle
    
    Args:
        file: The encrypted bundle file to upload
        
    Returns:
        JSON response with artifact ID and success message
    """
    try:
        # Generate unique artifact ID
        artifact_id = str(uuid.uuid4())
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Save file to storage
        file_path = STORAGE_DIR / f"{artifact_id}.cloq"
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Log the upload
        logger.info(f"📤 UPLOAD: {file.filename} -> {artifact_id}")
        logger.info(f"   Size: {file_size:,} bytes")
        logger.info(f"   Saved to: {file_path}")
        
        return {
            "artifact_id": artifact_id,
            "message": "Stored successfully",
            "filename": file.filename,
            "size_bytes": str(file_size)
        }
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/download/{artifact_id}")
async def download_artifact(artifact_id: str):
    """
    Download an encrypted software bundle
    
    Args:
        artifact_id: The UUID of the artifact to download
        
    Returns:
        File download response
    """
    try:
        # Construct file path
        file_path = STORAGE_DIR / f"{artifact_id}.cloq"
        
        # Check if file exists
        if not file_path.exists():
            logger.warning(f"❌ DOWNLOAD: Artifact {artifact_id} not found")
            raise HTTPException(status_code=404, detail="Artifact not found")
        
        # Get file info
        file_size = file_path.stat().st_size
        
        # Log the download
        logger.info(f"📥 DOWNLOAD: {artifact_id}")
        logger.info(f"   Size: {file_size:,} bytes")
        logger.info(f"   Path: {file_path}")
        
        # Return file as download
        return FileResponse(
            path=str(file_path),
            filename=f"{artifact_id}.cloq",
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    storage_files = list(STORAGE_DIR.glob("*.cloq"))
    
    return {
        "status": "healthy",
        "storage_directory": str(STORAGE_DIR),
        "artifacts_count": len(storage_files),
        "storage_size_bytes": sum(f.stat().st_size for f in storage_files)
    }


@app.get("/list")
async def list_artifacts():
    """List all stored artifacts (for debugging)"""
    artifacts = []
    
    for file_path in STORAGE_DIR.glob("*.cloq"):
        artifact_id = file_path.stem  # Remove .cloq extension
        file_size = file_path.stat().st_size
        
        artifacts.append({
            "artifact_id": artifact_id,
            "size_bytes": file_size,
            "filename": f"{artifact_id}.cloq"
        })
    
    return {
        "artifacts": artifacts,
        "count": len(artifacts),
        "total_size_bytes": sum(a["size_bytes"] for a in artifacts)
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Cloq Control Plane - MVP")
    print("=" * 50)
    print(f"📁 Storage directory: {STORAGE_DIR}")
    print(f"🌐 API will be available at: http://localhost:9000")
    print(f"📚 API docs available at: http://localhost:9000/docs")
    print("=" * 50)
    
    uvicorn.run(
        "src.cloq_cp.main:app",
        host="0.0.0.0",
        port=9000,
        reload=True
    )