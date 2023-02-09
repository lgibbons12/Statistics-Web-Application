from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


fig,ax = plt.subplots(figsize=(6, 6))
ax = sns.set_style(style="darkgrid")
#To-Do
#finish all statistical summaries
#add all session data to the logout page
#comment everything
#commit everything
#create READMe
#create log of user interaction
#push onto linode





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
                
                dataframe = pd.read_csv(file)


                with open("df.json", "r") as f:
                    data = json.load(f)
                data = dataframe.to_json(orient = 'index')
                with open('df.json', 'w') as f:
                    json.dump(data, f, indent=2)


                session['in progress'] = True
                session['stats-form'] = 0
                return redirect(url_for("statsinprogress"))
            
            return render_template("stats.html")
    flash("You are not logged in. Please log in before using Stats Summarizer")
    return redirect(url_for("login"))

@app.route("/statsinprogress", methods = ["POST", "GET"])
def statsinprogress():
    means_list = []
    medians_list = []
    if 'logged in' in session:
        if session['logged in'] == False:
            flash("You are not logged in. Please log in before using Stats Summarizer")
            return redirect(url_for("login"))
        else:
            if 'in progress' in session:
                if session['in progress'] == True:
                    with open("df.json", "r") as f:
                            data = json.load(f)
                    df = pd.read_json(data, orient="index")
                    columns_list = []
                    for i in range(len(df.columns)):
                        columns_list.append(df.columns[i])
                    if columns_list[0] == "Unnamed: 0":
                        columns_list.remove("Unnamed: 0")
                    
                    cool = session['stats-form']
                    
                    if request.method == "POST":
                        re_run = False
                        if 'return' in request.form:
                            
                            session['stats-form'] = 0
                            re_run = True
                                
                        
                        text_to_return = ""
                        
                        for column in df:
                            if df[column].dtype != 'int64' and df[column].dtype != 'float64':
                                columns_list.remove(column)
                        if session['stats-form'] == 0 and re_run == False:
                            output = request.form['firstselect']

                            if output == "Quick Summary":
                                text_to_return = f"This dataset has {len(columns_list)} numerical columns, all named: {columns_list}"
                                
                                for column in columns_list:
                                    means_list.append(df[column].mean())
                                
                                for column in columns_list:
                                    medians_list.append(df[column].median())
                            elif output == "Relationship":
                                session['stats-form'] = 2
                            elif output == "Graph":
                                session['stats-form'] = 3
                        
                        
                        
                        elif session["stats-form"] == 2 or session['stats-form'] == 3:
                            print("h1")
                            if 'relselect' in request.form:
                                relselect = request.form.getlist('relselect')
                            else:
                                relselect = ["", ""]
                            
                            if session['stats-form'] == 2:
                                correlation = df[relselect[0]].corr(df[relselect[1]])
                                correlation = round(correlation, 3)
                                if correlation > 0:
                                    sign = "positive, which means that as one goes up so does the other. "
                                else:
                                    sign = "negative, which means that as one goes up, the other goes down. "
                                if abs(correlation) > 0.5:
                                    magnitude = f"The significance of the relationship between {relselect[0]} and {relselect[1]} is high, with a correlation of {correlation}, which means they are closely associated"
                                else:
                                    magnitude = f"The significance of the relationship between {relselect[0]} and {relselect[1]} is low, with a correlation of {correlation}, which means they are not closely associated"
                                text_to_return = f"The correlation test shows the the correlation between {relselect[0]} and {relselect[1]} is {sign} {magnitude}"
                            else:
                                session['plotx'] = relselect[0]
                                session['ploty'] = relselect[1]
                                return redirect(url_for("graph"))
                            
                        cool = session['stats-form']
                        
                        

                        
                        return render_template("statsinprogress.html", means = means_list, medians = medians_list, url='/static/new_plot.png', show=cool, list = columns_list, text=text_to_return)
                    else:
                        session['stats-form'] = 0
                        return render_template("statsinprogress.html", means = means_list, medians = medians_list, show=cool, list=columns_list)
                else:
                    return render_template("statsinprogress.html")
            else:
                flash("No data entered, please submit a csv file")
                return redirect(url_for("stats"))
    else:
        flash("You are not logged in. Please log in before using Stats Summarizer")
        return redirect(url_for("login"))

@app.route('/get-plot', methods = ['POST', 'GET'])
def get_plot():
    if request.method == "POST":
        if 'return' in request.form:
            session['stats-form'] = 0
            return redirect(url_for("statsinprogress"))

        if 'relselect' in request.form:
            relselect = request.form.getlist('relselect')
        else:
            relselect = ["", ""]
        with open("df.json", "r") as f:
                data = json.load(f)
        df = pd.read_json(data, orient="index")
        plt.scatter(df[relselect[0]], df[relselect[1]])
        plt.title(f"{relselect[1]} vs. {relselect[0]}")
        plt.xlabel(relselect[0])
        plt.ylabel(relselect[1])
        plt.savefig('static/my_plot.png')
        return render_template('graph.html', plot_url = "static/my_plot.png")
    else:
        flash("Please Go Through Stats In Progress To Get To The Graph")
        return redirect(url_for("stats"))


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
