import os
from flask import Flask, render_template, request
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB = "carbonfootprint"

# IPCC 2014 median values (gCO2/kWh)
FACTORS = {"Coal": 820, "Gas": 490, "Oil": 740, "Hydro": 24, "Renewable": 41, "Nuclear": 12}

HOURS_PER_YEAR = 24 * 365
TREE_ABSORPTION_KG_PER_YEAR = 25  # order-of-magnitude assumption

app = Flask(__name__)

def db_conn():
    return mysql.connector.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=DB
    )

def fetch_preview(table_name: str, limit: int = 5):
    cnx = db_conn()
    cur = cnx.cursor(dictionary=True)
    cur.execute(f"SELECT * FROM `{table_name}` LIMIT %s", (limit,))
    rows = cur.fetchall()
    cur.close()
    cnx.close()
    return rows

def fetch_choices(table_name: str, col: str):
    cnx = db_conn()
    cur = cnx.cursor()
    cur.execute(f"SELECT DISTINCT `{col}` FROM `{table_name}` ORDER BY `{col}`")
    choices = [r[0] for r in cur.fetchall()]
    cur.close()
    cnx.close()
    return choices

def fetch_mix(table_name: str, key_col: str, key_val: str):
    cnx = db_conn()
    cur = cnx.cursor(dictionary=True)
    cur.execute(f"SELECT * FROM `{table_name}` WHERE `{key_col}`=%s LIMIT 1", (key_val,))
    row = cur.fetchone()
    cur.close()
    cnx.close()
    return row

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
    mode = request.form.get("mode", "Country")  # Country or World
    selected = request.form.get("selected", None)
    kw = request.form.get("kw", "1")

    if mode == "World":
        choices = fetch_choices("World", "Region")
        key_col = "Region"
        preview = fetch_preview("World")
    else:
        choices = fetch_choices("Country", "Country")
        key_col = "Country"
        preview = fetch_preview("Country")

    result = None
    if request.method == "POST" and selected:
        row = fetch_mix(mode, key_col, selected)
        if row:
            table, intensity_g = compute_table(row)

            # annual emissions: intensity (kg/kWh) * (kW * hours/year)
            intensity_kg_per_kwh = intensity_g / 1_000_000  # g -> kg
            try:
                kw_val = float(kw)
            except ValueError:
                kw_val = 1.0
            annual_kg = intensity_kg_per_kwh * HOURS_PER_YEAR * kw_val
            trees = annual_kg / TREE_ABSORPTION_KG_PER_YEAR if TREE_ABSORPTION_KG_PER_YEAR else 0.0

            result = {
                "mode": mode,
                "selected": selected,
                "kw": kw_val,
                "intensity_g_per_kwh": intensity_g,
                "annual_kg": annual_kg,
                "trees": trees,
                "table": table,
            }

    return render_template("index.html", mode=mode, choices=choices, selected=selected, kw=kw, preview=preview, result=result)

if __name__ == "__main__":
    app.run(debug=True)
