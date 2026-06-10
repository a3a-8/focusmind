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
        best_html = "<p>⏰ لا توجد بيانات بعد</p>"

    if request.method == "POST":
        score = float(request.form["score"])
        hour = datetime.now().hour

        conn = sqlite3.connect("focusmind.db")
        conn.execute(
            "INSERT INTO sessions VALUES (NULL, ?, ?)",
            (score, hour)
        )
        conn.commit()
        conn.close()

        return """
        <div style="text-align:center;font-family:sans-serif;padding:40px">
            <h2>⏱️ جلسة بدأت</h2>
            <h1 id="timer">25:00</h1>

            <script>
                let t = 25 * 60;

                let x = setInterval(()=>{
                    let m = Math.floor(t/60);
                    let s = t%60;

                    document.getElementById("timer").innerHTML =
                    m + ":" + (s<10?"0"+s:s);

                    t--;

                    if(t<0){
                        clearInterval(x);
                        alert("🎉 انتهت الجلسة");
                        window.location.href="/report";
                    }
                },1000);
            </script>

            <br><br>
            <a href="/">رجوع</a>
        </div>
        """

    return f"""
    <div style="text-align:center;font-family:sans-serif;background:#f4f4f4;padding:40px">

        <h1>🔥 FocusMind</h1>

        {best_html}

        <form method="POST">

            <input name="score" type="number" min="1" max="10"
            placeholder="مستوى التركيز"
            style="padding:10px;width:200px;border-radius:10px"><br><br>

            <button style="padding:10px 20px;background:#2196F3;color:white;border:none;border-radius:10px">
                🚀 ابدأ جلسة 25 دقيقة
            </button>

        </form>

        <br>

        <a href="/report">📊 التقرير</a>
        <br><br>

        <a href="/reset" style="padding:10px 20px;background:red;color:white;text-decoration:none;border-radius:10px">
            🗑️ تصفير البيانات
        </a>

    </div>
    """

# ======================
# التقرير
# ======================
@app.route("/report")
def report():

    df = get_data()

    if df.empty:
        return "<h2 style='text-align:center'>لا توجد بيانات</h2>"

    avg = df["focus_score"].mean()
    best_hour = df.groupby("session_hour")["focus_score"].mean().idxmax()

    xp = len(df) * 10
    level = xp // 50

    return f"""
    <div style="text-align:center;font-family:sans-serif;padding:40px">

        <h1>📊 لوحة التحكم</h1>

        <h2>⭐ XP: {xp}</h2>
        <h2>🏆 Level: {level}</h2>
        <h3>📈 المتوسط: {avg:.2f}</h3>

        <p>⏰ أفضل وقت: {best_hour}:00</p>

        <br><br>

        {df.to_html(index=False)}

        <br><br>

        <a href="/" style="padding:10px 20px;background:#2196F3;color:white;text-decoration:none;border-radius:10px">
            رجوع
        </a>

    </div>
    """

# ======================
# تصفير البيانات
# ======================
@app.route("/reset")
def reset():
    conn = sqlite3.connect("focusmind.db")
    conn.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()

    return """
    <div style="text-align:center;font-family:sans-serif;padding:40px">
        <h2>🗑️ تم تصفير البيانات</h2>
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
    
