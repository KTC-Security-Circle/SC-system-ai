import logging


# Create a custom logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output log messages to the console
    ]
)

# Create a logger for your package
logger = logging.getLogger(__name__)


