from flask import Flask, request
import sqlite3
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
    cur = conn.cursor()
    cur.execute("SELECT focus_score, session_hour FROM sessions")
    rows = cur.fetchall()
    conn.close()
    return rows

# ======================
# الصفحة الرئيسية
# ======================
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        score = request.form.get("score", "5")

        try:
            score = float(score)
        except:
            score = 5

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

            <h2>⏱️ تم بدء جلسة 25 دقيقة</h2>
            <h1 id="timer">25:00</h1>

            <script>
                let t = 25*60;

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

            <a href="/">رجوع</a>

        </div>
        """

    return """
    <div style="text-align:center;font-family:sans-serif;background:#f4f4f4;padding:40px">

        <h1>🧠 FocusMind</h1>

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

    </div>
    """

# ======================
# التقرير (بسيط)
# ======================
@app.route("/report")
def report():

    rows = get_data()

    if not rows:
        return "<h2 style='text-align:center'>لا توجد بيانات</h2>"

    scores = [r[0] for r in rows]
    hours = [r[1] for r in rows]

    avg = sum(scores) / len(scores)
    best_hour = max(set(hours), key=hours.count)

    return f"""
    <div style="text-align:center;font-family:sans-serif;padding:40px">

        <h1>📊 التقرير</h1>

        <p>⭐ المتوسط: {avg:.2f}</p>
        <p>⏰ أفضل وقت: {best_hour}:00</p>

        <br><br>

        <table border="1" style="margin:auto">
            <tr><th>التركيز</th><th>الوقت</th></tr>
            {''.join(f"<tr><td>{r[0]}</td><td>{r[1]}</td></tr>" for r in rows)}
        </table>

        <br><br>

        <a href="/">رجوع</a>

    </div>
    """

# ======================
# تشغيل Render
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
