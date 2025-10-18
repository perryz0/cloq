"""
Local Storage Module - File system storage for artifacts

This module provides:
- Local file system storage for artifacts
- Artifact metadata management
- Storage abstraction for future cloud integration
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class LocalStorage:
    """Local file system storage implementation"""
    
    def __init__(self, base_path: str = "artifacts"):
        self.base_path = Path(base_path)
        self.metadata_path = self.base_path / "metadata.json"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure storage directories exist"""
        self.base_path.mkdir(exist_ok=True)
        
        # Initialize metadata file if it doesn't exist
        if not self.metadata_path.exists():
            with open(self.metadata_path, 'w') as f:
                json.dump({}, f)
    
    def store_artifact(self, artifact_id: str, file_data: bytes, 
                      metadata: Dict[str, Any]) -> str:
        """
        Store artifact file and metadata
        
        Args:
            artifact_id: Unique artifact identifier
            file_data: Raw file data to store
            metadata: Artifact metadata
            
        Returns:
            Path to stored artifact file
        """
        # Store file
        file_path = self.base_path / f"{artifact_id}.cloq"
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Store metadata
        self._update_metadata(artifact_id, {
            **metadata,
            "file_path": str(file_path),
            "stored_at": datetime.now().isoformat(),
            "file_size": len(file_data)
        })
        
        return str(file_path)
    
    def retrieve_artifact(self, artifact_id: str) -> Optional[bytes]:
        """
        Retrieve artifact file data
        
        Args:
            artifact_id: Artifact identifier
            
        Returns:
            File data or None if not found
        """
        file_path = self.base_path / f"{artifact_id}.cloq"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def get_artifact_metadata(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """
        Get artifact metadata
        
        Args:
            artifact_id: Artifact identifier
            
        Returns:
            Metadata dictionary or None if not found
        """
        metadata = self._load_metadata()
        return metadata.get(artifact_id)
    
    def list_artifacts(self, vendor_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all artifacts, optionally filtered by vendor
        
        Args:
            vendor_id: Optional vendor filter
            
        Returns:
            List of artifact metadata
        """
        metadata = self._load_metadata()
        
        artifacts = []
        for artifact_id, artifact_metadata in metadata.items():
            if vendor_id is None or artifact_metadata.get('vendor_id') == vendor_id:
                artifacts.append({
                    'artifact_id': artifact_id,
                    **artifact_metadata
                })
        
        return artifacts
    
    def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete artifact and its metadata
        
        Args:
            artifact_id: Artifact identifier
            
        Returns:
            True if deleted successfully
        """
        # Delete file
        file_path = self.base_path / f"{artifact_id}.cloq"
        if file_path.exists():
            file_path.unlink()
        
        # Delete metadata
        metadata = self._load_metadata()
        if artifact_id in metadata:
            del metadata[artifact_id]
            self._save_metadata(metadata)
            return True
        
        return False
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from file"""
        try:
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_metadata(self, metadata: Dict[str, Any]):
        """Save metadata to file"""
        with open(self.metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _update_metadata(self, artifact_id: str, artifact_metadata: Dict[str, Any]):
        """Update metadata for specific artifact"""
        metadata = self._load_metadata()
        metadata[artifact_id] = artifact_metadata
        self._save_metadata(metadata)
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        metadata = self._load_metadata()
        
        total_size = 0
        file_count = 0
        
        for artifact_metadata in metadata.values():
            file_size = artifact_metadata.get('file_size', 0)
            total_size += file_size
            file_count += 1
        
        return {
            "total_artifacts": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "storage_path": str(self.base_path)
        }
