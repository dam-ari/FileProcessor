import argparse
import logging
import json
import os
from InquirerPy import prompt
import logger_config
from watermark import apply_watermark_to_files
from file_utils import process_files, show_log_tail

CONFIG_FILE = 'last_request.json'

def save_request(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

def load_request():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def get_action():
    questions = [
        {
            "type": "list",
            "name": "action",
            "message": "Hi there, File Processor is here! How can I help you?",
            "choices": ["Merge files", "Copy metadata", "Apply watermark", "Quit"]
        }
    ]
    return prompt(questions)["action"].lower().replace(" ", "_")

def get_directory(previous=None):
    directory_question = [
        {
            "type": "input",
            "name": "directory",
            "message": "Enter the directory path:",
            "default": previous if previous else ""
        }
    ]
    return prompt(directory_question)["directory"].strip()

def get_watermark_params(previous=None):
    watermark_question = [
        {
            "type": "input",
            "name": "watermark",
            "message": "Enter the watermark file path (leave blank for text only):",
            "default": previous.get("watermark") if previous else ""
        }
    ]
    watermark = prompt(watermark_question)["watermark"].strip()
    if watermark == "":
        watermark = None

    params_question = [
        {
            "type": "confirm",
            "name": "additional_params",
            "message": "Would you like to specify additional parameters for the watermark?",
            "default": previous.get("additional_params", False) if previous else False
        }
    ]
    additional_params = prompt(params_question)["additional_params"]

    text = None
    include_date = False
    image_position = "bottom_center"
    text_position = "bottom_center"
    size = 10
    transparency = 128  # Default transparency level (0-255)
    soft_edge = True  # Default soft edge

    if additional_params:
        text_question = [
            {
                "type": "input",
                "name": "text",
                "message": "Enter the text for watermark (leave blank if not applicable):",
                "default": previous.get("text") if previous else ""
            }
        ]
        text = prompt(text_question)["text"].strip()
        if text == "":
            text = None

        date_question = [
            {
                "type": "confirm",
                "name": "include_date",
                "message": "Include the current date in the watermark?",
                "default": previous.get("include_date", False) if previous else False
            }
        ]
        include_date = prompt(date_question)["include_date"]

        image_position_question = [
            {
                "type": "list",
                "name": "image_position",
                "message": "Select the position for the image watermark:",
                "choices": [
                    "top_left", "top_center", "top_right", 
                    "middle_left", "middle_center", "middle_right", 
                    "bottom_left", "bottom_center", "bottom_right"
                ],
                "default": previous.get("image_position", "bottom_center") if previous else "bottom_center"
            }
        ]
        image_position = prompt(image_position_question)["image_position"]

        if text:
            text_position_question = [
                {
                    "type": "confirm",
                    "name": "same_position",
                    "message": "Do you want the text in the same location as the image?",
                    "default": previous.get("same_position", True) if previous else True
                }
            ]
            same_position = prompt(text_position_question)["same_position"]

            if not same_position:
                text_position_question = [
                    {
                        "type": "list",
                        "name": "text_position",
                        "message": "Select the position for the text watermark:",
                        "choices": [
                            "top_left", "top_center", "top_right", 
                            "middle_left", "middle_center", "middle_right", 
                            "bottom_left", "bottom_center", "bottom_right"
                        ],
                        "default": previous.get("text_position", "bottom_center") if previous else "bottom_center"
                    }
                ]
                text_position = prompt(text_position_question)["text_position"]
            else:
                text_position = image_position
        else:
            text_position = None

        size_question = [
            {
                "type": "input",
                "name": "size",
                "message": "Enter the size of the watermark as a percentage of the image size (default is 10%):",
                "default": previous.get("size", "10") if previous else "10"
            }
        ]
        size = int(prompt(size_question)["size"])

        transparency_question = [
            {
                "type": "input",
                "name": "transparency",
                "message": "Enter the transparency level for the watermark (0-255, default is 128):",
                "default": previous.get("transparency", "128") if previous else "128"
            }
        ]
        transparency = int(prompt(transparency_question)["transparency"])

        soft_edge_question = [
            {
                "type": "confirm",
                "name": "soft_edge",
                "message": "Apply soft edges to the watermark image?",
                "default": previous.get("soft_edge", True) if previous else True
            }
        ]
        soft_edge = prompt(soft_edge_question)["soft_edge"]

    return watermark, text, include_date, image_position, text_position, size, transparency, soft_edge

def main():
    parser = argparse.ArgumentParser(description="File Processor Script")
    parser.add_argument('-f', '--full', action='store_true', help='Show full log')
    args = parser.parse_args()

    previous_request = load_request()
    if previous_request:
        load_previous_question = [
            {
                "type": "confirm",
                "name": "load_previous",
                "message": "Would you like to load and adjust the last request?",
                "default": True
            }
        ]
        load_previous = prompt(load_previous_question)["load_previous"]
    else:
        load_previous = False

    if load_previous:
        action = previous_request.get("action", "apply_watermark")
        directory = previous_request.get("directory", "")
    else:
        action = get_action()
        directory = get_directory()

    if action == "quit":
        print("Goodbye!")
        return

    watermark = None
    text = None
    include_date = False
    image_position = "bottom_center"
    text_position = "bottom_center"
    size = 10
    transparency = 128
    soft_edge = True

    if action == "apply_watermark":
        if load_previous:
            params = previous_request.get("params", {})
            watermark, text, include_date, image_position, text_position, size, transparency, soft_edge = get_watermark_params(previous=params)
        else:
            watermark, text, include_date, image_position, text_position, size, transparency, soft_edge = get_watermark_params()

    print(f"Processing files in directory: {directory} with watermark: {watermark}, text: {text}, date: {include_date}, image position: {image_position}, text position: {text_position}, size: {size}%, transparency: {transparency}, soft edge: {soft_edge}")

    if action == "apply_watermark":
        success, partial_success = apply_watermark_to_files(directory, watermark=watermark, text=text, include_date=include_date, image_position=image_position, text_position=text_position, size=size, transparency=transparency, soft_edge=soft_edge)
        request_data = {
            "action": action,
            "directory": directory,
            "params": {
                "watermark": watermark,
                "text": text,
                "include_date": include_date,
                "image_position": image_position,
                "text_position": text_position,
                "size": size,
                "transparency": transparency,
                "soft_edge": soft_edge
            }
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
