import os
import shutil
import logging
import json
from datetime import datetime

def get_metadata(file_path):
    try:
        stat = os.stat(file_path)
        metadata = {
            'size': stat.st_size,
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat()
        }
        return metadata
    except Exception as e:
        logging.error(f"Error getting metadata for {file_path}: {str(e)}")
        return None

def merge_files(files, output_file):
    try:
        with open(output_file, 'wb') as merged_file:
            for file in files:
                with open(file, 'rb') as f:
                    shutil.copyfileobj(f, merged_file)
        return True, False
    except Exception as e:
        metadata = get_metadata(file)
        logging.error(f"Error merging file {file}: {str(e)}, Metadata: {json.dumps(metadata)}")
        return False, True

def copy_metadata(files, output_file):
    metadata_list = []
    try:
        for file in files:
            metadata = get_metadata(file)
            if metadata:
                metadata_list.append({file: metadata})
        with open(output_file, 'w') as meta_file:
            json.dump(metadata_list, meta_file, indent=4)
        return True, False
    except Exception as e:
        logging.error(f"Error copying metadata: {str(e)}")
        return False, True

def get_files_to_process(directory):
    files_to_process = []
    logging.debug(f"Scanning directory: {directory}")

    if not os.path.isdir(directory):
        logging.error(f"Directory does not exist: {directory}")
        return []

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            files_to_process.append(file_path)
    logging.debug(f"Files to process: {files_to_process}")

    return files_to_process

def process_files(directory, action, file_type=None, custom_func=None):
    files_to_process = get_files_to_process(directory)
    if not files_to_process:
        logging.error(f"No files found to process in directory: {directory}")
        return False, False

    if action == 'merge_files':
        return merge_files(files_to_process, 'merged_file')
    elif action == 'copy_metadata':
        return copy_metadata(files_to_process, 'metadata.json')
    elif custom_func:
        success = True
        partial_success = False
        for file in files_to_process:
            try:
                custom_func(file)
            except Exception as e:
                partial_success = True
                metadata = get_metadata(file)
                logging.error(f"Error applying custom function to {file}: {str(e)}, Metadata: {json.dumps(metadata)}")
                success = False
        return success, partial_success
    return False, False

def show_log_tail(full=False):
    try:
        with open('file_processing.log', 'r') as log_file:
            lines = log_file.readlines()
            if full:
                print("\n".join(lines))
            else:
                tail_lines = lines[-5:] if len(lines) > 5 else lines
                print("\n".join(tail_lines))
    except Exception as e:
        print(f"Error reading log file: {str(e)}")
