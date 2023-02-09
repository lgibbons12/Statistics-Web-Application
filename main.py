#imports
from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import json

#import to make graphing work
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

#set up matplotlib plot
fig,ax = plt.subplots(figsize=(6, 6))
ax = sns.set_style(style="darkgrid")


#create application
app = Flask(__name__)

#application setup with SQL Alchemy
app.secret_key="atccs"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app)

#set up sign in SQL Database
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    #create username and password columns
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password


#home page
@app.route("/")
def home():
    return render_template("index.html")

#login page
@app.route("/login", methods=["POST", "GET"])
def login():
    #if the form is filled out
    if request.method == "POST":

        #get username and password from form
        session.permanent = True
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        session['password'] = password

        #check for admin login
        if username == "admin" and password == "admin":
                session['admin'] = True
                session['logged in'] = True
                flash("Logged In As Admin")
        else:
            #SQLAlchemy
            found_username = users.query.filter_by(username=username, password=password).first()

            #if username found, log user in and bring them to stats page
            if found_username:
                session['logged in'] = True
                flash("Login Successful")
                return redirect(url_for("stats"))
            else:
                #if not, show that it did not work
                flash("Username and Password Do Not Match. Try Again!")
    return render_template("login.html")

#create account page
@app.route("/create", methods=["POST", "GET"])
def create():
    if request.method == "POST":
        #get entered username and password
        new_username = request.form['username']
        new_password = request.form['password']

        #add user to database
        usr = users(new_username, new_password)
        db.session.add(usr)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("create.html")

#view users page
@app.route("/view")
def view():
    #only show if logged in as admin
    if 'admin' in session:
        if session['admin']:
            return render_template("view.html", values=users.query.all())
    else:
        flash("Sorry, you are not in admin mode and cannot access that page")
        return redirect(url_for("home"))
    

#stats file enter page
@app.route("/stats", methods = ["POST", "GET"])
def stats():
    #make sure user is logged in
    if 'logged in' in session:
        if session['logged in'] == False:
            flash("You are not logged in. Please log in before using Stats Summarizer")
            return redirect(url_for("login"))
        else:
            if request.method == "POST":
                #when form is filled out grab the file
                file = request.files['file']

                #make it a pandas dataframe
                dataframe = pd.read_csv(file)


                #save the dataframe to a JSON file
                with open("df.json", "r") as f:
                    data = json.load(f)
                data = dataframe.to_json(orient = 'index')
                with open('df.json', 'w') as f:
                    json.dump(data, f, indent=2)

                #get set up for the analyses
                session['in progress'] = True
                session['stats-form'] = 0
                return redirect(url_for("statsinprogress"))
            
            return render_template("stats.html")
    flash("You are not logged in. Please log in before using Stats Summarizer")
    return redirect(url_for("login"))

#selection page for stats picker
@app.route("/statsinprogress", methods = ["POST", "GET"])
def statsinprogress():
    #create lists that are used in quick summary
    means_list = []
    medians_list = []
    #make sure user is logged in
    if 'logged in' in session:
        if session['logged in'] == False:
            flash("You are not logged in. Please log in before using Stats Summarizer")
            return redirect(url_for("login"))
        else:
            if 'in progress' in session:
                #load in the dataframe
                if session['in progress'] == True:
                    with open("df.json", "r") as f:
                            data = json.load(f)
                    df = pd.read_json(data, orient="index")
                    columns_list = []
                    #make a list of all of the columns
                    for i in range(len(df.columns)):
                        columns_list.append(df.columns[i])
                    if columns_list[0] == "Unnamed: 0":
                        columns_list.remove("Unnamed: 0")
                    
                    #save what type of stats operation into a temporary variable
                    cool = session['stats-form']
                    
                    if request.method == "POST":
                        #variable to prevent error when selecting back to stats picker button
                        re_run = False
                        if 'return' in request.form:
                            
                            session['stats-form'] = 0
                            re_run = True
                                
                        #create return variable
                        text_to_return = ""
                        
                        #factor out non-number columns
                        for column in df:
                            if df[column].dtype != 'int64' and df[column].dtype != 'float64':
                                columns_list.remove(column)
                        
                        #quick summary
                        if session['stats-form'] == 0 and re_run == False:
                            #get form selection
                            output = request.form['firstselect']

                            if output == "Quick Summary":
                                text_to_return = f"This dataset has {len(columns_list)} numerical columns, all named: {columns_list}"
                                #get list of the means
                                for column in columns_list:
                                    means_list.append(df[column].mean())
                                #get list of the medians
                                for column in columns_list:
                                    medians_list.append(df[column].median())
                            #determine what was selected from the form
                            elif output == "Relationship":
                                session['stats-form'] = 2
                            elif output == "Graph":
                                session['stats-form'] = 3
                        
                        
                        #if relationship or graph was selected
                        elif session["stats-form"] == 2 or session['stats-form'] == 3:
                            #if form has been filled, get the results
                            if 'relselect' in request.form:
                                relselect = request.form.getlist('relselect')
                            else:
                                relselect = ["", ""]
                            
                            #correlation logic
                            if session['stats-form'] == 2:
                                #get the correlation and round it 
                                correlation = df[relselect[0]].corr(df[relselect[1]])
                                correlation = round(correlation, 3)

                                #create output based on what the correlation is 
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
                                #set up axes and go to graphing page
                                session['plotx'] = relselect[0]
                                session['ploty'] = relselect[1]
                                return redirect(url_for("graph"))
                            
                        #resave temporary variable
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

#graphing code
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
        #get dataframe from JSON
        with open("df.json", "r") as f:
                data = json.load(f)
        #get data frame and create plot
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

#logout logic
@app.route("/logout")
def logout():
    
    #warning, info error are categories, second term you pass in flash
    flash("You have been logged out successfully :)", "info")
        
    session.pop("username", None)
    session.pop("password", None)
    session.pop("logged in", None)
    session.pop("admin", None)
    session.pop("stats-form", None)
    session.pop("plotx", None)
    session.pop("ploty", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
