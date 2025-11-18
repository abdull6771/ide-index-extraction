"""
Configuration Management
"""

import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Application configuration"""
    
    # Base directories
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "outputs"
    DATABASE_DIR = BASE_DIR / "database"
    
    # Database
    DATABASE_PATH = DATABASE_DIR / "ide_index.db"
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # gpt-4o-mini, gpt-4o, gpt-3.5-turbo
    
    # Processing Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "3000"))  # Characters per chunk
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "500"))  # Overlap between chunks
    MAX_CHUNKS_PER_DOCUMENT = int(os.getenv("MAX_CHUNKS_PER_DOCUMENT", "0"))  # 0 = process all chunks
    
    # Categories
    DIGITAL_CATEGORIES = [
        "Digital Infrastructure",
        "AI & Automation",
        "Cybersecurity",
        "Customer Experience",
        "ESG Tech"
    ]
    
    # Report types
    REPORT_TYPES = [
        "Annual Report",
        "Corporate Governance Report",
        "Sustainability Report"
    ]
    
    # Supported years
    SUPPORTED_YEARS = [2022, 2023, 2024, 2025]
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        errors = []
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        
        if not cls.DATA_DIR.exists():
            errors.append(f"Data directory does not exist: {cls.DATA_DIR}")
        
        if errors:
            for error in errors:
                print(f"❌ Configuration Error: {error}")
            return False
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        print("=" * 60)
        print("CONFIGURATION")
        print("=" * 60)
        print(f"Base Directory: {cls.BASE_DIR}")
        print(f"Data Directory: {cls.DATA_DIR}")
        print(f"Output Directory: {cls.OUTPUT_DIR}")
        print(f"Database Path: {cls.DATABASE_PATH}")
        print(f"OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"Chunk Size: {cls.CHUNK_SIZE}")
        print(f"Chunk Overlap: {cls.CHUNK_OVERLAP}")
        if cls.MAX_CHUNKS_PER_DOCUMENT > 0:
            print(f"Max Chunks/Document: {cls.MAX_CHUNKS_PER_DOCUMENT}")
        else:
            print(f"Max Chunks/Document: All")
        print(f"API Key Set: {'Yes' if cls.OPENAI_API_KEY else 'No'}")
        print("=" * 60)


if __name__ == "__main__":
    Config.print_config()
    
    if Config.validate():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has errors")
