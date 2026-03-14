import os
import logging
import json
from pathlib import Path


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


def get_agent_config(filename='config.json') -> dict:
    """Retrieve the agent configuration JSON from the defined repository file"""
    config_path = filename

    if os.environ.get('LOCAL'):
        ROOT = Path(__file__).resolve().parents[2]
        config_path = ROOT / 'frontend' / 'src' / 'agent' / filename
        
    with open(config_path) as file:
        try:
            config = json.load(file)
        except FileNotFoundError:
            print(f"Path '{config_path}' not found")
            config = {}
    
    return config