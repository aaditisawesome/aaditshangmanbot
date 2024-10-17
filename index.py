from bot import HangmanBot
import os
from dotenv import load_dotenv

load_dotenv()
HangmanBot().run(os.environ["token"])