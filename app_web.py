from flask import Flask
import sqlite3
import pandas as pd

app = Flask(__name__)

def get_data():
    conn = sqlite3.connect("focusmind.db")
    df = pd.read_sql_query("SELECT * FROM sessions", conn)
    conn.close()
    return df

@app.route("/")
def home():
    df = get_data()

    if df.empty:
        return "لا توجد بيانات"

    avg = df["focus_score"].mean()

    return f"""
    <h1>FocusMind</h1>
    <p>متوسط التركيز: {avg:.2f}</p>
    <a href='/report'>التقرير</a>
    """

@app.route("/report")
def report():
    df = get_data()
    return df.to_html()

if __name__ == "__main__":
    app.run()
    