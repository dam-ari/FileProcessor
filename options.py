# options.py

actions = {
    "merge_files": {
        "name": "Merge files",
        "options": []
    },
    "copy_metadata": {
        "name": "Copy metadata",
        "options": []
    },
    "apply_watermark": {
        "name": "Apply watermark",
        "options": [
            {
                "type": "input",
                "name": "watermark",
                "message": "Enter the watermark file path (leave blank for text only):",
                "default": ""
            },
            {
                "type": "confirm",
                "name": "additional_params",
                "message": "Would you like to specify additional parameters for the watermark?",
                "default": False
            }
        ]
    },
    "watermark_additional_params": [
        {
            "type": "input",
            "name": "text",
            "message": "Enter the text for watermark (leave blank if not applicable):",
            "default": ""
        },
        {
            "type": "confirm",
            "name": "include_date",
            "message": "Include the current date in the watermark?",
            "default": False
        },
        {
            "type": "list",
            "name": "image_position",
            "message": "Select the position for the image watermark:",
            "choices": [
                "top_left", "top_center", "top_right", 
                "middle_left", "middle_center", "middle_right", 
                "bottom_left", "bottom_center", "bottom_right"
            ],
            "default": "bottom_center"
        },
        {
            "type": "confirm",
            "name": "same_position",
            "message": "Do you want the text in the same location as the image?",
            "default": True
        },
        {
            "type": "list",
            "name": "text_position",
            "message": "Select the position for the text watermark:",
            "choices": [
                "top_left", "top_center", "top_right", 
                "middle_left", "middle_center", "middle_right", 
                "bottom_left", "bottom_center", "bottom_right"
            ],
            "default": "bottom_center"
        },
        {
            "type": "input",
            "name": "size",
            "message": "Enter the size of the watermark as a percentage of the image size (default is 10%):",
            "default": "10"
        },
        {
            "type": "input",
            "name": "transparency",
            "message": "Enter the transparency level for the watermark (0-255, default is 128):",
            "default": "128"
        },
        {
            "type": "confirm",
            "name": "soft_edge",
            "message": "Apply soft edges to the watermark image?",
            "default": True
        },
        {
            "type": "input",
            "name": "font_size",
            "message": "Enter the font size for the text watermark (default is 20):",
            "default": "20"
        },
        {
            "type": "input",
            "name": "font_path",
            "message": "Enter the path to the font file for the text watermark (leave blank for default):",
            "default": ""
        }
    ]
}
