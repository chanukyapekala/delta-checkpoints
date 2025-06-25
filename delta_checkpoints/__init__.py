"""
Delta Checkpoints Data Source for Apache Spark

This package provides a custom data source for reading Delta checkpoints
from Spark Structured Streaming, exposing offset, metadata, and commits
information as SQL-readable data.
"""

from .delta_checkpoint_source import DeltaCheckpointDataSource
from .spark_integration import DeltaCheckpointDataSourceV2

# Import the integration module to enable spark.read.format("delta-checkpoint").load()
from . import spark_integration

# Convenience function for easy usage
def read_delta_checkpoint(spark, path):
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

__version__ = "0.1.0"
__all__ = [
    "DeltaCheckpointDataSource", 
    "DeltaCheckpointDataSourceV2",
    "read_delta_checkpoint"
] 