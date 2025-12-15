"""
Initialize MySQL for the Hello DBMS+ project.

Creates:
- hello_dbms.world (from countries of the world.csv)
- carbonfootprint.Country (from carbon-footprint-data.csv)
- carbonfootprint.World (derived by continent aggregation)
- uefa tables (small dataset for jobs)
- somecompany database (placeholder; job8.sql recreates)
"""

import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

WORLD_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "countries of the world.csv")
CARBON_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "carbon-footprint-data.csv")

# IPCC medians (gCO2/kWh)
FACTORS = {
    "Coal": 820,
    "Gas": 490,
    "Oil": 740,
    "Hydro": 24,
    "Renewable": 41,
    "Nuclear": 12
}

def connect(db=None):
    cfg = dict(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        autocommit=True
    )
    if db:
        cfg["database"] = db
    return mysql.connector.connect(**cfg)

def exec_many(cur, statements):
    for st in statements:
        cur.execute(st)

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
    cnx = connect()
    cur = cnx.cursor()

    # -------- hello_dbms.world --------
    exec_many(cur, [
        "CREATE DATABASE IF NOT EXISTS hello_dbms;",
        "USE hello_dbms;",
        "DROP TABLE IF EXISTS world;"
    ])

    dfw = pd.read_csv(WORLD_CSV, decimal=",", encoding="utf-8", engine="python")
    dfw.columns = [c.strip() for c in dfw.columns]

    rename = {
        "Country": "Name",
        "Region": "Region",
        "Population": "Population",
        "Area (sq. mi.)": "SurfaceArea",
        "Pop. Density (per sq. mi.)": "PopDensity",
        "Coastline (coast/area ratio)": "Coastline",
        "Net migration": "NetMigration",
        "Infant mortality (per 1000 births)": "InfantMortality",
        "GDP ($ per capita)": "GDP",
        "Literacy (%)": "Literacy",
        "Phones (per 1000)": "Phones",
        "Arable (%)": "Arable",
        "Crops (%)": "Crops",
        "Other (%)": "Other",
        "Climate": "Climate",
        "Birthrate": "Birthrate",
        "Deathrate": "Deathrate",
        "Agriculture": "Agriculture",
        "Industry": "Industry",
        "Service": "Service"
    }
    dfw = dfw.rename(columns=rename)
    dfw["Continent"] = dfw["Region"].apply(map_continent)

    num_cols = ["Population","SurfaceArea","PopDensity","Coastline","NetMigration","InfantMortality",
                "GDP","Literacy","Phones","Arable","Crops","Other","Climate","Birthrate","Deathrate",
                "Agriculture","Industry","Service"]
    for c in num_cols:
        if c in dfw.columns:
            dfw[c] = pd.to_numeric(dfw[c], errors="coerce")

    cur.execute("""
    CREATE TABLE world (
      id INT AUTO_INCREMENT PRIMARY KEY,
      Name VARCHAR(255),
      Region VARCHAR(255),
      Continent VARCHAR(50),
      Population BIGINT,
      SurfaceArea DOUBLE,
      PopDensity DOUBLE,
      Coastline DOUBLE,
      NetMigration DOUBLE,
      InfantMortality DOUBLE,
      GDP DOUBLE,
      Literacy DOUBLE,
      Phones DOUBLE,
      Arable DOUBLE,
      Crops DOUBLE,
      Other DOUBLE,
      Climate DOUBLE,
      Birthrate DOUBLE,
      Deathrate DOUBLE,
      Agriculture DOUBLE,
      Industry DOUBLE,
      Service DOUBLE
    );
    """)

    insert_cols = ["Name","Region","Continent"] + num_cols
    placeholders = ",".join(["%s"] * len(insert_cols))
    sql = f"INSERT INTO world ({','.join(insert_cols)}) VALUES ({placeholders})"
    data = []
    for _, r in dfw.iterrows():
        row = []
        for c in insert_cols:
            v = r.get(c)
            if pd.isna(v):
                v = None
            row.append(v)
        data.append(tuple(row))
    cur.executemany(sql, data)
    print(f"✅ hello_dbms.world imported: {len(data)} rows")

    # -------- carbonfootprint --------
    exec_many(cur, [
        "CREATE DATABASE IF NOT EXISTS carbonfootprint;",
        "USE carbonfootprint;",
        "DROP TABLE IF EXISTS `Country`;",
        "DROP TABLE IF EXISTS `World`;",
        "DROP TABLE IF EXISTS factors;"
    ])

    dfc = pd.read_csv(CARBON_CSV, sep=";", encoding="latin1")
    dfc.columns = [c.strip() for c in dfc.columns]
    energy_cols = ["Coal","Gas","Oil","Hydro","Renewable","Nuclear"]
    for c in energy_cols:
        dfc[c] = dfc[c].astype(str).str.replace(",", ".", regex=False)
        dfc[c] = pd.to_numeric(dfc[c], errors="coerce").fillna(0.0)

    cur.execute("""
    CREATE TABLE `Country` (
      id INT AUTO_INCREMENT PRIMARY KEY,
      Country VARCHAR(255),
      Coal DOUBLE, Gas DOUBLE, Oil DOUBLE, Hydro DOUBLE, Renewable DOUBLE, Nuclear DOUBLE
    );
    """)
    cur.executemany(
        "INSERT INTO `Country` (Country,Coal,Gas,Oil,Hydro,Renewable,Nuclear) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        [(
            str(r["Country"]).strip(),
            float(r["Coal"]), float(r["Gas"]), float(r["Oil"]),
            float(r["Hydro"]), float(r["Renewable"]), float(r["Nuclear"])
        ) for _, r in dfc.iterrows()]
    )
    print(f"✅ carbonfootprint.Country imported: {len(dfc)} rows")

    # derive World table by continent
    cnx2 = connect("hello_dbms")
    df_region = pd.read_sql("SELECT Name, Continent FROM world", cnx2)
    cnx2.close()

    df_join = dfc.merge(df_region, left_on="Country", right_on="Name", how="left")
    df_join["Continent"] = df_join["Continent"].fillna("Unknown")
    df_world_mix = df_join.groupby("Continent")[energy_cols].mean().reset_index()

    cur.execute("""
    CREATE TABLE `World` (
      id INT AUTO_INCREMENT PRIMARY KEY,
      Region VARCHAR(255),
      Coal DOUBLE, Gas DOUBLE, Oil DOUBLE, Hydro DOUBLE, Renewable DOUBLE, Nuclear DOUBLE
    );
    """)
    cur.executemany(
        "INSERT INTO `World` (Region,Coal,Gas,Oil,Hydro,Renewable,Nuclear) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        [(
            str(r["Continent"]),
            float(r["Coal"]), float(r["Gas"]), float(r["Oil"]),
            float(r["Hydro"]), float(r["Renewable"]), float(r["Nuclear"])
        ) for _, r in df_world_mix.iterrows()]
    )
    print(f"✅ carbonfootprint.World derived: {len(df_world_mix)} rows")

    cur.execute("""
    CREATE TABLE factors (
      source VARCHAR(50) PRIMARY KEY,
      median_gco2_per_kwh DOUBLE
    );
    """)
    cur.executemany(
        "INSERT INTO factors (source, median_gco2_per_kwh) VALUES (%s,%s)",
        [(k, v) for k, v in FACTORS.items()]
    )

    # -------- uefa dataset --------
    exec_many(cur, [
        "CREATE DATABASE IF NOT EXISTS uefa;",
        "USE uefa;",
        "DROP TABLE IF EXISTS goal;",
        "DROP TABLE IF EXISTS game;",
        "DROP TABLE IF EXISTS eteam;"
    ])

    cur.execute("CREATE TABLE eteam (id VARCHAR(3) PRIMARY KEY, teamname VARCHAR(60), coach VARCHAR(60));")
    cur.execute("CREATE TABLE game (id INT PRIMARY KEY, mdate DATE, stadium VARCHAR(120), team1 VARCHAR(3), team2 VARCHAR(3));")
    cur.execute("CREATE TABLE goal (matchid INT, teamid VARCHAR(3), player VARCHAR(60), gtime INT, PRIMARY KEY (matchid, teamid, player, gtime));")

    teams = [
        ("POL","Poland","Franciszek Smuda"),
        ("GRE","Greece","Fernando Santos"),
        ("GER","Germany","Joachim Löw"),
        ("POR","Portugal","Paulo Bento"),
        ("FRA","France","Laurent Blanc"),
        ("RUS","Russia","Dick Advocaat"),
        ("CZE","Czech Republic","Michal Bílek")
    ]
    cur.executemany("INSERT INTO eteam VALUES (%s,%s,%s)", teams)

    games = [
        (1001,"2012-06-08","National Stadium, Warsaw","POL","GRE"),
        (1003,"2012-06-09","Metalist Stadium","GER","POR"),
        (1012,"2012-06-16","PGE Arena, Gdansk","GER","GRE"),
        (1020,"2012-06-19","National Stadium, Warsaw","FRA","POL"),
        (1021,"2012-06-20","Stadion Miejski (Wroclaw)","GRE","RUS"),
    ]
    cur.executemany("INSERT INTO game VALUES (%s,%s,%s,%s,%s)", games)

    goals = [
        (1001,"POL","Robert Lewandowski",17),
        (1001,"GRE","Dimitris Salpingidis",51),
        (1003,"GER","Mario Gomez",72),
        (1012,"GER","Lars Bender",10),
        (1012,"GER","Mario Gomez",44),
        (1020,"FRA","Karim Benzema",22),
        (1020,"FRA","Karim Benzema",63),
        (1021,"RUS","Alan Dzagoev",15),
    ]
    cur.executemany("INSERT INTO goal VALUES (%s,%s,%s,%s)", goals)
    print("✅ uefa dataset created")

    # -------- somecompany placeholder --------
    cur.execute("CREATE DATABASE IF NOT EXISTS somecompany;")
    print("✅ somecompany database created")

    cur.close()
    cnx.close()
    print("\\nAll done ✅\\n")

if __name__ == "__main__":
    main()
