import sys
import os
import logging
from utils.cli import parse_args
from utils.config_loader import load_app_config
from core.container import AppContainer

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("Main")

def run_application():
    args = parse_args()

    try:
        config = load_app_config(args.config_dir)
    except Exception:
        sys.exit(1)

    container = AppContainer(config)
    storage = container.create_storage()
    crawler = container.create_crawler()

    try:
        logger.info(">>> Starting Nuri Bid Collector <<<")
        
        storage.connect()
        
        if checkpoint := storage.get_last_checkpoint():
            logger.info(f"Resuming from checkpoint: {checkpoint}")

        results = crawler.run()
        
        if results:
            storage.save(results)
            logger.info(">>> Job Completed Successfully <<<")
        else:
            logger.warning("No data collected.")

    except Exception as e:
        logger.error(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)
    finally:
        storage.close()
        logger.info("Application shutdown.")

if __name__ == "__main__":
    run_application()