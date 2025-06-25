#!/usr/bin/env python3
"""
Demo script for Delta Checkpoints Data Source

This script demonstrates how to use the delta-checkpoints data source
with sample checkpoint data.
"""

import os
import json
import tempfile
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_unixtime

# Import the delta-checkpoints package
import delta_checkpoints


def create_sample_checkpoint_data(checkpoint_path: Path):
    """Create sample checkpoint data for demonstration."""
    
    # Create directory structure
    (checkpoint_path / "offsets").mkdir()
    (checkpoint_path / "metadata").mkdir()
    (checkpoint_path / "commits").mkdir()
    
    # Create sample offset data
    offset_dir = checkpoint_path / "offsets"
    
    # Offset file 0
    offset_data_0 = {
        "partition": 0,
        "offset": "12345",
        "metadata": {
            "topic": "test-topic",
            "partition": 0,
            "leader": "broker-1:9092"
        }
    }
    with open(offset_dir / "0", 'w') as f:
        json.dump(offset_data_0, f)
    
    # Offset file 1
    offset_data_1 = {
        "partition": 1,
        "offset": "67890",
        "metadata": {
            "topic": "test-topic",
            "partition": 1,
            "leader": "broker-2:9092"
        }
    }
    with open(offset_dir / "1", 'w') as f:
        json.dump(offset_data_1, f)
    
    # Create sample metadata data
    metadata_dir = checkpoint_path / "metadata"
    
    metadata_data = {
        "queryName": "test-streaming-query",
        "schema": {
            "type": "struct",
            "fields": [
                {"name": "id", "type": "string", "nullable": True},
                {"name": "value", "type": "integer", "nullable": True},
                {"name": "timestamp", "type": "timestamp", "nullable": True}
            ]
        },
        "config": {
            "checkpointLocation": str(checkpoint_path),
            "trigger.interval": "1 minute",
            "maxOffsetsPerTrigger": 1000
        },
        "sources": ["kafka://broker-1:9092/test-topic"]
    }
    with open(metadata_dir / "0", 'w') as f:
        json.dump(metadata_data, f)
    
    # Create sample commits data
    commits_dir = checkpoint_path / "commits"
    
    # Commit file 0
    commit_data_0 = {
        "batchId": 1,
        "timestamp": 1640995200000,
        "offset": "12345",
        "metadata": {
            "processedRecords": 100,
            "processingTime": 5000,
            "stateStoreMetrics": {
                "numUpdatedStateRows": 50,
                "numRemovedStateRows": 10
            }
        }
    }
    with open(commits_dir / "0", 'w') as f:
        json.dump(commit_data_0, f)
    
    # Commit file 1
    commit_data_1 = {
        "batchId": 2,
        "timestamp": 1640995260000,
        "offset": "67890",
        "metadata": {
            "processedRecords": 150,
            "processingTime": 7500,
            "stateStoreMetrics": {
                "numUpdatedStateRows": 75,
                "numRemovedStateRows": 15
            }
        }
    }
    with open(commits_dir / "1", 'w') as f:
        json.dump(commit_data_1, f)


def main():
    """Main demo function."""
    
    print("=== Delta Checkpoints Data Source Demo ===\n")
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("DeltaCheckpointsDemo") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    
    # Create temporary directory for sample data
    with tempfile.TemporaryDirectory() as temp_dir:
        checkpoint_path = Path(temp_dir) / "checkpoint"
        checkpoint_path.mkdir()
        
        print(f"Creating sample checkpoint data in: {checkpoint_path}")
        create_sample_checkpoint_data(checkpoint_path)
        
        print("\n=== Reading Checkpoint Data ===")
        
        # Method 1: Using the format API (recommended)
        print("\n1. Using spark.read.format('delta-checkpoint').load():")
        df = spark.read.format("delta-checkpoint").load(str(checkpoint_path))
        
        print("DataFrame Schema:")
        df.printSchema()
        
        print("\nAll checkpoint data:")
        df.show(truncate=False)
        
        print("\n=== SQL Queries ===")
        
        # Register the DataFrame as a temp view for SQL queries
        df.createOrReplaceTempView("checkpoint_data")
        
        # Query 1: Get all offset information
        print("\nSQL Query 1: All offset information")
        offset_df = spark.sql("""
            SELECT * FROM checkpoint_data 
            WHERE type = 'offset'
            ORDER BY timestamp DESC
        """)
        offset_df.show(truncate=False)
        
        # Query 2: Get metadata information
        print("\nSQL Query 2: All metadata information")
        metadata_df = spark.sql("""
            SELECT * FROM checkpoint_data 
            WHERE type = 'metadata'
            ORDER BY timestamp DESC
        """)
        metadata_df.show(truncate=False)
        
        # Query 3: Get commit information
        print("\nSQL Query 3: All commit information")
        commit_df = spark.sql("""
            SELECT * FROM checkpoint_data 
            WHERE type = 'commit'
            ORDER BY timestamp DESC
        """)
        commit_df.show(truncate=False)
        
        # Query 4: Convert timestamps to readable format
        print("\nSQL Query 4: Timestamps in readable format")
        readable_df = spark.sql("""
            SELECT 
                type,
                source,
                partition,
                offset,
                metadata,
                from_unixtime(timestamp / 1000) as readable_timestamp
            FROM checkpoint_data 
            ORDER BY timestamp DESC
        """)
        readable_df.show(truncate=False)
        
        # Query 5: Summary statistics
        print("\nSQL Query 5: Summary by type")
        summary_df = spark.sql("""
            SELECT 
                type,
                COUNT(*) as count,
                MIN(from_unixtime(timestamp / 1000)) as earliest_timestamp,
                MAX(from_unixtime(timestamp / 1000)) as latest_timestamp
            FROM checkpoint_data 
            GROUP BY type
            ORDER BY type
        """)
        summary_df.show(truncate=False)
        
        print("\n=== DataFrame API Operations ===")
        
        # Filter operations
        print("\nFilter: Only offset data")
        offset_only = df.filter(col("type") == "offset")
        offset_only.show(truncate=False)
        
        # Select specific columns
        print("\nSelect: Only essential columns")
        essential_cols = df.select("type", "source", "offset", "timestamp")
        essential_cols.show(truncate=False)
        
        # Group by operations
        print("\nGroup by: Count by type")
        type_counts = df.groupBy("type").count()
        type_counts.show()
        
        # Order by operations
        print("\nOrder by: Latest entries first")
        latest_first = df.orderBy(col("timestamp").desc())
        latest_first.show(truncate=False)
        
        print("\n=== Alternative Usage Methods ===")
        
        # Method 2: Using the convenience function
        print("\n2. Using convenience function:")
        df2 = delta_checkpoints.read_delta_checkpoint(spark, str(checkpoint_path))
        df2.show(truncate=False)
        
        # Method 3: Using the class directly
        print("\n3. Using class directly:")
        source = delta_checkpoints.DeltaCheckpointDataSource(spark)
        df3 = source.load(str(checkpoint_path))
        df3.show(truncate=False)
        
        print(f"\nTotal number of records: {df.count()}")
        
        print("\n=== Demo Completed Successfully! ===")
    
    # Stop Spark session
    spark.stop()


if __name__ == "__main__":
    main() 