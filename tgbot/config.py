import ast
import dotenv
import os
import pathlib


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

DATABASE_FILE_PATH = BASE_DIR / 'database.db'

DOTENV_PATH = BASE_DIR / '.env'

if DOTENV_PATH.exists():
    dotenv.load_dotenv(DOTENV_PATH)

ADMIN_IDS = ast.literal_eval(os.getenv('ADMIN_IDS', '[688003991]'))

try:
    PROXY = ast.literal_eval(os.getenv('PROXY'))
except Exception:
    PROXY = os.getenv('PROXY')

DEBUG = ast.literal_eval(os.getenv('DEBUG'))

TOKEN = os.getenv('TOKEN')

if DEBUG:
    TOKEN = os.getenv('DEBUG_TOKEN')
