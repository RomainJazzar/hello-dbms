import os
from pathlib import Path

import pandas as pd
import mysql.connector
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

DATA_DIR = ROOT / "data"
CARBON_CSV = DATA_DIR / "carbon-footprint-data.csv"
WORLD_CSV = DATA_DIR / "countries of the world.csv"

ENERGY_COLS = ["Coal", "Gas", "Oil", "Hydro", "Renewable", "Nuclear"]

def connect(db=None):
    if not MYSQL_USER or not MYSQL_PASSWORD:
        raise RuntimeError("Missing MYSQL_USER / MYSQL_PASSWORD in .env")

    cfg = dict(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        autocommit=True,
    )
    if db:
        cfg["database"] = db
    return mysql.connector.connect(**cfg)

def map_continent(region: str) -> str:
    if not isinstance(region, str):
        return "Unknown"
    r = region.upper()
    if "EUROPE" in r:
        return "Europe"
    if "ASIA" in r or "NEAR EAST" in r:
        return "Asia"
    if "AFRICA" in r:
        return "Africa"
    if "OCEANIA" in r:
        return "Oceania"
    if "NORTH AMERICA" in r:
        return "North America"
    if "LATIN AMER" in r or "CARIBBEAN" in r:
        return "South America"
    return "Unknown"

def main():
    if not CARBON_CSV.exists():
        raise FileNotFoundError(f"Missing: {CARBON_CSV}")
    if not WORLD_CSV.exists():
        raise FileNotFoundError(f"Missing: {WORLD_CSV}")

    # 1) Load carbon CSV
    dfc = pd.read_csv(CARBON_CSV, sep=";", encoding="latin1")
    dfc.columns = [c.strip() for c in dfc.columns]
    dfc["Country"] = dfc["Country"].astype(str).str.strip()

    for c in ENERGY_COLS:
        dfc[c] = dfc[c].astype(str).str.replace(",", ".", regex=False).str.strip()
        dfc[c] = pd.to_numeric(dfc[c], errors="coerce").fillna(0.0)

    # 2) Load world CSV and map country -> continent
    dfw = pd.read_csv(WORLD_CSV, decimal=",", encoding="utf-8", engine="python")
    dfw.columns = [c.strip() for c in dfw.columns]
    dfw["Country"] = dfw["Country"].astype(str).str.strip()
    dfw["Continent"] = dfw["Region"].apply(map_continent)

    mapping = dfw[["Country", "Continent"]].drop_duplicates()

    # 3) Create databases + tables
    cnx = connect()
    cur = cnx.cursor()

    # create DBs
    cur.execute("CREATE DATABASE IF NOT EXISTS carbonfootprint;")
    cur.execute("CREATE DATABASE IF NOT EXISTS hello_dbms;")

    # hello_dbms.country_continent mapping table
    cur.execute("USE hello_dbms;")
    cur.execute("DROP TABLE IF EXISTS country_continent;")
    cur.execute("""
        CREATE TABLE country_continent (
            Country VARCHAR(255) PRIMARY KEY,
            Continent VARCHAR(50)
        );
    """)

    cur.executemany(
        "INSERT INTO country_continent (Country, Continent) VALUES (%s, %s)",
        [(r["Country"], r["Continent"]) for _, r in mapping.iterrows()]
    )

    # carbonfootprint tables
    cur.execute("USE carbonfootprint;")
    cur.execute("DROP TABLE IF EXISTS Country;")
    cur.execute("DROP TABLE IF EXISTS World;")

    cur.execute("""
        CREATE TABLE Country (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Country VARCHAR(255),
            Coal DOUBLE, Gas DOUBLE, Oil DOUBLE, Hydro DOUBLE, Renewable DOUBLE, Nuclear DOUBLE
        );
    """)

    cur.executemany(
        "INSERT INTO Country (Country, Coal, Gas, Oil, Hydro, Renewable, Nuclear) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        [(r["Country"], float(r["Coal"]), float(r["Gas"]), float(r["Oil"]),
          float(r["Hydro"]), float(r["Renewable"]), float(r["Nuclear"])) for _, r in dfc.iterrows()]
    )

    # 4) Build World table (continent averages)
    df_join = dfc.merge(mapping, on="Country", how="left")
    df_join["Continent"] = df_join["Continent"].fillna("Unknown")

    df_world = df_join.groupby("Continent")[ENERGY_COLS].mean().reset_index()
    df_world = df_world.rename(columns={"Continent": "Region"})

    cur.execute("""
        CREATE TABLE World (
            id INT AUTO_INCREMENT PRIMARY KEY,
            Region VARCHAR(255),
            Coal DOUBLE, Gas DOUBLE, Oil DOUBLE, Hydro DOUBLE, Renewable DOUBLE, Nuclear DOUBLE
        );
    """)

    cur.executemany(
        "INSERT INTO World (Region, Coal, Gas, Oil, Hydro, Renewable, Nuclear) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        [(r["Region"], float(r["Coal"]), float(r["Gas"]), float(r["Oil"]),
          float(r["Hydro"]), float(r["Renewable"]), float(r["Nuclear"])) for _, r in df_world.iterrows()]
    )

    cnx.close()

    print("✅ Done.")
    print(f"✅ carbonfootprint.Country rows: {len(dfc)}")
    print(f"✅ carbonfootprint.World rows: {len(df_world)}")

if __name__ == "__main__":
    main()
