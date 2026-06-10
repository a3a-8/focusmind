from flask import Flask, request
import sqlite3
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# ======================
# قاعدة البيانات
# ======================
def init_db():
    conn = sqlite3.connect("focusmind.db")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        focus_score REAL,
        session_hour INTEGER
    )
    """)
    conn.close()

init_db()

def get_data():
    conn = sqlite3.connect("focusmind.db")
    df = pd.read_sql_query("SELECT * FROM sessions", conn)
    conn.close()
    return df

# ======================
# الصفحة الرئيسية
# ======================
@app.route("/", methods=["GET", "POST"])
def home():

    df = get_data()

    if not df.empty:
        best_hour = df.groupby("session_hour")["focus_score"].mean().idxmax()
        best_html = f"<p>⏰ أفضل وقت للمذاكرة: <b>{best_hour}:00</b></p>"
    else:
        best_html = "<p>⏰ أفضل وقت للمذاكرة: لا يوجد بيانات بعد</p>"

    if request.method == "POST":
        score = float(request.form["score"])
        hour = datetime.now().hour
        distracted = request.form["distracted"]

        conn = sqlite3.connect("focusmind.db")
        conn.execute(
            "INSERT INTO sessions (focus_score, session_hour) VALUES (?, ?)",
            (score, hour)
        )
        conn.commit()
        conn.close()

        return """
        <div style="text-align:center;font-family:sans-serif;padding:40px">

            <h2>⏱️ جلسة تركيز بدأت</h2>
            <h1 id="timer">25:00</h1>

            <p>ركز الآن 💪</p>

            <script>
                let time = 25 * 60;

                let x = setInterval(() => {
                    let m = Math.floor(time / 60);
                    let s = time % 60;

                    document.getElementById("timer").innerHTML =
                        m + ":" + (s < 10 ? "0" + s : s);

                    time--;

                    if (time < 0) {
                        clearInterval(x);
                        alert("انتهت جلسة التركيز 🎉");
                        window.location.href = "/report";
                    }
                }, 1000);
            </script>

            <br><br>
            <a href="/" style="padding:10px 20px;background:#4CAF50;color:white;text-decoration:none;border-radius:10px">
                رجوع
            </a>

        </div>
        """

    return f"""
    <div style="text-align:center;font-family:sans-serif;background:#f5f5f5;padding:40px">

        <h1>FocusMind 🧠</h1>

        {best_html}

        <form method="POST">

            <label>مستوى التركيز (1 - 10)</label><br><br>

            <input name="score" type="number" step="0.1" min="1" max="10"
            style="padding:10px;width:200px;border-radius:10px"><br><br>

            <label>هل أنت مشتت؟</label><br><br>

            <select name="distracted"
            style="padding:10px;width:200px;border-radius:10px">
                <option value="no">لا</option>
                <option value="yes">نعم</option>
            </select>

            <br><br>

            <button type="submit"
            style="padding:10px 20px;background:#2196F3;color:white;border:none;border-radius:10px">
                🚀 ابدأ جلسة 25 دقيقة
            </button>

        </form>

        <br>
        <a href="/report">📊 التقرير</a>

    </div>
    """

# ======================
# التقرير
# ======================
@app.route("/report")
def report():
    conn = sqlite3.connect("focusmind.db")
    df = pd.read_sql_query("SELECT * FROM sessions", conn)
    conn.close()

    if df.empty:
        return "<h2 style='text-align:center'>لا توجد بيانات بعد</h2>"

    avg = df["focus_score"].mean()
    best_hour = df.groupby("session_hour")["focus_score"].mean().idxmax()

    return f"""
    <div style="text-align:center;font-family:sans-serif;padding:40px">

        <h1>📊 التقرير</h1>

        <p>متوسط التركيز: <b>{avg:.2f}</b></p>
        <p>أفضل وقت للمذاكرة: <b>{best_hour}:00</b></p>

        <br>

        {df.to_html()}

        <br><br>

        <a href="/" style="padding:10px 20px;background:#2196F3;color:white;text-decoration:none;border-radius:10px">
            رجوع
        </a>

    </div>
    """

# ======================
# تشغيل Render
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

