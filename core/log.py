import logging
import os
import asyncio
from enum import Enum
from datetime import datetime

# Ensure logs directory exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Setup basic file handler
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Internal logger for file operations to avoid recursion if we used our own class
_file_logger = logging.getLogger("FixMate")

async def sendError(level: str, msg: str):
    """
    Placeholder for external notification logic.
    """
    try:
        # In a real application, you would make an HTTP request here
        # print(f"[{level.upper()} NOTIFICATION SENT]: {msg}")
        pass
    except Exception as e:
        _file_logger.error(f"Failed to send notification: {e}")

class Logger:
    class StyleModifier:
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'

    class Error:
        def __init__(self, parent):
            self.parent = parent

        def _log(self, msg: str, level: str = "ERROR", color: str = None):
            if color is None:
                color = Logger.StyleModifier.RED
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Console output
            print(f"{color}{timestamp} - ERROR - {level} - {msg}{Logger.StyleModifier.ENDC}")
            # File output
            _file_logger.error(f"[{level}] {msg}")

        def _trigger(self, severity: str, *args):
            msg = " ".join(str(a) for a in args)
            self._log(msg, level=severity.upper())
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(sendError(severity, msg))
            except RuntimeError:
                # No running loop, just skip notification or run sync if needed
                pass

        def __call__(self, *args):
            msg = " ".join(str(a) for a in args)
            self._log(msg)

        def low(self, *args):
            self._trigger("low", *args)

        def medium(self, *args):
            self._trigger("medium", *args)

        def high(self, *args):
            self._trigger("high", *args)

        def critical(self, *args):
            self._trigger("critical", *args)

    def __init__(self):
        self.error = Logger.Error(self)

    def _print(self, color, level, *args):
        msg = " ".join(str(a) for a in args)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Console output
        print(f"{color}{timestamp} - {level} - {msg}{Logger.StyleModifier.ENDC}")
        
        # File output mapping
        if level == "INFO":
            _file_logger.info(msg)
        elif level == "WARN":
            _file_logger.warning(msg)
        elif level == "TRACK":
            _file_logger.info(f"[TRACK] {msg}")

    def info(self, *args):
        self._print(Logger.StyleModifier.BLUE, "INFO", *args)

    def warn(self, *args):
        self._print(Logger.StyleModifier.YELLOW, "WARN", *args)

    def track(self, *args):
        self._print(Logger.StyleModifier.GREEN, "TRACK", *args)

# Create singleton instance
logger = Logger()
