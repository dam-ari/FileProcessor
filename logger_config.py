import logging

# Configure logging to only log to a file and not to the console
logging.basicConfig(
    filename='file_processing.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
