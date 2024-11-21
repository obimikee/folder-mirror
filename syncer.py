import argparse
import os
import shutil

def argument_parser():
    '''
    Parse the command line arguments
    '''
    parser = argparse.ArgumentParser(description='Syncer')
    parser.add_argument('source', type=str, help='Path to the source folder')
    parser.add_argument('replica', type=str, help='Path to the replica folder')
    parser.add_argument('interval', type=int, help='Synchronization interval in seconds')
    parser.add_argument('log_file', type=str, help='Path to the log file')

    return parser.parse_args()


def syncer(source, replica):
    '''
    Synchronize the source folder with the replica folder

    Requires:
    Ensures:
    '''
    
    # iterate over the directories and files in the source folder
    for root, dirs, files in os.walk(source):

        relative_path = os.path.relpath(root, source)  # relative path to the source folder
        replica_path = os.path.join(replica, relative_path)  # path to the replica folder

        # ensure that the corresponding directory exists in the replica
        os.makedirs(replica_path, exist_ok=True)

        # iterate over the files in the source folder
        for file in files:
            source_file = os.path.join(root, file)  # path to the source file
            replica_file = os.path.join(replica, file)  # path to the replica file

            # copy the file to the replica folder if it does not exist or if it is outdated
            if not os.path.exists(replica_file) or os.path.getmtime(source_file) > os.path.getmtime(replica_file):
                shutil.copy2(source_file, replica_file)  # copy the file (including metadata)