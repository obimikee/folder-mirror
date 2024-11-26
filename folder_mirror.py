import argparse
import os
import shutil
import time
import hashlib
import re
import signal
import sys

def argumentPasser():
    '''
    Parse the command line arguments
    '''
    parser = argparse.ArgumentParser(description='Syncer')
    parser.add_argument('source', type=str, help='Path to the source folder')
    parser.add_argument('replica', type=str, help='Path to the replica folder')
    parser.add_argument('interval', type=int, help='Synchronization interval in seconds')
    parser.add_argument('log_file_path', type=str, help='Path to the log file')

    return parser.parse_args()

"---------------------------------------------------------------------------------------------"

def logger(log_file_path, changes_made, total_folders=None, total_files=None, 
           folders_created=None, folders_removed=None, files_copied=None, files_replaced=None, files_removed=None):
    '''
    Log the message to the log file and print it to the console output.

    Requires: 
    Ensures:
    '''

    # define the colors for console output
    COLOR_RESET = "\033[0m"
    COLOR_CYAN = "\033[36m"
    COLOR_GREEN = "\033[32m"
    COLOR_YELLOW = "\033[33m"
    COLOR_RED = "\033[31m"

    # get the current timestamp
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # identation space for the message output
    ident = "    "

    if changes_made:

        message = (
            f"{COLOR_GREEN}Sync complete: {COLOR_RESET}"
            f"{len(folders_created)} folder(s) created, "
            f"{len(files_copied)} file(s) copied, "
            f"{len(files_replaced)} file(s) replaced, "
            f"{len(folders_removed)} folder(s) removed, "
            f"{len(files_removed)} file(s) removed."
        )

        if folders_created:
            formatted_folders_created = [f"/{folder}" for folder in folders_created]  # add a slash to each folder
            message += f"\n{ident}{COLOR_YELLOW}Folders created:{COLOR_RESET} {', '.join(formatted_folders_created)}"
        if files_copied:
            message += f"\n{ident}{COLOR_YELLOW}Files copied:{COLOR_RESET} {', '.join(files_copied)}"
        if files_replaced:
            message += f"\n{ident}{COLOR_YELLOW}Files replaced:{COLOR_RESET} {', '.join(files_replaced)}"
        if folders_removed:
            formatted_folders_removed = [f"/{folder}" for folder in folders_removed]  # add a slash to each folder
            message += f"\n{ident}{COLOR_RED}Folders removed:{COLOR_RESET} {', '.join(formatted_folders_removed)}"
        if files_removed:
            message += f"\n{ident}{COLOR_RED}Files removed:{COLOR_RESET} {', '.join(files_removed)}"
    
    else:
        message = (
            f"{COLOR_GREEN}Sync complete{COLOR_RESET}: No changes needed - {total_folders} folder(s) and {total_files} file(s) are already in sync."
        )

    formatted_message = f"{COLOR_CYAN}{timestamp}{COLOR_RESET}: {message}"

    # print the message to the console
    print(formatted_message)

    # remove ANSI escape codes from the text
    ansi_escape = re.compile(r'\x1b\[([0-9;]*[mK])')
    log_message = ansi_escape.sub('', formatted_message)

    # ensure the log directory exists if log_file_path is a directory
    if os.path.isdir(log_file_path):
        os.makedirs(log_file_path, exist_ok=True)
        log_file = os.path.join(log_file_path, "log_file.txt")  # default log file in the directory
    else:
        # treat log_file_path as a file
        log_file = log_file_path

    # write the message to the log file
    with open(log_file, 'a') as file:
        file.write(log_message + "\n")

"---------------------------------------------------------------------------------------------"

def signalHandler(signal, frame):
    '''
    
    '''
    print("\nSync process terminated by user.")
    sys.exit(0)

"---------------------------------------------------------------------------------------------"

