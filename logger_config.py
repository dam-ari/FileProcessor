import logging

# Configure logging
logging.basicConfig(
    filename='file_processing.log',
    level=//logging.debug,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Console handler for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setLevel(//logging.debug)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

logging.getLogger().addHandler(console_handler)
