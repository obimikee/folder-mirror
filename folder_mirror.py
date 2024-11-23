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
    parser.add_argument('log_file_path', type=str, help='Path to the log file')

    return parser.parse_args()

"---------------------------------------------------------------------------------------------"

def logger(log_file_path, console_message=None, log_message=None, folders_created=None, folders_removed=None, files_copied=None, files_replaced=None, files_removed=None):
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

    # build the summary message for the console output
    if not console_message:
        console_message = (
            f"{COLOR_GREEN}Sync complete:{COLOR_RESET} "
            f"{len(folders_created)} folder(s) created, "
            f"{len(files_copied)} file(s) copied, "
            f"{len(files_replaced)} file(s) replaced, "
            f"{len(folders_removed)} folder(s) removed, "
            f"{len(files_removed)} file(s) removed."
        )
    
    indent = "    "
    if folders_created:
        formatted_folders_created = [f"/{folder}" for folder in folders_created]  # add a slash to each folder
        console_message += f"\n{indent}{COLOR_YELLOW}Folders created:{COLOR_RESET} {', '.join(formatted_folders_created)}"
    if files_copied:
        console_message += f"\n{indent}{COLOR_YELLOW}Files copied:{COLOR_RESET} {', '.join(files_copied)}"
    if files_replaced:
        console_message += f"\n{indent}{COLOR_YELLOW}Files replaced:{COLOR_RESET} {', '.join(files_replaced)}"
    if folders_removed:
        formatted_folders_removed = [f"/{folder}" for folder in folders_removed]  # add a slash to each folder
        console_message += f"\n{indent}{COLOR_RED}Folders removed:{COLOR_RESET} {', '.join(formatted_folders_removed)}"
    if files_removed:
        console_message += f"\n{indent}{COLOR_RED}Files removed:{COLOR_RESET} {', '.join(files_removed)}"
        
    formatted_console_message = f"{COLOR_CYAN}{timestamp}{COLOR_RESET}: {console_message}"  # add color to the timestamp
    print(formatted_console_message)  # print the message to the console


    # ensure the log directory exists
    os.makedirs(log_file_path, exist_ok=True)

    # build the summary message for the console output
    if not log_message:
        log_message = (
            f"Sync complete: "
            f"{len(folders_created)} folder(s) created, "
            f"{len(files_copied)} file(s) copied, "
            f"{len(files_replaced)} file(s) replaced, "
            f"{len(folders_removed)} folder(s) removed, "
            f"{len(files_removed)} file(s) removed."
        )
    
    indent = "    "
    if folders_created:
        formatted_folders_created = [f"/{folder}" for folder in folders_created]  # add a slash to each folder
        log_message += f"\n{indent}Folders created: {', '.join(formatted_folders_created)}"
    if files_copied:
        log_message += f"\n{indent}Files copied: {', '.join(files_copied)}"
    if files_replaced:
        log_message += f"\n{indent}Files replaced: {', '.join(files_replaced)}"
    if folders_removed:
        formatted_folders_removed = [f"/{folder}" for folder in folders_removed]  # add a slash to each folder
        log_message += f"\n{indent}Folders removed: {', '.join(formatted_folders_removed)}"
    if files_removed:
        log_message += f"\n{indent}Files removed: {', '.join(files_removed)}"

    formatted_log_message = f"{timestamp}: {log_message}"

    # write the message to the log file
    with open(f"{log_file_path}/logs.txt", 'a') as file:
        file.write(formatted_log_message + "\n")

"---------------------------------------------------------------------------------------------"

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
                shutil.copy2(source_file, replica_file)  # copy the file (including metadata)
                files_copied.append(file)
                changes_made = True

            # replace (in case they are outdated)
            elif not filesAreEqual(source_file, replica_file):
                shutil.copy2(source_file, replica_file)  # copy the file (including metadata)
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
    
    # log a message if no files were copied or removed
    if changes_made:
        logger(log_file_path, 
                folders_created=folders_created, 
                folders_removed=folders_removed, 
                files_copied=files_copied, 
                files_replaced=files_replaced, 
                files_removed=files_removed
            )
    else:
        # define the colors for console output
        COLOR_RESET = "\033[0m"
        COLOR_GREEN = "\033[32m"

        logger(log_file_path, 
            console_message=(f"{COLOR_GREEN}Sync complete:{COLOR_RESET} No changes needed - {total_folders} folder(s) and {total_files} file(s) are already in sync."),
            log_message=(f"Sync complete: No changes needed - {total_folders} folder(s) and {total_files} file(s) are already in sync.")
            )

"---------------------------------------------------------------------------------------------"

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
        syncer(args.source, args.replica, args.log_file_path)
        time.sleep(args.interval)

"---------------------------------------------------------------------------------------------"

if __name__ == "__main__":
    main()  # run the main function