# folder-mirror 📂

A Python script for one-way folder synchronization, developed as part of a test task for a job application at Veeam Software.

## Features ✨
- One-way synchronization from source to replica folder
- Exact mirror of source folder contents
- Detailed logging of file and folder operations
  - Console output with color-coded messages
  - Persistent log file tracking
- Continuous synchronization with custom intervals
- Keyboard interrupt (Ctrl+C) support

## Prerequisites 🛠
- Python 3.7+
- Standard Python libraries (no additional installations required)

## Installation
1. Clone the repository
2. Ensure you have Python 3.7 or higher installed

## Usage 🚀
```bash
python3 folder-sync.py <source_folder> <replica_folder> <interval_seconds> <log_file_path>
```

- source_folder: Path to the source directory
- replica_folder: Path to the replica directory
- interval_seconds:  Synchronization interval in seconds (the frequency at which synchronization happens).
- log_file_path: Path to the log file or log file name where synchronization operations will be recorded.

## Usage Example

```bash
python folder-sync.py /path/to/source /path/to/replica 60 /path/to/log_file.txt
```

## Log Example


## Video Demo


#### Created by Miguel Lages