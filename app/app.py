import os
from pathlib import Path

from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import Error
import pandas as pd
from dotenv import load_dotenv

# --- Paths ---
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CARBON_CSV = DATA_DIR / "carbon-footprint-data.csv"
WORLD_CSV = DATA_DIR / "countries of the world.csv"

# --- Load env from root reliably ---
load_dotenv(ROOT / ".env")

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB = "carbonfootprint"

# IPCC 2014 median values (gCO2/kWh)
FACTORS = {"Coal": 820, "Gas": 490, "Oil": 740, "Hydro": 24, "Renewable": 41, "Nuclear": 12}
HOURS_PER_YEAR = 24 * 365
TREE_ABSORPTION_KG_PER_YEAR = 25

app = Flask(__name__)


def db_conn():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=DB,
    )


# ---------- CSV fallback helpers ----------
def load_carbon_country_df() -> pd.DataFrame:
    df = pd.read_csv(CARBON_CSV, sep=";", encoding="latin1")
    df.columns = [c.strip() for c in df.columns]
    df["Country"] = df["Country"].astype(str).str.strip()

    for c in ["Coal", "Gas", "Oil", "Hydro", "Renewable", "Nuclear"]:
        df[c] = df[c].astype(str).str.replace(",", ".", regex=False).str.strip()
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    return df


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


def build_world_from_csv(country_df: pd.DataFrame) -> pd.DataFrame:
    # Use world CSV to map each country -> continent, then average the mix per continent
    w = pd.read_csv(WORLD_CSV, decimal=",", encoding="utf-8", engine="python")
    w.columns = [c.strip() for c in w.columns]
    # country names in this dataset often have spaces; strip
    w["Country"] = w["Country"].astype(str).str.strip()
    w["Continent"] = w["Region"].apply(map_continent)

    joined = country_df.merge(w[["Country", "Continent"]], on="Country", how="left")
    joined["Continent"] = joined["Continent"].fillna("Unknown")

    energy_cols = ["Coal", "Gas", "Oil", "Hydro", "Renewable", "Nuclear"]
    world = joined.groupby("Continent")[energy_cols].mean().reset_index()
    world = world.rename(columns={"Continent": "Region"})
    return world


# ---------- DB access with fallback ----------
def fetch_choices(mode: str):
    """mode: 'Country' or 'World'"""
    try:
        cnx = db_conn()
        cur = cnx.cursor()
        if mode == "World":
            cur.execute("SELECT DISTINCT Region FROM World ORDER BY Region;")
        else:
            cur.execute("SELECT DISTINCT Country FROM Country ORDER BY Country;")
        rows = cur.fetchall()
        cur.close()
        cnx.close()
        choices = [r[0] for r in rows]
        if choices:
            return choices, None
    except Error as e:
        # fall back to CSV
        pass

    # CSV fallback
    df_country = load_carbon_country_df()
    if mode == "World":
        df_world = build_world_from_csv(df_country)
        return sorted(df_world["Region"].dropna().unique().tolist()), "CSV fallback (World derived)"
    return sorted(df_country["Country"].dropna().unique().tolist()), "CSV fallback"


def fetch_preview(mode: str, limit: int = 8):
    try:
        cnx = db_conn()
        cur = cnx.cursor(dictionary=True)
        table = "World" if mode == "World" else "Country"
        cur.execute(f"SELECT * FROM `{table}` LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        cnx.close()
        if rows:
            return rows, None
    except Error:
        pass

    # CSV fallback
    df_country = load_carbon_country_df()
    if mode == "World":
        df_world = build_world_from_csv(df_country).head(limit)
        return df_world.to_dict(orient="records"), "CSV fallback (World derived)"
    return df_country.head(limit).to_dict(orient="records"), "CSV fallback"


def fetch_mix(mode: str, selected: str):
    try:
        cnx = db_conn()
        cur = cnx.cursor(dictionary=True)
        if mode == "World":
            cur.execute("SELECT * FROM World WHERE Region=%s LIMIT 1", (selected,))
        else:
            cur.execute("SELECT * FROM Country WHERE Country=%s LIMIT 1", (selected,))
        row = cur.fetchone()
        cur.close()
        cnx.close()
        if row:
            return row
    except Error:
        pass

    # CSV fallback
    df_country = load_carbon_country_df()
    if mode == "World":
        df_world = build_world_from_csv(df_country)
        row = df_world[df_world["Region"] == selected]
        return row.iloc[0].to_dict() if not row.empty else None

    row = df_country[df_country["Country"] == selected]
    return row.iloc[0].to_dict() if not row.empty else None


def compute_table(mix_row: dict):
    out = []
    total_intensity = 0.0  # gCO2/kWh
    for source, factor in FACTORS.items():
        pct = float(mix_row.get(source, 0.0) or 0.0)
        contrib = (pct / 100.0) * factor
        total_intensity += contrib
        out.append({"source": source, "pct": pct, "median": factor, "contrib": contrib})
    return out, total_intensity


@app.route("/", methods=["GET", "POST"])
def index():
    mode = request.form.get("mode", "Country")
    selected = request.form.get("selected", None)
    kw = request.form.get("kw", "1")

    choices, choice_note = fetch_choices(mode)
    preview, preview_note = fetch_preview(mode)

    # Auto-pick first option so UI is never blank
    if not selected and choices:
        selected = choices[0]

    result = None
    if request.method == "POST" and selected:
        row = fetch_mix(mode, selected)
        if row:
            table, intensity_g = compute_table(row)
            intensity_kg = intensity_g / 1000.0  # ✅ g -> kg

            try:
                kw_val = float(kw)
            except ValueError:
                kw_val = 1.0

            annual_kg = intensity_kg * HOURS_PER_YEAR * kw_val
            trees = annual_kg / TREE_ABSORPTION_KG_PER_YEAR

            result = {
                "mode": mode,
                "selected": selected,
                "kw": kw_val,
                "intensity_g_per_kwh": intensity_g,
                "annual_kg": annual_kg,
                "trees": trees,
                "table": table,
            }

    return render_template(
        "index.html",
        mode=mode,
        choices=choices,
        selected=selected,
        kw=kw,
        preview=preview,
        result=result,
        choice_note=choice_note,
        preview_note=preview_note,
    )


if __name__ == "__main__":
    app.run(debug=True)
