import logging
import sys
import asyncio
from queue import SimpleQueue

log_queue = SimpleQueue()

class QueueHandler(logging.Handler):
    """Custom log handler to push logs to a queue"""
    def emit(self, record):
        log_entry = self.format(record)
        log_queue.put(log_entry)

def get_logger(name: str):
    """Get a configured logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Queue Handler (for streaming logs)
        queue_handler = QueueHandler()
        queue_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        queue_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(queue_handler)
    
    return logger

def setup_logging():
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
