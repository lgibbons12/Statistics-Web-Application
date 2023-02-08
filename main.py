from flask import Flask, redirect, url_for, render_template, request, session, flash 
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

#create application
app = Flask(__name__)

#application setup
app.secret_key="atccs"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app)

#set up sign in SQL Database
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        session['password'] = password

        if username == "admin" and password == "admin":
                session['admin'] = True
                session['logged in'] = True
                flash("Logged In As Admin")
        else:
            #SQLAlchemy
            found_username = users.query.filter_by(username=username, password=password).first()

            if found_username:
                session['logged in'] = True
                flash("Login Successful")
                return redirect(url_for("stats"))
            else:
                flash("Username and Password Do Not Match. Try Again!")
    return render_template("login.html")

@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "POST":
        new_username = request.form['username']
        new_password = request.form['password']

        usr = users(new_username, new_password)
        db.session.add(usr)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("create.html")


@app.route("/view")
def view():
    if 'admin' in session:
        if session['admin']:
            return render_template("view.html", values=users.query.all())
    else:
        flash("Sorry, you are not in admin mode and cannot access that page")
        return redirect(url_for("home"))
    


@app.route("/stats", methods = ["POST", "GET"])
def stats():
    if 'logged in' in session:
        if session['logged in'] == False:
            flash("You are not logged in. Please log in before using Stats Summarizer")
            return redirect(url_for("login"))
        else:
            if request.method == "POST":
                file = request.files['file']

                #pandas code
                df = pd.read_csv(file)
                session['df'] = df
                name = request.form['name']
                session['name'] = name
                return redirect(url_for("statsinprogress"))
            a="no stats"
            return render_template("stats.html", a=a)
    flash("You are not logged in. Please log in before using Stats Summarizer")
    return redirect(url_for("login"))

@app.route("/statsinprogress", methods = ["POST", "GET"])
def statsinprogress():
    if 'logged in' in session:
        if session['logged in'] == False:
            flash("You are not logged in. Please log in before using Stats Summarizer")
            return redirect(url_for("login"))
        else:
            if request.method == "POST":
                name = session['name']
                return render_template("statsinprogress.html", name=name)


@app.route("/logout")
def logout():
    
    #warning, info error are categories, second term you pass in flash
    flash("You have been logged out successfully :)", "info")
        
    session.pop("username", None)
    session.pop("password", None)
    session.pop("logged in", None)
    session.pop("admin", None)
    return redirect(url_for("login"))
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
