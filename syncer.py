import argparse
import os
import shutil
import time

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

def logger(log_file, message):
    '''
    Log the message to the log file

    Requires:
    Ensures:
    '''

    # get the current timestamp in the format 'HH:MM:SS'
    timestamp = time.strftime("%H:%M:%S", time.localtime())

    """
    --- uncomment the following lines to include the date in the timestamp ---

    # get the current timestamp in the format 'YYYY-MM-DD HH:MM:SS'
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    """
    # format the message
    formatted_message = f"[{timestamp}]: {message}"
    
    # print the formatted message to the console output
    print(formatted_message)

    # write the message to the log file
    with open(log_file, 'a') as file:
        file.write(formatted_message + "\n")

def syncer(source, replica, log_file):
    '''
    Synchronize the source folder with the replica folder

    Requires:
    Ensures:
    '''

    files_coppied = False  # flag to indicate if any files were copied
    
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
                logger(log_file, f"File '{file}' copied to '{replica}' successfully.")
                files_coppied = True  # set the flag to True

    
    # log a message if no files were copied
    if not files_coppied:
        logger(log_file, f"Both folders are already in sync. No changes were made.")

        """
        --- uncomment the follwing line to include the folders path in the log message ---
        --- was commented out to avoid redundancy and easier to read ---

        logger(log_file, f"Both folders '{source}' and '{replica}' are already in sync. No changes were made.")
        """


if __name__ == "__main__":
    args = argument_parser()
    
    while True:
        syncer(args.source, args.replica, args.log_file)
        time.sleep(args.interval)