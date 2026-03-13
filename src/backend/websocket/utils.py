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
        format='%(asctime)s [%(levelname)-5s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Suppress verbose third-party library logs
    for name in ['websockets', 'asyncio', 'botocore.loaders', 'botocore.hooks']:
        logging.getLogger(name).propagate = False
