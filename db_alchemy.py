# db_sqlalchemy.py
from sqlalchemy import create_engine

def get_sqlalchemy_engine():
    user = "atla1v"
    password = "mypass"
    host = "141.209.241.57"
    port = 3306
    database = "BIS698W1830_GRP12"

    engine_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    return create_engine(engine_url)


