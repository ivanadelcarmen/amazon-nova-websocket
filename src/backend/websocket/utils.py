import os
import logging


def is_debug_mode():
    """Check if debug mode is enabled by the DEBUG env variable"""
    return bool(os.environ.get('DEBUG'))


def setup_logging(debug=False):
    """Configure logging for the application"""
    level = logging.DEBUG if debug else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set level for specific loggers if needed
    if not debug:
        # Suppress verbose third-party library logs in non-debug mode
        logging.getLogger('websockets').setLevel(logging.WARNING)
        logging.getLogger('asyncio').setLevel(logging.WARNING)
