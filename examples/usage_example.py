"""
Usage Example for Delta Checkpoints Data Source

This example demonstrates how to use the delta-checkpoints data source
to read checkpoint information from Spark Structured Streaming.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_unixtime

# Import the delta-checkpoints package
import delta_checkpoints


def main():
    # Create Spark session
    spark = SparkSession.builder \
        .appName("DeltaCheckpointsExample") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()
    
    # Example checkpoint path (replace with your actual checkpoint path)
    checkpoint_path = "/path/to/your/checkpoint/directory"
    
    print("=== Reading Delta Checkpoint Data ===")
    
    # Method 1: Using the format API (recommended)
    print("\n1. Using spark.read.format('delta-checkpoint').load():")
    df = spark.read.format("delta-checkpoint").load(checkpoint_path)
    
    # Show the data
    df.show(truncate=False)
    
    # Method 2: Using the convenience function
    print("\n2. Using convenience function:")
    df2 = delta_checkpoints.read_delta_checkpoint(spark, checkpoint_path)
    df2.show(truncate=False)
    
    # Method 3: Using the class directly
    print("\n3. Using class directly:")
    source = delta_checkpoints.DeltaCheckpointDataSource(spark)
    df3 = source.load(checkpoint_path)
    df3.show(truncate=False)
    
    print("\n=== SQL Queries on Checkpoint Data ===")
    
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
    
    print("\n=== Schema Information ===")
    print("DataFrame Schema:")
    df.printSchema()
    
    print(f"\nTotal number of records: {df.count()}")
    
    # Stop Spark session
    spark.stop()


if __name__ == "__main__":
    main() 