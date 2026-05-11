import logging
import os

def get_logger(module_name):    
    os.makedirs("outputs/logs", exist_ok=True)
    logger = logging.getLogger(module_name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)    
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(module)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        file_handler = logging.FileHandler("outputs/logs/pipeline.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)    
    return logger