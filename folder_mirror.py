import argparse
import os
import shutil
import time
import hashlib

def argumentPasser():
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

    # get the current timestamp in the format 'YYYY-MM-DD HH:MM:SS'
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    formatted_message = f"[{timestamp}]: {message}"  # format the message
    print(formatted_message)  # print the formatted message to the console output

    # write the message to the log file
    with open(log_file, 'a') as file:
        file.write(formatted_message + "\n")

def getFileHash(file_path):
    '''

    '''
    hasher = hashlib.md5()  # create a new md5 hash object

    with open(file_path, 'rb') as file:
        buf = file.read()  # read the file in chunks

        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read()
    
    return hasher.hexdigest()  # return the hash of the file

def filesAreEqual(file1, file2):
    '''
    Compare two files.
    First by size, then by hash if sizes match.
    '''
    # compare the sizes of the files
    if os.path.getsize(file1) != os.path.getsize(file2):
        return False

    # compare the hashes of the files
    return getFileHash(file1) == getFileHash(file2)


def syncer(source, replica, log_file):
    '''
    Synchronize the source folder with the replica folder.

    Requires:
    Ensures:
    '''
    changes_made = False  # flag to indicate if any changes were made

    os.makedirs(replica, exist_ok=True)  # ensure that the corresponding folder exists in the replica
    
    # sync folders first (including empty folders)
    for root, dirs, files in os.walk(source):

        relative_path = os.path.relpath(root, source)  # calculate the relative path from the source folder         
        replica_path = os.path.join(replica, relative_path)  # calculate the corresponding path in the replica folder

        # create corresponding folders in the replica, even if empty
        if not os.path.exists(replica_path):
            os.makedirs(replica_path)
            logger(log_file, f"Created folder '{os.path.basename(replica_path)}' in '{replica_path}'.")
            changes_made = True

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
                logger(log_file, f"Copied file '{file}' to '{replica_path}'.")
                changes_made = True

            # update (in case they are outdated)
            elif not filesAreEqual(source_file, replica_file):
                shutil.copy2(source_file, replica_file)  # copy the file (including metadata)
                logger(log_file, f"Updated file '{file}' in '{replica_path}'.")
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
                logger(log_file, f"Removed file '{file}' from '{replica_path}'.")
                changes_made = True

        # remove empty folders from the replica folder that dont exist in the source
        if not os.path.exists(source_path) and root != replica:
            try:
                os.rmdir(root)
                logger(log_file, f"Removed folder '{relative_path}' from '{replica_path}'.")
                changes_made = True
            except OSError:
                # folder might not be empty, which is fine
                pass
    
    # log a message if no files were copied or removed
    if not changes_made:
        logger(log_file, f"No changes were made. Both folders are already in sync.")

        """
        --- uncomment the follwing line to include the folders path in the log message ---
        --- was commented out to avoid redundancy and easier to read ---

        logger(log_file, f"No changes were made. Both folders '{source}' and '{replica}' are already in sync.")
        """

def main():
    '''
    Main function to run the syncer function when conditions are met
    '''
    args = argumentPasser()

    # check if the source folder exists before starting the loop
    if not os.path.exists(args.source):
        print(f"Error: The source folder '{args.source}' does not exist.")
        return

    # check if the replica folder exists before starting the loop
    if not os.path.exists(args.replica):
        print(f"Error: The replica folder '{args.replica}' does not exist.")
        return

    # run the syncer function in a loop with the specified interval
    while True:
        syncer(args.source, args.replica, args.log_file)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()  # run the main function