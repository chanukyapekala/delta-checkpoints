"""
Tests for Delta Checkpoint Data Source

This module contains comprehensive tests for the delta checkpoint data source
to ensure it correctly reads and parses checkpoint information.
"""

import os
import json
import tempfile
import shutil
import pytest
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, LongType

from delta_checkpoints.delta_checkpoint_source import DeltaCheckpointDataSource


@pytest.fixture(scope="session")
def spark_session():
    """Create a Spark session for testing."""
    spark = SparkSession.builder \
        .appName("DeltaCheckpointTest") \
        .master("local[2]") \
        .config("spark.sql.adaptive.enabled", "false") \
        .getOrCreate()
    
    yield spark
    
    spark.stop()


@pytest.fixture(scope="session")
def delta_checkpoint_source(spark_session):
    """Create a DeltaCheckpointDataSource instance for testing."""
    return DeltaCheckpointDataSource(spark_session)


@pytest.fixture
def temp_checkpoint_dir():
    """Create a temporary checkpoint directory for testing."""
    test_dir = tempfile.mkdtemp()
    checkpoint_path = Path(test_dir)
    
    # Create checkpoint directory structure
    (checkpoint_path / "offsets").mkdir()
    (checkpoint_path / "metadata").mkdir()
    (checkpoint_path / "commits").mkdir()
    
    yield checkpoint_path
    
    # Cleanup
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


