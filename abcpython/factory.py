from app import create_app
from config import Config

application = create_app(Config())
