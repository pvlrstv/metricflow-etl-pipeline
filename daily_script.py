# Import required libraries
from datetime import datetime, timedelta
import json
import requests
import logging
import os
import configparser

from pgdb import PGDatabase

# Load configuration from config.ini
config = configparser.ConfigParser()
dirname = os.path.dirname(__file__)
config.read(os.path.join(dirname, "config.ini"))

DATABASE_CREDS = config["Database"]
API_CREDS = config["Api"]

# Create logs directory if it doesn't exist
logs_dir = os.path.join(dirname, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

log_name = os.path.join(logs_dir, f"{datetime.now():%Y_%m_%d}.log")

# Remove log files older than 3 days
for file in os.listdir(logs_dir):
    if file.endswith(".log"):
        if (
            datetime.now() - datetime.strptime(file.split(".")[0], "%Y_%m_%d")
        ).days > 3:
            os.remove(os.path.join(logs_dir, file))

# Logging configuration
logging.basicConfig(
    filename=log_name,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Connect to the database and ensure the table exists
database = PGDatabase(
    host=DATABASE_CREDS["HOST"],
    database=DATABASE_CREDS["DATABASE"],
    user=DATABASE_CREDS["USER"],
    password=DATABASE_CREDS["PASSWORD"],
)

creating_query = """
CREATE TABLE IF NOT EXISTS purchases (
        id SERIAL PRIMARY KEY,
        client_id INTEGER,
        gender TEXT,
        purchase_datetime DATE,
        purchase_time_as_seconds_from_midnight INTEGER,
        product_id INTEGER,
        quantity NUMERIC,
        price_per_item NUMERIC,
        discount_per_item NUMERIC,
        total_price NUMERIC
    );
"""
database.post(creating_query)

# API connection settings
yesterday = str((datetime.now() - timedelta(days=1)).date())

api_url = API_CREDS["URL"]
params = {"date": yesterday}
headers = {"Accept": API_CREDS["ACCEPT"]}

# Data fetching from API
logging.info("Starting API data download")

try:
    r = requests.get(url=api_url, params=params, headers=headers)
    r.raise_for_status()
    purchases = r.json()
    logging.info("API data download completed successfully")
except Exception as err:
    logging.error(f"API access failed, status code: {r.status_code}, error: {err}")
    purchases = []

# Prepare data for insertion
columns = [
    "client_id",
    "gender",
    "purchase_datetime",
    "purchase_time_as_seconds_from_midnight",
    "product_id",
    "quantity",
    "price_per_item",
    "discount_per_item",
    "total_price",
]

cols_str = ", ".join(columns)
values_str = ", ".join(["%s"] * len(columns))

query = f"""
    INSERT INTO purchases ({cols_str})
    VALUES ({values_str})
    ON CONFLICT DO NOTHING;
"""

# Write fetched data to the database
logging.info("Starting database population")

try:
    if purchases:
        for i, purchase in enumerate(purchases, start=1):
            values = [purchase[col] for col in columns]
            database.post(query, values)
        database.post("ANALYZE purchases;")
        logging.info("Data successfully written and table statistics updated")
    else:
        logging.warning("No data available to insert")

except Exception as err:
    logging.error(f"Database write error: {err}")
    try:
        if getattr(database, "connection", None):
            database.connection.rollback()
    except Exception:
        logging.exception("Rollback error")
finally:
    try:
        if getattr(database, "connection", None):
            database.connection.close()
    except Exception:
        logging.exception("Connection closure error")
    logging.info("Database connection closed")