def getFileHash(file_path):
    '''

    '''
    hasher = hashlib.md5()  # create a new md5 hash object

    with open(file_path, 'rb') as file:
        buf = file.read(65536)  # read the file in chunks of 64KB

        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(65536)
    
    return hasher.hexdigest()  # return the hash of the file

"---------------------------------------------------------------------------------------------"

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

"---------------------------------------------------------------------------------------------"

def syncer(source, replica, log_file_path):
    '''
    Synchronize the source folder with the replica folder.

    Requires:
    Ensures:
    '''
    # counters for total folder and files
    total_folders = 0
    total_files = 0

    # lists for logging affected folders and files
    folders_created = []
    folders_removed = []
    files_copied = []
    files_replaced = []
    files_removed = []

    changes_made = False  # flag to indicate if any changes were made

    os.makedirs(replica, exist_ok=True)  # ensure that the corresponding folder exists in the replica
    
    # sync folders first (including empty folders)
    for root, dirs, files in os.walk(source):

        relative_path = os.path.relpath(root, source)  # calculate the relative path from the source folder         
        replica_path = os.path.join(replica, relative_path)  # calculate the corresponding path in the replica folder

        # create corresponding folders in the replica, even if empty
        if not os.path.exists(replica_path):
            os.makedirs(replica_path)
            folders_created.append(relative_path)
            changes_made = True

    # sync files from source to replica (copy and replace)
    for root, dirs, files in os.walk(source):

        relative_path = os.path.relpath(root, source)  # calculate the relative path from the source          
        replica_path = os.path.join(replica, relative_path)  # calculate the corresponding path in the replica 

        total_folders += len(dirs)
        total_files += len(files)

        # iterate over the files in the source 
        for file in files:
            source_file = os.path.join(root, file)  # path to the source file
            replica_file = os.path.join(replica_path, file)  # path to the replica file

            # copy (in case they dont exist)
            if not os.path.exists(replica_file):
                try:
                    shutil.copy2(source_file, replica_file)  # copy the file (including metadata)
                except Exception as e:
                    print(f"Error copying file '{source_file}' to '{replica_file}': {e}")

                files_copied.append(file)
                changes_made = True

            # replace (in case they are outdated)
            elif not filesAreEqual(source_file, replica_file):
                try:
                    shutil.copy2(source_file, replica_file)  # copy the file (including metadata)
                except Exception as e:
                    print(f"Error replacing file '{source_file}' to '{replica_file}': {e}")

                files_replaced.append(file)
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
                files_removed.append(file)
                changes_made = True

        # remove empty folders from the replica folder that dont exist in the source
        if not os.path.exists(source_path) and root != replica:
            try:
                os.rmdir(root)
                folders_removed.append(relative_path)
                changes_made = True
            except OSError:
                # folder might not be empty, which is fine
                pass
    
    if changes_made:
        logger(log_file_path, changes_made, 
                folders_created=folders_created, 
                folders_removed=folders_removed, 
                files_copied=files_copied, 
                files_replaced=files_replaced, 
                files_removed=files_removed
            )
    else:
        logger(log_file_path, changes_made,
                total_folders=total_folders, total_files=total_files
            )

"---------------------------------------------------------------------------------------------"

def main():
    '''
    Main function to run the syncer function when conditions are met
    '''
    args = argumentPasser()

    # handle the SIGINT signal (Ctrl+C) to terminate the sync process
    signal.signal(signal.SIGINT, signalHandler)

    # check if the source folder exists beCOLOR starting the loop
    if not os.path.exists(args.source):
        print(f"Error: The source folder '{args.source}' does not exist.")
        return

    # check if the replica folder exists beCOLOR starting the loop
    if not os.path.exists(args.replica):
        print(f"Error: The replica folder '{args.replica}' does not exist.")
        return

    # run the syncer function in a loop with the specified interval
    while True:
        try:
            syncer(args.source, args.replica, args.log_file_path)
            time.sleep(args.interval)
        except KeyboardInterrupt:
            break

"---------------------------------------------------------------------------------------------"

if __name__ == "__main__":
    main()  # run the main function