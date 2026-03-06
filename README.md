# Project Info

**Project:** Automated ETL Pipeline for a Marketplace

**Goals:** 

1. Automatically extract sales data from an API every day.
2. Store the data in a PostgreSQL database.
3. Create a dashboard to track key metrics in real-time.

**Data:** The script gets JSON data from an API.

**Tools:** 

- Python: Used for data processing (Pandas, Psycopg2, Logging).
- Docker: To run the database and Metabase in containers.
- PostgreSQL: A relational database for data storage.
- Metabase: A tool for creating charts and dashboards.
- Cron: A task scheduler to run the script at 6:00 AM daily.

**Key Results:**

- A Python ETL script that runs and handles errors via logging automatically.
- A PostgreSQL database that updates every morning.
- A Metabase dashboard for daily metrics monitoring.
*Public Dashboard:* <a href="http://89.168.75.28:3000/public/dashboard/ad49ba70-5444-4a62-abc6-1ead8090bfcc">Daily Metrics Dashboard</a>

# Project Structure

- *daily_script.py* — the main ETL script with logging and log rotation
- *pgdb.py* — the module for database operations
- *docker-compose.yml* — infrastructure setup (Postgres & Metabase)
- *requirements.txt* — Python dependencies
- *config.ini.example* — a template for Database Host/User and API URL
- *.env.example* — a template for Database passwords (Docker)

# How to open locally

1. Clone the repository

2. Create your local configuration files from the templates (*.env* and *config.ini*)

3. Launch PostgreSQL and Metabase using Docker:
```
docker-compose up -d
```
Metabase must be available at *http://localhost:3000*.

4. Install dependencies and run the main script to create database:
```
pip install -r requirements.txt
python3 daily_script.py
```