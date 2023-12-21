import logging
import logging.handlers
import constants
import functools
from extended_updates import ExtendedUpdate

class CustomLogger():
    __slots__ = ["logger"]
    default_fmt: str = '%(asctime)s -- %(name)s:%(levelname)s: %(message)s' 
    default_datefmt: str = '%Y-%m-%d %H:%M:%S'
    default_level = logging.INFO
    loggers: list = []

    def __init__(self, name=None, level=default_level) -> None:
        # I decided not to inherit from the logging.Logger class, since loggers shouldn't be instantiated directly, but returned via logging.getLogger instead.
        # This approach is recommended because getLogger function checks if a requested logger already exists, and creates a new one only if it's necessary.
        # Therefore, I decided to just create an attribute that is an instance of Logger class, and delegate needed functionlities to it.
        
        self.logger = logging.getLogger(name)
        self.loggers.append(self.logger)
        self.logger.setLevel(level)
        
    def _makeFormatter(self, formatter=logging.Formatter, fmt=default_fmt, datefmt=default_datefmt) -> logging.Formatter:
        return formatter(fmt=fmt, datefmt=datefmt)
       
    def addHandler(self, handler_class, formatter=logging.Formatter, fmt=default_fmt, datefmt=default_datefmt, level=default_level, **kwargs) -> None:
        handler = handler_class(**kwargs)
        handler.setLevel(level)
        handler.setFormatter(self._makeFormatter(formatter, fmt, datefmt))
        self.logger.addHandler(handler)
        
    def debug(self, msg, *args, **kwargs) -> None:
        self.logger.debug(msg, *args, **kwargs)
         
    def info(self, msg, *args, **kwargs) -> None:
        self.logger.info(msg, *args, **kwargs)
        
    def warning(self, msg, *args, **kwargs) -> None:
        self.logger.warning(msg, *args, **kwargs)
        
    def error(self, msg, *args, **kwargs) -> None:
        self.logger.error(msg, *args, **kwargs)
        
    def exception(self, msg, *args, **kwargs) -> None:
        self.logger.exception(msg, *args, **kwargs)
        
    def critical(self, msg, *args, **kwargs) -> None:
        self.logger.critical(msg, *args, **kwargs)
        
    def setLevel(self, level) -> None:
        self.logger.setLevel(level)


def conversation(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        update, context = ExtendedUpdate(args[0]), args[1]
        args = (update,) + args[1:]
        response = await func(*args, **kwargs)
        conversation_logger.info(f"{update.update_type} sent by USER ({update.effective_user.name}) in {update.effective_chat.type} ({repr(update.effective_chat.effective_name)}). TEXT: {repr(update.effective_text)}; CONTENT: {update.message_type}")
        if response:
            conversation_logger.info(f"message sent by BOT ({constants.BOT_USERNAME}) in {update.effective_chat.type} ({repr(update.effective_chat.effective_name)}). CONTENT: {repr(response)}")
        return response
    return wrapper

def error(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        update, context = args[0], args[1]
        conversation_logger.error(f"{context.error} was raised by Update {update}")
        return response
    return wrapper


# data registered by root logger at INFO level will be saved to root.log file,
# and all that is of ERROR level will also be saved to a separate errors.log file 
root_logger = CustomLogger()
root_logger.addHandler(logging.handlers.TimedRotatingFileHandler, **{'level': logging.INFO, 'filename': "root.log", 'when': constants.EVERY_SUNDAY, 'backupCount': constants.BACKUP_COUNT, 'encoding': constants.ENCODING})
root_logger.addHandler(logging.handlers.TimedRotatingFileHandler, **{'level': logging.ERROR, 'filename': "errors.log", 'when': constants.EVERY_SUNDAY, 'backupCount': constants.BACKUP_COUNT, 'encoding': constants.ENCODING})

logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram.ext.Application').setLevel(logging.INFO)

# Creating a custom conversation logger to keep track of the conversation only. It will not be saved to a separate file, 
# but will stream logs to the console. Logs from this logger will be included in the root log
conversation_logger = CustomLogger("conversation")
conversation_logger.addHandler(handler_class=logging.StreamHandler, level=logging.INFO)
