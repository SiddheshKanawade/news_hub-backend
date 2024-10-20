import logging

LOG_FILE_NAME = "zapq-api"

LOCAL_LOG_PATH = f"/tmp/{LOG_FILE_NAME}.log"

formatter = logging.Formatter(
    "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
)


logging.basicConfig(
    format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOCAL_LOG_PATH), logging.StreamHandler()],
)

logger = logging.getLogger("general")
