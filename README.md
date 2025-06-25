# Delta Checkpoints Data Source for Apache Spark

[![PyPI version](https://badge.fury.io/py/delta-checkpoints.svg)](https://badge.fury.io/py/delta-checkpoints)
[![Python versions](https://img.shields.io/pypi/pyversions/delta-checkpoints.svg)](https://pypi.org/project/delta-checkpoints/)
[![License](https://img.shields.io/pypi/l/delta-checkpoints.svg)](https://pypi.org/project/delta-checkpoints/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A custom Spark data source for reading Delta checkpoints from Spark Structured Streaming. This data source reads the RocksDB checkpoint directories and exposes offset, metadata, and commits information as SQL-readable data.

## 🚀 Quick Start

```bash
pip install delta-checkpoints
```

```python
from pyspark.sql import SparkSession
import delta_checkpoints

# Create Spark session
spark = SparkSession.builder \
    .appName("DeltaCheckpointsExample") \
    .getOrCreate()

# Read checkpoint data
df = spark.read.format("delta-checkpoint").load("/path/to/checkpoint")
df.show()
```

## 📖 Overview

Spark Structured Streaming uses RocksDB as the checkpoint provider, which creates multiple directories under the checkpoint path:
- `/path/to/checkpoint/offsets/` - Contains offset information
- `/path/to/checkpoint/metadata/` - Contains metadata information  
- `/path/to/checkpoint/commits/` - Contains commit information

This data source makes it easy to read and analyze this checkpoint information using Spark SQL and DataFrame APIs.

## ✨ Features

- **🔌 Easy Integration**: Use familiar `spark.read.format("delta-checkpoint").load()` syntax
- **📊 SQL Support**: Query checkpoint data using Spark SQL
- **📁 Multiple Data Types**: Read offset, metadata, and commit information
- **🔄 Flexible Parsing**: Handles various checkpoint file formats
- **🛡️ Error Handling**: Graceful handling of missing or corrupted checkpoint files
- **⚡ Performance**: Optimized for large checkpoint datasets

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install delta-checkpoints
```

### From Source

```bash
git clone https://github.com/yourusername/delta-checkpoints.git
cd delta-checkpoints
pip install -e .
```

### Requirements

- Python 3.7+
- PySpark 3.0.0+
- py4j 0.10.9+

## 🎯 Usage Examples

### Method 1: Using Format API (Recommended)

```python
# Read checkpoint data
df = spark.read.format("delta-checkpoint").load("/path/to/checkpoint")

# Show all data
df.show(truncate=False)
```

### Method 2: Using Convenience Function

```python
import delta_checkpoints

df = delta_checkpoints.read_delta_checkpoint(spark, "/path/to/checkpoint")
df.show()
```

### Method 3: Using Class Directly

```python
from delta_checkpoints import DeltaCheckpointDataSource

source = DeltaCheckpointDataSource(spark)
df = source.load("/path/to/checkpoint")
df.show()
```

## 📋 Data Schema

The data source returns a DataFrame with the following schema:

```python
StructType([
    StructField("type", StringType(), False),      # "offset", "metadata", or "commit"
    StructField("source", StringType(), True),     # Source file name
    StructField("partition", LongType(), True),    # Partition number
    StructField("offset", StringType(), True),     # Offset value
    StructField("metadata", StringType(), True),   # JSON string of metadata
    StructField("timestamp", LongType(), True)     # Unix timestamp in milliseconds
])
```

## 🔍 SQL Queries

Register the DataFrame as a temp view and use SQL:

```python
# Register as temp view
df.createOrReplaceTempView("checkpoint_data")

# Query offset information
offset_df = spark.sql("""
    SELECT * FROM checkpoint_data 
    WHERE type = 'offset'
    ORDER BY timestamp DESC
""")

# Query metadata information
metadata_df = spark.sql("""
    SELECT * FROM checkpoint_data 
    WHERE type = 'metadata'
    ORDER BY timestamp DESC
""")

# Query commit information
commit_df = spark.sql("""
    SELECT * FROM checkpoint_data 
    WHERE type = 'commit'
    ORDER BY timestamp DESC
""")

# Convert timestamps to readable format
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
```

## 🛠️ DataFrame API Operations

```python
# Filter by type
offset_only = df.filter(col("type") == "offset")

# Select specific columns
essential_cols = df.select("type", "source", "offset", "timestamp")

# Group by operations
type_counts = df.groupBy("type").count()

# Order by timestamp
latest_first = df.orderBy(col("timestamp").desc())
```

## 📁 Checkpoint Directory Structure

The data source expects a checkpoint directory structure like this:

```
/path/to/checkpoint/
├── offsets/
│   ├── 0
│   ├── 1
│   └── ...
├── metadata/
│   ├── 0
│   ├── 1
│   └── ...
└── commits/
    ├── 0
    ├── 1
    └── ...
```

## 📚 Understanding Checkpoint Data

Based on the [Spark Structured Streaming Checkpointing article](https://medium.com/@alonisser/spark-structured-streaming-checkpointing-2dbb2b2afdd0):

### Offsets
- Contains the current offset for each partition
- Used to track progress in the stream
- Essential for fault tolerance and recovery

### Metadata
- Contains configuration and state information
- Includes query metadata, schema information, and other settings
- Used for query recovery and state management

### Commits
- Contains information about committed batches
- Tracks which data has been processed
- Used for exactly-once processing guarantees

## 🛡️ Error Handling

The data source includes robust error handling:

- **Missing Directories**: Gracefully handles missing offset, metadata, or commits directories
- **Corrupted Files**: Skips files that cannot be read and logs warnings
- **Invalid Formats**: Attempts multiple parsing strategies for different file formats
- **Path Validation**: Validates checkpoint path existence before processing

## ⚡ Performance Considerations

- **Lazy Evaluation**: Data is only read when actions are triggered
- **Partitioning**: Consider repartitioning large checkpoint datasets for better performance
- **Caching**: Cache frequently accessed checkpoint data using `df.cache()`
- **Filtering**: Use filters early to reduce data volume

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=delta_checkpoints

# Run specific test file
pytest tests/test_delta_checkpoint_source.py

# Run tests in parallel
pytest -n auto
```

### Code Formatting

```bash
# Format code with black
black .

# Check code style with flake8
flake8 delta_checkpoints tests

# Type checking with mypy
mypy delta_checkpoints
```

### Running the Demo

```bash
# Run the interactive demo
python demo.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Path Not Found**: Ensure the checkpoint path exists and is accessible
2. **Permission Denied**: Check file permissions on the checkpoint directory
3. **Empty Results**: Verify that the checkpoint directory contains data
4. **Parsing Errors**: Check the format of checkpoint files

### Debug Mode

Enable debug logging to see detailed information about file reading:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Format code: `black .`
6. Check types: `mypy delta_checkpoints`
7. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Apache Spark](https://spark.apache.org/) for the amazing streaming framework
- [PySpark Data Sources Example](https://github.com/allisonwang-db/pyspark-data-sources) for the inspiration
- [Spark Structured Streaming Checkpointing](https://medium.com/@alonisser/spark-structured-streaming-checkpointing-2dbb2b2afdd0) for the detailed explanation

## 📞 Support

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/delta-checkpoints/issues)
- 📖 Documentation: [GitHub README](https://github.com/yourusername/delta-checkpoints#readme)

---

**Made with ❤️ for the Apache Spark community** 