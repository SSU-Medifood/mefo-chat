import pandas as pd
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset": "utf8mb4"
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)


def load_recipe_df():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM recipe", conn)
    conn.close()
    return df


def load_ingredient_df():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM ingredient", conn)
    conn.close()
    return df
