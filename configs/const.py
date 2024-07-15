from dotenv import load_dotenv
load_dotenv()

import os

# 機密情報
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_ENDPOINT = os.getenv('API_ENDPOINT')
API_VERSION = os.getenv('API_VERSION')
NEO4J_URI=os.getenv('NEO4J_URI')
NEO4J_USERNAME=os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD=os.getenv('NEO4J_PASSWORD')
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
PLACES_API_ENDPOINT=os.getenv('PLACES_API_ENDPOINT')

# Path
ORIGIN_PATH = os.getenv('ORIGIN_PATH')
DATA_PATH = ORIGIN_PATH + "data/"
OUTPUT_PATH = ORIGIN_PATH + "outputs/"