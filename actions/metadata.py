import logging
import os
import json
from file_utils import get_files_to_process, get_metadata

def copy_metadata(directory, **kwargs):
    try:
        files_to_process = get_files_to_process(directory)
        metadata_list = []
        
        for file in files_to_process:
            metadata = get_metadata(file)
            metadata_list.append(metadata)
        
        output_file = os.path.join(directory, "metadata.json")
        with open(output_file, 'w') as f:
            json.dump(metadata_list, f)
        
        logging.info(f"Metadata copied to {output_file}")
        return True, False
    except Exception as e:
        logging.error(f"Error copying metadata: {str(e)}")
        return False, True
