import logging

# Create a logger for your package
logger = logging.getLogger(__name__)

# Create a custom logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/path/to/log/file.log'),  # Specify the path to your log file
        logging.StreamHandler()  # Output log messages to the console
    ]
)