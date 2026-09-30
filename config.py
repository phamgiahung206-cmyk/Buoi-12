import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("system.log"), logging.StreamHandler()]
)
logger = logging.getLogger("SmartClean")

EXPECTED_COLUMNS = ["customer_id", "full_name", "email", "phone", "date_of_birth", "address"]
REQUIRED_FIELDS = ["customer_id", "full_name"]
DB_PATH = "smartclean_state.db"

# Model configuration
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")