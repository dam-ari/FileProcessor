from config import (
    DEFAULT_WATERMARK_SIZE,
    DEFAULT_WATERMARK_TRANSPARENCY,
    DEFAULT_WATERMARK_POSITION,
    DEFAULT_FONT_SIZE,
    DEFAULT_SOFT_EDGE,
    DEFAULT_INCLUDE_DATE,
    DEFAULT_SAME_POSITION
)

options_mapping = {
    "main_menu": {
        "question": {
            "type": "list",
            "name": "action",
            "message": "Hi there, File Processor is here! How can I help you?",
            "choices": ["Merge files", "Copy metadata", "Apply watermark", "Load last request", "Quit"]
        },
        "actions": {
            "merge_files": {
                "description": "Merge all files in the directory",
                "params": []
            },
            "copy_metadata": {
                "description": "Copy metadata of all files in the directory",
                "params": []
            },
            "apply_watermark": {
                "description": "Apply watermark to files in the directory",
                "params": [
                    {"type": "input", "name": "watermark", "message": "Enter the watermark file path (leave blank for text only):", "default": ""},
                    {"type": "confirm", "name": "additional_params", "message": "Would you like to specify additional parameters for the watermark?", "default": False},
                    {"type": "input", "name": "text", "message": "Enter the text for watermark (leave blank if not applicable):", "default": "", "condition": "additional_params"},
                    {"type": "confirm", "name": "include_date", "message": "Include the current date in the watermark?", "default": DEFAULT_INCLUDE_DATE, "condition": "additional_params"},
                    {"type": "list", "name": "image_position", "message": "Select the position for the image watermark:", "choices": ["top_left", "top_center", "top_right", "middle_left", "middle_center", "middle_right", "bottom_left", "bottom_center", "bottom_right"], "default": DEFAULT_WATERMARK_POSITION, "condition": "additional_params"},
                    {"type": "confirm", "name": "same_position", "message": "Do you want the text in the same location as the image?", "default": DEFAULT_SAME_POSITION, "condition": "additional_params and text"},
                    {"type": "list", "name": "text_position", "message": "Select the position for the text watermark:", "choices": ["top_left", "top_center", "top_right", "middle_left", "middle_center", "middle_right", "bottom_left", "bottom_center", "bottom_right"], "default": DEFAULT_WATERMARK_POSITION, "condition": "additional_params and text and not same_position"},
                    {"type": "input", "name": "size", "message": f"Enter the size of the watermark as a percentage of the image size (default is {str(DEFAULT_WATERMARK_SIZE)}%):", "default": str(DEFAULT_WATERMARK_SIZE), "condition": "additional_params"},
                    {"type": "input", "name": "transparency", "message": f"Enter the transparency level for the watermark (0-255, default is {str(DEFAULT_FONT_SIZE)}):", "default": str(DEFAULT_WATERMARK_TRANSPARENCY), "condition": "additional_params"},
                    {"type": "confirm", "name": "soft_edge", "message": "Apply soft edges to the watermark image?", "default": DEFAULT_SOFT_EDGE, "condition": "additional_params"},
                    {"type": "input", "name": "font_size", "message": f"Enter the font size for the text watermark (default is { str(DEFAULT_FONT_SIZE)}):", "default": str(DEFAULT_FONT_SIZE), "condition": "additional_params and text"},
                ]
            },
            "load_last_request": {
                "description": "Load and adjust the last request",
                "params": []
            },
            "quit": {
                "description": "Quit the application",
                "params": []
            }
        }
    }
}
