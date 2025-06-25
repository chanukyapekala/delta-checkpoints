"""
Spark DataSourceV2 Integration for Delta Checkpoints

This module provides the proper integration with Spark's DataSourceV2 API
to enable the spark.read.format("delta-checkpoint").load() syntax.
"""

from typing import Optional, Dict, Any
from pyspark.sql.types import StructType
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.utils import AnalysisException

from .delta_checkpoint_source import DeltaCheckpointDataSource


class DeltaCheckpointDataSourceV2:
    """
    DataSourceV2 implementation for Delta Checkpoints.
    
    This class implements the Spark DataSourceV2 API to enable
    spark.read.format("delta-checkpoint").load() syntax.
    """
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self._source = DeltaCheckpointDataSource(spark)
    
    def load(self, path: Optional[str] = None, **options: Dict[str, Any]) -> DataFrame:
        """
        Load checkpoint data using DataSourceV2 API.
        
        Args:
            path: Path to the checkpoint directory
            **options: Additional options
            
        Returns:
            DataFrame containing checkpoint information
        """
        if not path:
            raise AnalysisException("Path must be specified for delta-checkpoint data source")
        
        return self._source.load(path)
    
    def schema(self, path: Optional[str] = None, **options: Dict[str, Any]) -> StructType:
        """
        Get the schema for the checkpoint data.
        
        Args:
            path: Path to the checkpoint directory
            **options: Additional options
            
        Returns:
            Schema of the checkpoint data
        """
        return self._source.load(path).schema


# Global registry for the data source
_delta_checkpoint_source = None


def get_delta_checkpoint_source(spark: SparkSession) -> DeltaCheckpointDataSourceV2:
    """
    Get or create the delta checkpoint data source instance.
    
    Args:
        spark: SparkSession instance
        
    Returns:
        DeltaCheckpointDataSourceV2 instance
    """
    global _delta_checkpoint_source
    if _delta_checkpoint_source is None:
        _delta_checkpoint_source = DeltaCheckpointDataSourceV2(spark)
    return _delta_checkpoint_source


# Monkey patch SparkSession to add delta-checkpoint format support
def _patch_spark_session():
    """
    Patch SparkSession to add delta-checkpoint format support.
    
    This function adds a custom format handler to Spark's DataFrameReader
    to enable spark.read.format("delta-checkpoint").load() syntax.
    """
    original_load = None
    
    def custom_load(self, path=None, format=None, schema=None, **options):
        if format == "delta-checkpoint":
            # Get the SparkSession from the DataFrameReader
            spark = self._spark
            source = get_delta_checkpoint_source(spark)
            return source.load(path, **options)
        else:
            # Call the original load method
            return original_load(self, path, format, schema, **options)
    
    # Store the original load method
    from pyspark.sql.readwriter import DataFrameReader
    original_load = DataFrameReader.load
    
    # Replace with our custom implementation
    DataFrameReader.load = custom_load


# Auto-patch when module is imported
_patch_spark_session() 