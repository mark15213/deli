import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.core.config import get_settings

settings = get_settings()

def setup_logging():
    """
    Configure logging for the application.
    Logs to console and to a rotating file.
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    # Define formatter for files
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Define formatter for console (matching uvicorn style)
    try:
        from uvicorn.logging import DefaultFormatter
        console_formatter = DefaultFormatter("%(levelprefix)s %(name)s: %(message)s")
    except ImportError:
        console_formatter = logging.Formatter("%(levelname)s:     %(name)s: %(message)s")

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # File Handler (Rotating)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5  # 10MB per file, keep 5 backups
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG) # Catch everything in file

    # Root Logger Configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates (e.g. uvicorn's)
    if root_logger.handlers:
        root_logger.handlers = []
        
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Set levels for specific libraries
    # Set levels for specific libraries to reduce noise
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING) # Suppress binary/form-data logs
    logging.getLogger("pdfminer").setLevel(logging.WARNING)

    return root_logger

# Initialize logger for convenient import
logger = logging.getLogger("app")
