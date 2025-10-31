import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root directory

# Ensure the run-logs directory exists
log_dir = os.path.abspath(os.path.join(os.path.dirname(BASE_DIR), "run-logs"))  # Explicitly resolve absolute path
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(log_dir, "debug.log"),  # Use the ensured directory
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "scd": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}