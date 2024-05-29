import os
import logging

def get_files_to_process(directory):
    files_to_process = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            files_to_process.append(file_path)
    return files_to_process

def get_metadata(file):
    metadata = {}
    try:
        stat_info = os.stat(file)
        metadata = {
            "size": stat_info.st_size,
            "modified_time": stat_info.st_mtime,
            "created_time": stat_info.st_ctime
        }
    except Exception as e:
        logging.error(f"Error getting metadata for {file}: {str(e)}")
    return metadata

def show_log_tail(full_log=False):
    log_file = 'file_processing.log'
    if not os.path.exists(log_file):
        print("Log file does not exist.")
        return

    with open(log_file, 'r') as f:
        if full_log:
            log_content = f.read()
        else:
            log_content = f.readlines()[-10:]  # Show last 10 lines
    print("".join(log_content))