class TestDeltaCheckpointDataSource:
    """Test cases for DeltaCheckpointDataSource."""
    
    def test_load_nonexistent_path(self, delta_checkpoint_source):
        """Test loading from non-existent path."""
        with pytest.raises(Exception):
            delta_checkpoint_source.load("/nonexistent/path")
    
    def test_load_empty_checkpoint(self, delta_checkpoint_source, temp_checkpoint_dir):
        """Test loading empty checkpoint directory."""
        df = delta_checkpoint_source.load(str(temp_checkpoint_dir))
        
        # Should return empty DataFrame with correct schema
        assert df.count() == 0
        assert isinstance(df.schema, StructType)
        
        # Check schema fields
        expected_fields = ["type", "source", "partition", "offset", "metadata", "timestamp"]
        actual_fields = [field.name for field in df.schema.fields]
        assert actual_fields == expected_fields
    
    def test_load_with_offset_data(self, delta_checkpoint_source, temp_checkpoint_dir):
        """Test loading checkpoint with offset data."""
        # Create offset files
        offset_dir = temp_checkpoint_dir / "offsets"
        
        # Create JSON offset file
        offset_data1 = {
            "partition": 0,
            "offset": "12345",
            "metadata": {"topic": "test-topic", "partition": 0}
        }
        with open(offset_dir / "0", 'w') as f:
            json.dump(offset_data1, f)
        
        # Create simple key-value offset file
        with open(offset_dir / "1", 'w') as f:
            f.write("partition=1\noffset=67890\ntopic=test-topic-2")
        
        df = delta_checkpoint_source.load(str(temp_checkpoint_dir))
        
        # Should have 2 offset records
        offset_df = df.filter(df.type == "offset")
        assert offset_df.count() == 2
        
        # Check first record
        first_row = offset_df.first()
        assert first_row.type == "offset"
        assert first_row.source == "0"
        assert first_row.partition == 0
        assert first_row.offset == "12345"
        
        # Check metadata is JSON string
        metadata = json.loads(first_row.metadata)
        assert metadata["topic"] == "test-topic"
    
    def test_load_with_metadata_data(self, delta_checkpoint_source, temp_checkpoint_dir):
        """Test loading checkpoint with metadata data."""
        # Create metadata files
        metadata_dir = temp_checkpoint_dir / "metadata"
        
        metadata_data = {
            "queryName": "test-query",
            "schema": {"type": "struct", "fields": []},
            "config": {"checkpointLocation": "/tmp/checkpoint"}
        }
        with open(metadata_dir / "0", 'w') as f:
            json.dump(metadata_data, f)
        
        df = delta_checkpoint_source.load(str(temp_checkpoint_dir))
        
        # Should have 1 metadata record
        metadata_df = df.filter(df.type == "metadata")
        assert metadata_df.count() == 1
        
        # Check metadata record
        row = metadata_df.first()
        assert row.type == "metadata"
        assert row.source == "0"
        
        # Check metadata content
        metadata = json.loads(row.metadata)
        assert metadata["queryName"] == "test-query"
    
    def test_load_with_commits_data(self, delta_checkpoint_source, temp_checkpoint_dir):
        """Test loading checkpoint with commits data."""
        # Create commits files
        commits_dir = temp_checkpoint_dir / "commits"
        
        commit_data = {
            "batchId": 1,
            "timestamp": 1640995200000,
            "offset": "12345",
            "metadata": {"processedRecords": 100}
        }
        with open(commits_dir / "0", 'w') as f:
            json.dump(commit_data, f)
        
        df = delta_checkpoint_source.load(str(temp_checkpoint_dir))
        
        # Should have 1 commit record
        commit_df = df.filter(df.type == "commit")
        assert commit_df.count() == 1
        
        # Check commit record
        row = commit_df.first()
        assert row.type == "commit"
        assert row.source == "0"
        assert row.offset == "12345"
        
        # Check metadata content
        metadata = json.loads(row.metadata)
        assert metadata["processedRecords"] == 100
    
    def test_load_complete_checkpoint(self, delta_checkpoint_source, temp_checkpoint_dir):
        """Test loading complete checkpoint with all data types."""
        # Create offset data
        offset_dir = temp_checkpoint_dir / "offsets"
        with open(offset_dir / "0", 'w') as f:
            json.dump({"partition": 0, "offset": "12345"}, f)
        
        # Create metadata data
        metadata_dir = temp_checkpoint_dir / "metadata"
        with open(metadata_dir / "0", 'w') as f:
            json.dump({"queryName": "test-query"}, f)
        
        # Create commits data
        commits_dir = temp_checkpoint_dir / "commits"
        with open(commits_dir / "0", 'w') as f:
            json.dump({"batchId": 1, "offset": "12345"}, f)
        
        df = delta_checkpoint_source.load(str(temp_checkpoint_dir))
        
        # Should have 3 total records
        assert df.count() == 3
        
        # Check each type
        assert df.filter(df.type == "offset").count() == 1
        assert df.filter(df.type == "metadata").count() == 1
        assert df.filter(df.type == "commit").count() == 1
    
    def test_parse_invalid_json(self, delta_checkpoint_source, temp_checkpoint_dir):
        """Test parsing invalid JSON content."""
        # Create file with invalid JSON
        offset_dir = temp_checkpoint_dir / "offsets"
        with open(offset_dir / "0", 'w') as f:
            f.write("invalid json content")
        
        df = delta_checkpoint_source.load(str(temp_checkpoint_dir))
        
        # Should still create a record with parsed key-value pairs
        offset_df = df.filter(df.type == "offset")
        assert offset_df.count() == 1
        
        row = offset_df.first()
        assert row.type == "offset"
    
    def test_missing_directories(self, delta_checkpoint_source, temp_checkpoint_dir):
        """Test handling of missing checkpoint subdirectories."""
        # Remove some directories
        shutil.rmtree(temp_checkpoint_dir / "metadata")
        shutil.rmtree(temp_checkpoint_dir / "commits")
        
        # Should still work with only offsets
        offset_dir = temp_checkpoint_dir / "offsets"
        with open(offset_dir / "0", 'w') as f:
            json.dump({"partition": 0, "offset": "12345"}, f)
        
        df = delta_checkpoint_source.load(str(temp_checkpoint_dir))
        
        # Should have 1 offset record
        assert df.count() == 1
        assert df.filter(df.type == "offset").count() == 1
    
    def test_sql_queries(self, delta_checkpoint_source, temp_checkpoint_dir, spark_session):
        """Test SQL queries on checkpoint data."""
        # Create test data
        offset_dir = temp_checkpoint_dir / "offsets"
        with open(offset_dir / "0", 'w') as f:
            json.dump({"partition": 0, "offset": "12345"}, f)
        
        metadata_dir = temp_checkpoint_dir / "metadata"
        with open(metadata_dir / "0", 'w') as f:
            json.dump({"queryName": "test-query"}, f)
        
        df = delta_checkpoint_source.load(str(temp_checkpoint_dir))
        
        # Register as temp view
        df.createOrReplaceTempView("checkpoint_data")
        
        # Test SQL query
        result = spark_session.sql("""
            SELECT type, COUNT(*) as count 
            FROM checkpoint_data 
            GROUP BY type
        """)
        
        # Should have 2 types
        assert result.count() == 2
        
        # Check results
        rows = result.collect()
        types = [row.type for row in rows]
        assert "offset" in types
        assert "metadata" in types
    
    def test_dataframe_operations(self, delta_checkpoint_source, temp_checkpoint_dir):
        """Test DataFrame API operations."""
        # Create test data
        offset_dir = temp_checkpoint_dir / "offsets"
        with open(offset_dir / "0", 'w') as f:
            json.dump({"partition": 0, "offset": "12345"}, f)
        
        df = delta_checkpoint_source.load(str(temp_checkpoint_dir))
        
        # Test filter
        offset_df = df.filter(df.type == "offset")
        assert offset_df.count() == 1
        
        # Test select
        selected_df = df.select("type", "source")
        assert len(selected_df.columns) == 2
        
        # Test order by
        ordered_df = df.orderBy(df.timestamp.desc())
        assert ordered_df.count() == 1


# Additional pytest-style tests
def test_spark_integration(spark_session, temp_checkpoint_dir):
    """Test the Spark integration module."""
    # Import the integration module
    from delta_checkpoints import spark_integration
    
    # Create some test data
    offset_dir = temp_checkpoint_dir / "offsets"
    with open(offset_dir / "0", 'w') as f:
        json.dump({"partition": 0, "offset": "12345"}, f)
    
    # Test the format API
    df = spark_session.read.format("delta-checkpoint").load(str(temp_checkpoint_dir))
    assert df.count() == 1
    assert df.first().type == "offset"


def test_convenience_function(spark_session, temp_checkpoint_dir):
    """Test the convenience function."""
    from delta_checkpoints import read_delta_checkpoint
    
    # Create some test data
    offset_dir = temp_checkpoint_dir / "offsets"
    with open(offset_dir / "0", 'w') as f:
        json.dump({"partition": 0, "offset": "12345"}, f)
    
    # Test the convenience function
    df = read_delta_checkpoint(spark_session, str(temp_checkpoint_dir))
    assert df.count() == 1
    assert df.first().type == "offset" 