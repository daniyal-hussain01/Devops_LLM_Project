"""Application configuration with environment-based settings."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///prompts.db")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    LOG_LEVEL = "WARNING"


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///test_prompts.db"
    GROQ_API_KEY = "test-api-key"


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.getenv("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
