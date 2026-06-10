from flask import Flask, request, redirect
import sqlite3
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# إنشاء قاعدة البيانات
def init_db():
    conn = sqlite3.connect("focusmind.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY,
        focus_score REAL,
        session_hour INTEGER
    )
    """)
    conn.close()

init_db()

# الصفحة الرئيسية (إدخال البيانات)
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        score = float(request.form["score"])
        hour = datetime.now().hour

        conn = sqlite3.connect("focusmind.db")
        conn.execute("INSERT INTO sessions (focus_score, session_hour) VALUES (?, ?)",
                     (score, hour))
        conn.commit()
        conn.close()

        return redirect("/report")

    return """
    <h1>FocusMind 🧠</h1>
    <form method="POST">
        <label>مستوى التركيز (من 1 إلى 10):</label><br>
        <input name="score" type="number" step="0.1" min="1" max="10" required>
        <br><br>
        <button type="submit">ابدأ / سجل الجلسة</button>
    </form>
    """

# التقرير
@app.route("/report")
def report():
    conn = sqlite3.connect("focusmind.db")
    df = pd.read_sql_query("SELECT * FROM sessions", conn)
    conn.close()

    if df.empty:
        return "<h2>لا توجد بيانات بعد</h2>"

    avg = df["focus_score"].mean()
    best_hour = df.groupby("session_hour")["focus_score"].mean().idxmax()

    return f"""
    <h1>📊 التقرير</h1>
    <p>متوسط التركيز: {avg:.2f}</p>
    <p>أفضل وقت للمذاكرة: الساعة {best_hour}</p>
    <br>
    {df.to_html()}
    <br>
    <a href="/">رجوع</a>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

