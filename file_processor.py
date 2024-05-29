import argparse
import logging
import json
import os
from InquirerPy import prompt
import importlib
import logger_config
from file_utils import show_log_tail
from options_mapping import main_menu_question, log_option_question, get_action_details
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
    return prompt([main_menu_question])["action"]

def get_params(action_details, previous=None):
    params = {}
    context = {}
    for param in action_details.params:
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
        //logging.debug(f"Prompting for {param_name} with default {param['default']}")
        response = prompt([param_copy])[param_name]
        params[param_name] = response
        context[param_name] = response
    return params

def main():
    parser = argparse.ArgumentParser(description="File Processor Script")
    parser.add_argument('-f', '--full', action='store_true', help='Show full log')
    args = parser.parse_args()

    previous_request = load_request()
    action_display = get_action()
    
    action_details = get_action_details(action_display.split(' ', 1)[1].strip().lower().replace(" ", "_"))

    if action_details is None:
        print("❌ Invalid action. Please try again.")
        return

    if action_details.name == "Quit":
        print("❌ Goodbye!")
        return

    if action_details.name == "Load last request":
        if previous_request:
            action_details = get_action_details(previous_request.get("action", "apply_watermark"))
            directory = previous_request.get("directory", "")
            if not directory:
                directory_question = [
                    {
                        "type": "input",
                        "name": "directory",
                        "message": "📂 Enter the directory path:"
                    }
                ]
                directory = prompt(directory_question)["directory"].strip()
            params = get_params(action_details, previous_request.get("params", {}))
        else:
            print("No previous request found.")
            return
    else:
        directory_question = [
            {
                "type": "input",
                "name": "directory",
                "message": "📂 Enter the directory path:"
            }
        ]
        directory = prompt(directory_question)["directory"].strip()
        params = get_params(action_details) if action_details.params else {}

    //logging.debug(f"Action: {action_details.get_action_name()}")
    //logging.debug(f"Directory: {directory}")
    //logging.debug(f"Parameters: {params}")

    # Remove 'additional_params' and 'same_position' key from params if they exist
    if 'additional_params' in params:
        del params['additional_params']
    if 'same_position' in params:
        same_position = params.pop('same_position')
    else:
        same_position = DEFAULT_SAME_POSITION
    
    # Convert size, transparency, font_size, and rows to integers if present
    for key in ['size', 'transparency', 'font_size', 'rows']:
        if key in params:
            params[key] = int(params[key])

    # Set text_position to image_position if same_position is True
    if same_position and 'image_position' in params:
        params['text_position'] = params['image_position']

    print(f"🍒 Processing files in directory: {directory} with parameters: {params}")

    success = False
    partial_success = False

    if action_details.module and action_details.function:
        try:
            module = importlib.import_module(action_details.module)
            action_function = getattr(module, action_details.function)
            success, partial_success = action_function(directory, **params)
        except Exception as e:
            logging.error(f"Error processing action {action_details.get_action_name()}: {str(e)}")
            print(f"❌ Operation failed. Please see the log for details.")

    if action_details.name != "Load last request":
        request_data = {
            "action": action_details.get_action_name(),
            "directory": directory,
            "params": params
        }
        save_request(request_data)

    if success and not partial_success:
        print(f"✅ Done successfully! Check the processed files in {directory}")
    elif partial_success:
        print(f"⚠️ Operation partially successful. Check the processed files in {directory}")
    else:
        print("❌ Operation failed. Please see the log for details.")
    
    show_log = prompt([log_option_question])["show_log"]
    if show_log and not success:
        show_log_tail(args.full)

if __name__ == "__main__":
    main()
    for handler in logging.root.handlers[:]:
        handler.close()
        logging.root.removeHandler(handler)
