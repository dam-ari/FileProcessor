from config import (
    DEFAULT_WATERMARK_SIZE,
    DEFAULT_WATERMARK_TRANSPARENCY,
    DEFAULT_WATERMARK_POSITION,
    DEFAULT_FONT_SIZE,
    DEFAULT_SOFT_EDGE,
    DEFAULT_INCLUDE_DATE,
    DEFAULT_SAME_POSITION
)

class ActionOption:
    def __init__(self, emoji, name, module, function, description, params):
        self.emoji = emoji
        self.name = name
        self.module = module
        self.function = function
        self.description = description
        self.params = params

    def get_display_name(self):
        return f"{self.emoji} {self.name}"

    def get_action_name(self):
        return self.name.lower().replace(" ", "_")

actions = [
    ActionOption("✨", "Merge files", "actions.merge", "merge_files", "Merge all files in the directory", [
        {"type": "confirm", "name": "include_subdirectories", "message": "🔍 Include subdirectories?", "default": True},
        {"type": "input", "name": "rows", "message": "🔢 Enter the number of rows for merging images:", "default": "1"},
        {"type": "list", "name": "fill_method", "message": "🖼️ Choose how to handle the last row:", "choices": ["stretch", "leave", "repeat"], "default": "stretch"}
    ]),
    ActionOption("📋", "Copy metadata", "actions.metadata", "copy_metadata", "Copy metadata of all files in the directory", [
        {"type": "confirm", "name": "include_subdirectories", "message": "🔍 Include subdirectories?", "default": True}
    ]),
    ActionOption("🌊", "Apply watermark", "actions.watermark", "apply_watermark_to_files", "Apply watermark to files in the directory", [
        {"type": "input", "name": "watermark", "message": "🌊 Enter the watermark file path (leave blank for text only):", "default": ""},
        {"type": "confirm", "name": "additional_params", "message": "⚙️ Would you like to specify additional parameters for the watermark?", "default": False},
        {"type": "input", "name": "text", "message": "📝 Enter the text for watermark (leave blank if not applicable):", "default": "", "condition": "additional_params"},
        {"type": "confirm", "name": "include_date", "message": "📅 Include the current date in the watermark?", "default": DEFAULT_INCLUDE_DATE, "condition": "additional_params"},
        {"type": "list", "name": "image_position", "message": "📍 Select the position for the image watermark:", "choices": ["top_left", "top_center", "top_right", "middle_left", "middle_center", "middle_right", "bottom_left", "bottom_center", "bottom_right"], "default": DEFAULT_WATERMARK_POSITION, "condition": "additional_params"},
        {"type": "confirm", "name": "same_position", "message": "🖼️ Do you want the text in the same location as the image?", "default": DEFAULT_SAME_POSITION, "condition": "additional_params and text"},
        {"type": "list", "name": "text_position", "message": "📍 Select the position for the text watermark:", "choices": ["top_left", "top_center", "top_right", "middle_left", "middle_center", "middle_right", "bottom_left", "bottom_center", "bottom_right"], "default": DEFAULT_WATERMARK_POSITION, "condition": "additional_params and text and not same_position"},
        {"type": "input", "name": "size", "message": f"🔍 Enter the size of the watermark as a percentage of the image size (default is { str(DEFAULT_WATERMARK_SIZE)}%):", "default": str(DEFAULT_WATERMARK_SIZE), "condition": "additional_params"},
        {"type": "input", "name": "transparency", "message": f"💧 Enter the transparency level for the watermark (0-255, default is {str(DEFAULT_WATERMARK_TRANSPARENCY)}):", "default": str(DEFAULT_WATERMARK_TRANSPARENCY), "condition": "additional_params"},
        {"type": "confirm", "name": "soft_edge", "message": f"🌫️ Apply soft edges to the watermark image?", "default": DEFAULT_SOFT_EDGE, "condition": "additional_params"},
        {"type": "input", "name": "font_size", "message": f"🔤 Enter the font size for the text watermark (default is {str(DEFAULT_FONT_SIZE)}):", "default": str(DEFAULT_FONT_SIZE), "condition": "additional_params and text"},
    ]),
    ActionOption("🔄", "Load last request", None, None, "Load and adjust the last request", []),
    ActionOption("❌", "Quit", None, None, "Quit the application", [])
]

main_menu_question = {
    "type": "list",
    "name": "action",
    "message": "🦄 Hi there, File Processor is here! How can I help you? 🦄",
    "choices": [action.get_display_name() for action in actions]
}

log_option_question = {
    "type": "confirm",
    "name": "show_log",
    "message": "📜 Would you like to see the last few lines of the log?",
    "default": False
}

def get_action_details(action_name):
    for action in actions:
        if action.get_action_name() == action_name:
            return action
    return None
