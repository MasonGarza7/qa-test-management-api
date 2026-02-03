import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = (
        f"postgresql+psycopg://"
        f"{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@"
        f"{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/"
        f"{os.getenv('DATABASE_NAME')}"
    )

if not DATABASE_URL or "None" in DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured correctly. "
        "Set DATABASE_URL, or set DATABASE_HOST/PORT/NAME/USER/PASSWORD."
    )

# engine = create_engine(DATABASE_URL, echo=True)            # Uncomment this line and comment the two lines below if you want SQL logs 
sql_echo = os.getenv("SQL_ECHO", "false").lower() == "true"
engine = create_engine(DATABASE_URL, echo=sql_echo)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
