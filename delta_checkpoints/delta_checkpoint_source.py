"""
Delta Checkpoint Data Source Implementation

This module implements a custom Spark data source for reading Delta checkpoints
from Spark Structured Streaming. It reads the RocksDB checkpoint directories
and exposes offset, metadata, and commits information as SQL-readable data.
"""

import os
import json
import struct
from typing import Dict, List, Optional, Any
from pathlib import Path

from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, 
    TimestampType, BinaryType, MapType
)
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.utils import AnalysisException


class DeltaCheckpointDataSource:
    """
    Custom Spark data source for reading Delta checkpoints.
    
    This data source reads the RocksDB checkpoint directories created by
    Spark Structured Streaming and exposes the checkpoint information
    as SQL-readable data.
    """
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        
    def load(self, path: str) -> DataFrame:
        """
        Load checkpoint data from the specified path.
        
        Args:
            path: Path to the checkpoint directory
            
        Returns:
            DataFrame containing checkpoint information
        """
        checkpoint_path = Path(path)
        
        if not checkpoint_path.exists():
            raise AnalysisException(f"Checkpoint path does not exist: {path}")
            
        # Read different types of checkpoint data
        offset_data = self._read_offset_data(checkpoint_path)
        metadata_data = self._read_metadata_data(checkpoint_path)
        commits_data = self._read_commits_data(checkpoint_path)
        
        # Combine all data
        all_data = []
        
        # Add offset data
        for offset in offset_data:
            all_data.append({
                "type": "offset",
                "source": offset.get("source", ""),
                "partition": offset.get("partition", 0),
                "offset": offset.get("offset", ""),
                "metadata": json.dumps(offset.get("metadata", {})),
                "timestamp": offset.get("timestamp", 0)
            })
            
        # Add metadata data
        for metadata in metadata_data:
            all_data.append({
                "type": "metadata",
                "source": metadata.get("source", ""),
                "partition": metadata.get("partition", 0),
                "offset": "",
                "metadata": json.dumps(metadata),
                "timestamp": metadata.get("timestamp", 0)
            })
            
        # Add commits data
        for commit in commits_data:
            all_data.append({
                "type": "commit",
                "source": commit.get("source", ""),
                "partition": commit.get("partition", 0),
                "offset": commit.get("offset", ""),
                "metadata": json.dumps(commit.get("metadata", {})),
                "timestamp": commit.get("timestamp", 0)
            })
        
        # Create DataFrame
        schema = StructType([
            StructField("type", StringType(), False),
            StructField("source", StringType(), True),
            StructField("partition", LongType(), True),
            StructField("offset", StringType(), True),
            StructField("metadata", StringType(), True),
            StructField("timestamp", LongType(), True)
        ])
        
        return self.spark.createDataFrame(all_data, schema)
    
    def _read_offset_data(self, checkpoint_path: Path) -> List[Dict[str, Any]]:
        """Read offset data from the checkpoint directory."""
        offset_data = []
        offset_dir = checkpoint_path / "offsets"
        
        if not offset_dir.exists():
            return offset_data
            
        try:
            # Read offset files (usually numbered files)
            for offset_file in offset_dir.glob("*"):
                if offset_file.is_file():
                    try:
                        with open(offset_file, 'r') as f:
                            content = f.read().strip()
                            if content:
                                # Parse offset data (format may vary)
                                offset_info = self._parse_offset_content(content)
                                offset_info["source"] = str(offset_file.name)
                                offset_info["timestamp"] = offset_file.stat().st_mtime * 1000
                                offset_data.append(offset_info)
                    except Exception as e:
                        print(f"Warning: Could not read offset file {offset_file}: {e}")
        except Exception as e:
            print(f"Warning: Could not read offset directory: {e}")
            
        return offset_data
    
    def _read_metadata_data(self, checkpoint_path: Path) -> List[Dict[str, Any]]:
        """Read metadata from the checkpoint directory."""
        metadata_data = []
        metadata_dir = checkpoint_path / "metadata"
        
        if not metadata_dir.exists():
            return metadata_data
            
        try:
            # Read metadata files
            for metadata_file in metadata_dir.glob("*"):
                if metadata_file.is_file():
                    try:
                        with open(metadata_file, 'r') as f:
                            content = f.read().strip()
                            if content:
                                metadata_info = self._parse_metadata_content(content)
                                metadata_info["source"] = str(metadata_file.name)
                                metadata_info["timestamp"] = metadata_file.stat().st_mtime * 1000
                                metadata_data.append(metadata_info)
                    except Exception as e:
                        print(f"Warning: Could not read metadata file {metadata_file}: {e}")
        except Exception as e:
            print(f"Warning: Could not read metadata directory: {e}")
            
        return metadata_data
    
    def _read_commits_data(self, checkpoint_path: Path) -> List[Dict[str, Any]]:
        """Read commits data from the checkpoint directory."""
        commits_data = []
        commits_dir = checkpoint_path / "commits"
        
        if not commits_dir.exists():
            return commits_data
            
        try:
            # Read commit files
            for commit_file in commits_dir.glob("*"):
                if commit_file.is_file():
                    try:
                        with open(commit_file, 'r') as f:
                            content = f.read().strip()
                            if content:
                                commit_info = self._parse_commit_content(content)
                                commit_info["source"] = str(commit_file.name)
                                commit_info["timestamp"] = commit_file.stat().st_mtime * 1000
                                commits_data.append(commit_info)
                    except Exception as e:
                        print(f"Warning: Could not read commit file {commit_file}: {e}")
        except Exception as e:
            print(f"Warning: Could not read commits directory: {e}")
            
        return commits_data
    
    def _parse_offset_content(self, content: str) -> Dict[str, Any]:
        """Parse offset content from checkpoint files."""
        try:
            # Try to parse as JSON first
            return json.loads(content)
        except json.JSONDecodeError:
            # If not JSON, try to parse as simple key-value pairs
            result = {}
            lines = content.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    result[key.strip()] = value.strip()
            return result
    
    def _parse_metadata_content(self, content: str) -> Dict[str, Any]:
        """Parse metadata content from checkpoint files."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback to simple parsing
            result = {}
            lines = content.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    result[key.strip()] = value.strip()
            return result
    
    def _parse_commit_content(self, content: str) -> Dict[str, Any]:
        """Parse commit content from checkpoint files."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback to simple parsing
            result = {}
            lines = content.split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    result[key.strip()] = value.strip()
            return result


# Register the data source with Spark
def register_delta_checkpoint_source(spark: SparkSession):
    """
    Register the delta-checkpoint data source with Spark.
    
    Args:
        spark: SparkSession instance
    """
    # This is a simplified registration - in a real implementation,
    # you would need to implement the full DataSourceV2 API
    pass


# Convenience function for easy usage
def read_delta_checkpoint(spark: SparkSession, path: str) -> DataFrame:
    """
    Convenience function to read delta checkpoint data.
    
    Args:
        spark: SparkSession instance
        path: Path to the checkpoint directory
        
    Returns:
        DataFrame containing checkpoint information
    """
    source = DeltaCheckpointDataSource(spark)
    return source.load(path) 