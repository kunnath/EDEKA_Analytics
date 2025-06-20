"""
Database connection utilities for the EDEKA analytics application.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()

def load_config():
    """Load configuration from config.yaml file with environment variable substitution."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                              'config', 'config.yaml')
    
    # Read the raw YAML file
    with open(config_path, 'r') as file:
        config_content = file.read()
    
    # Substitute environment variables
    for key, value in os.environ.items():
        placeholder = f"${{{key}}}"
        if placeholder in config_content:
            config_content = config_content.replace(placeholder, value)
    
    # Parse the YAML with substitutions
    config = yaml.safe_load(config_content)
    return config

def get_connection_string(db_type, host, port, database, username, password):
    """Build a connection string based on database type."""
    password_quoted = quote_plus(password)
    
    if db_type.lower() == 'postgresql':
        return f"postgresql://{username}:{password_quoted}@{host}:{port}/{database}"
    elif db_type.lower() == 'mysql':
        return f"mysql+pymysql://{username}:{password_quoted}@{host}:{port}/{database}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def get_db_engine(db_config):
    """Create a SQLAlchemy engine from database configuration."""
    connection_string = get_connection_string(
        db_config['type'],
        db_config['host'],
        db_config['port'],
        db_config['database'],
        db_config['username'],
        db_config['password']
    )
    
    return create_engine(
        connection_string,
        pool_size=db_config.get('pool_size', 5),
        max_overflow=db_config.get('max_overflow', 10)
    )

def get_db_session(engine):
    """Create a SQLAlchemy session from an engine."""
    Session = sessionmaker(bind=engine)
    return Session()

def get_internal_db_engine():
    """Get the SQLAlchemy engine for the internal database."""
    config = load_config()
    return get_db_engine(config['databases']['internal'])

def get_external_db_engine():
    """Get the SQLAlchemy engine for the external database."""
    config = load_config()
    return get_db_engine(config['databases']['external'])
