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

    timestamp = time.strftime("%H:%M:%S", time.localtime())  # get the current timestamp in the format 'HH:MM:SS'

    """
    --- uncomment the following lines to include the date in the timestamp ---

    # get the current timestamp in the format 'YYYY-MM-DD HH:MM:SS'
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    """

    formatted_message = f"[{timestamp}]: {message}"  # format the message
    print(formatted_message)  # print the formatted message to the console output

    # write the message to the log file
    with open(log_file, 'a') as file:
        file.write(formatted_message + "\n")

def syncer(source, replica, log_file):
    '''
    Synchronize the source folder with the replica folder

    Requires:
    Ensures:
    '''
    changes_made = False  # flag to indicate if any changes were made

    os.makedirs(replica_path, exist_ok=True)  # ensure that the corresponding directory exists in the replica
    
    # sync folders first (including empty folders)
    for root, dirs, files in os.walk(source):

        relative_path = os.path.relpath(root, source)  # calculate the relative path from the source folder         
        replica_path = os.path.join(replica, relative_path)  # calculate the corresponding path in the replica folder

        # create corresponding folders in the replica, even if empty
        if not os.path.exists(replica_path):
            os.makedirs(replica_path)
            logger(log_file, f"Directory '{replica_path}' successfully created in '{replica}'.")


    # sync files from source to replica (copy and update)
    for root, dirs, files in os.walk(source):

        relative_path = os.path.relpath(root, source)  # calculate the relative path from the source          
        replica_path = os.path.join(replica, relative_path)  # calculate the corresponding path in the replica 

        # iterate over the files in the source 
        for file in files:
            source_file = os.path.join(root, file)  # path to the source file
            replica_file = os.path.join(replica_path, file)  # path to the replica file

            # copy (in case they dont exist)
            if not os.path.exists(replica_file): 
                shutil.copy2(source_file, replica_file)  # copy the file (including metadata)
                logger(log_file, f"File '{file}' successfully copied to '{replica}'.")
                changes_made = True

            # update (in case they are outdated)
            elif os.path.getmtime(source_file) > os.path.getmtime(replica_file):
                shutil.copy2(source_file, replica_file)  # copy the file (including metadata)
                logger(log_file, f"File '{file}' successfully updated on '{replica}'.")
                changes_made = True

    # remove files from replica that dont exist in source
    for root, dirs, files, in os.walk(replica):

        relative_path = os.path.relpath(root, replica)  # calculate the relative path from the replica   
        source_path = os.path.join(source, relative_path)  # calculate the corresponding path in the source 

        # iterate over the files in the replica
        for file in files:
            replica_file = os.path.join(root, file)  # path to the replica file
            source_file = os.path.join(source_path, file)  # path to the corresponding source file

            # remove the file from the replica if it does not exist in the source
            if not os.path.exists(source_file):
                os.remove(replica_file)
                logger(log_file, f"File '{file}' removed from '{replica}' successfully.")
                changes_made = True

        # remove empty directories from the replica folder that dont exist in the source
        if not os.listdir(root) and root != replica:
            os.rmdir(root)
            logger(log_file, f"Directory '{root}' removed from '{replica}' successfully.")
            changes_made = True     
    
    # log a message if no files were copied or removed
    if not (changes_made or changes_made):
        logger(log_file, f"No changes were made. Both folders are already in sync.")

        """
        --- uncomment the follwing line to include the folders path in the log message ---
        --- was commented out to avoid redundancy and easier to read ---

        logger(log_file, f"No changes were made. Both folders '{source}' and '{replica}' are already in sync.")
        """


if __name__ == "__main__":
    args = argument_parser()

    # check if the source folder exists before starting the loop
    if not os.path.exists(args.source):
        print(f"Error: The source folder '{args.source}' does not exist.")

    # check if the replica folder exists before starting the loop
    elif not os.path.exists(args.replica):
        print(f"Error: The replica folder '{args.replica}' does not exist.")
    else:
        # Run the syncer function in a loop with the specified interval
        while True:
            syncer(args.source, args.replica, args.log_file)
            time.sleep(args.interval)