import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Nuri Bid Collector - Public Procurement Crawler")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    default_config_dir = os.path.join(project_root, "config")

    parser.add_argument(
        "--config-dir", 
        type=str, 
        default=default_config_dir,
        help="Path to the configuration directory"
    )
    
    return parser.parse_args()