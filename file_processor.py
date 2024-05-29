import argparse
import logging
import json
import os
from InquirerPy import prompt
import logger_config
from watermark import apply_watermark_to_files
from file_utils import process_files, show_log_tail
from options_mapping import options_mapping
from config import (
    DEFAULT_WATERMARK_SIZE,
    DEFAULT_WATERMARK_TRANSPARENCY,
    DEFAULT_FONT_SIZE,
    DEFAULT_SOFT_EDGE,
    DEFAULT_INCLUDE_DATE,
    DEFAULT_SAME_POSITION
)

CONFIG_FILE = 'last_request.json'

def save_request(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

def load_request():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def evaluate_condition(condition, context):
    try:
        return eval(condition, {}, context)
    except NameError:
        return False

def get_action():
    question = options_mapping["main_menu"]["question"]
    return prompt([question])["action"].lower().replace(" ", "_")

def get_params(action, previous=None):
    params = {}
    context = {}
    action_options = options_mapping["main_menu"]["actions"].get(action, {})
    for param in action_options.get("params", []):
        if "condition" in param and not evaluate_condition(param["condition"], context):
            continue
        param_name = param["name"]
        param_default = previous.get(param_name) if previous and param_name in previous else param.get("default", "")
        if isinstance(param_default, bool):
            param["default"] = param_default
        else:
            param["default"] = str(param_default)
        param_copy = param.copy()  # Create a copy of the param to avoid modifying the original
        if "condition" in param_copy:
            del param_copy["condition"]  # Remove the condition key from the copy if it exists
        response = prompt([param_copy])[param_name]
        params[param_name] = response
        context[param_name] = response
    return params

def main():
    parser = argparse.ArgumentParser(description="File Processor Script")
    parser.add_argument('-f', '--full', action='store_true', help='Show full log')
    args = parser.parse_args()

    previous_request = load_request()
    action = get_action()
    
    if action == "quit":
        print("Goodbye!")
        return

    if action == "load_last_request":
        if previous_request:
            action = previous_request.get("action", "apply_watermark")
            directory = previous_request.get("directory", "")
            params = get_params(action, previous_request.get("params", {}))
        else:
            print("No previous request found.")
            return
    else:
        directory_question = [
            {
                "type": "input",
                "name": "directory",
                "message": "Enter the directory path:"
            }
        ]
        directory = prompt(directory_question)["directory"].strip()
        params = get_params(action)
    
    # Remove 'additional_params' and 'same_position' key from params if they exist
    if 'additional_params' in params:
        del params['additional_params']
    if 'same_position' in params:
        same_position = params.pop('same_position')
    else:
        same_position = DEFAULT_SAME_POSITION
    
    # Convert size and transparency to integers
    if 'size' in params:
        params['size'] = int(params['size'])
    else:
        params['size'] = DEFAULT_WATERMARK_SIZE
    if 'transparency' in params:
        params['transparency'] = int(params['transparency'])
    else:
        params['transparency'] = DEFAULT_WATERMARK_TRANSPARENCY
    if 'font_size' in params:
        params['font_size'] = int(params['font_size'])
    else:
        params['font_size'] = DEFAULT_FONT_SIZE

    # Set text_position to image_position if same_position is True
    if same_position:
        params['text_position'] = params['image_position']

    print(f"Processing files in directory: {directory} with parameters: {params}")

    if action == "apply_watermark":
        success, partial_success = apply_watermark_to_files(directory, **params)
        request_data = {
            "action": action,
            "directory": directory,
            "params": params
        }
        save_request(request_data)
    else:
        success, partial_success = process_files(directory, action)

    if success and not partial_success:
        print(f"Done successfully! Check the processed files in {directory}")
    elif partial_success:
        print(f"Operation partially successful. Check the processed files in {directory}")
        log_option_question = [
            {
                "type": "confirm",
                "name": "show_log",
                "message": "Would you like to see the last few lines of the log?",
                "default": False
            }
        ]
        show_log = prompt(log_option_question)["show_log"]
        if show_log:
            show_log_tail(args.full)
    else:
        print("Operation failed. Please see the log for details.")
        log_option_question = [
            {
                "type": "confirm",
                "name": "show_log",
                "message": "Would you like to see the last few lines of the log?",
                "default": False
            }
        ]
        show_log = prompt(log_option_question)["show_log"]
        if show_log:
            show_log_tail(args.full)

if __name__ == "__main__":
    main()
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)
