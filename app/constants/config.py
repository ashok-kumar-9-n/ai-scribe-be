import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment
ENV = os.getenv("ENV", "PROD")

# Deepgram credentials
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# AWS credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")

# OpenAI API key
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

# MongoDB credentials
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
