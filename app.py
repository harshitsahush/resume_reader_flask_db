from flask import Flask, redirect, render_template, jsonify, request, session
from flask_session import Session
import pandas as pd
from utils import *


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "dev"
Session()


@app.route("/", methods = ["GET", "POST"])
def index():
    return redirect("/process_resume")


@app.route("/process_resume", methods = ["GET", "POST"])
def process():
    if(request.method == "POST"):
        #if uid not in session_var, create and store
        if("uid" not in session):
            session["uid"] = str(uuid.uuid4())
        
        conn = sqlite3.connect("resume_db")
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS resume_data (uid TEXT, name TEXT, email TEXT, contact TEXT, skills TEXT, experience TEXT)"
        )
        conn.commit()


        pdf = request.files['resume_file']
        text = get_pdf_text(pdf)
        response = query_response(text)
        response_dict = json.loads(response)

        save_to_db(conn, cursor, session["uid"], response_dict)
        db_res = fetch_from_db(conn, cursor, session["uid"])

        # print(db_res)

        db_res = pd.DataFrame(db_res)

        return render_template("upload_resume.html", res = db_res)

    else:
        return render_template("upload_resume.html",  res = "")


if(__name__ == "__main__"):
    app.run(debug = True)