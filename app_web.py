from flask import Flask, request
import sqlite3
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# ======================
# قاعدة البيانات الآمنة
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

    best_html = ""
    if not df.empty:
        try:
            best_hour = int(df.groupby("session_hour")["focus_score"].mean().idxmax())
            best_html = f"<p>⏰ أفضل وقت للمذاكرة: <b>{best_hour}:00</b></p>"
        except:
            best_html = "<p>⏰ لا يوجد تحليل كافي</p>"
    else:
        best_html = "<p>⏰ لا توجد بيانات بعد</p>"

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

            <h2>⏱️ جلسة تركيز بدأت</h2>
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
                        alert("🎉 انتهت جلسة التركيز");
                        window.location.href="/report";
                    }
                },1000);
            </script>

            <p>ركز الآن 💪</p>

        </div>
        """

    return f"""
    <div style="text-align:center;font-family:sans-serif;background:#f2f4f8;padding:40px">

        <h1>🧠 FocusMind</h1>

        {best_html}

        <form method="POST">

            <input name="score" type="number" min="1" max="10"
            placeholder="مستوى التركيز (1-10)"
            style="padding:10px;width:220px;border-radius:10px"><br><br>

            <button style="padding:12px 25px;background:#2196F3;color:white;border:none;border-radius:10px">
                🚀 ابدأ جلسة 25 دقيقة
            </button>

        </form>

        <br>

        <a href="/report">📊 التقرير</a>
        <br><br>

        <a href="/reset" style="color:red">🗑️ تصفير البيانات</a>

    </div>
    """

# ======================
# التقرير الاحترافي
# ======================
@app.route("/report")
def report():

    df = get_data()

    if df.empty:
        return "<h2 style='text-align:center;font-family:sans-serif'>لا توجد بيانات بعد</h2>"

    avg = df["focus_score"].mean()
    best_hour = int(df.groupby("session_hour")["focus_score"].mean().idxmax())

    xp = len(df) * 10
    level = xp // 50

    mood = "🔥 ممتاز" if avg >= 7 else "😐 متوسط" if avg >= 4 else "😴 يحتاج تحسين"

    table_html = df.to_html(index=False)

    return f"""
    <div style="font-family:sans-serif;background:#f5f6fa;padding:40px;text-align:center">

        <h1>📊 تقرير الأداء</h1>

        <div style="display:flex;justify-content:center;gap:15px;flex-wrap:wrap;margin-top:20px">

            <div style="background:white;padding:20px;border-radius:12px;width:180px">
                <h3>⭐ XP</h3>
                <p>{xp}</p>
            </div>

            <div style="background:white;padding:20px;border-radius:12px;width:180px">
                <h3>🏆 Level</h3>
                <p>{level}</p>
            </div>

            <div style="background:white;padding:20px;border-radius:12px;width:180px">
                <h3>📈 المتوسط</h3>
                <p>{avg:.2f}</p>
            </div>

        </div>

        <br>

        <h3>🧠 الحالة: {mood}</h3>

        <h3>⏰ أفضل وقت: {best_hour}:00</h3>

        <br>

        <div style="background:white;padding:15px;border-radius:10px;overflow:auto">
            {table_html}
        </div>

        <br><br>

        <a href="/" style="padding:10px 20px;background:#2196F3;color:white;text-decoration:none;border-radius:10px">
            رجوع
        </a>

    </div>
    """

# ======================
# تصفير آمن
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
    
