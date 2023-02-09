# Statistics-Web-Application


Link To Website: http://liamg12.pythonanywhere.com/

The graphing function does not work yet for the hosted version.



This simple web application takes in any .csv file provided by the user, and give quick summary, relationship, and graphing summaries that are understandable by a non-statistics savvy person.


I decided to do this project because I really wanted to learn how to do statistics in python, and this allowed me to learn it and create a useful application that I could use to get ideas of datafiles quickly



**My Learning:**

Pandas

I learned how to do statistical analyses in python with the pandas and numpy libraries through FreeCodeCamp. It is similar to coding in R, a language that I already know, and I know understand how to create and manipulate dataframes to get information.

Flask

I learned how to create applications with the Python Web Framework called flask. I learned this in a tutorial by TechWithTim, where I could use python to run webpages.



**The Project:**

Part 1: Flask

The flask webpage, with help from a SQLAlchemy database, stores user information, and can register whether the login information is correct. Additionally, if it is a new user, there is a webpage to create a new account which is then saved in the SQLAlchemy database. Flask operates on the back end and handles form submissions and movement between pages.

Part 2: Jinja and Templates

As part of the flask tutorials, I learned about how to create HTML templates. Jinja is a script where you can write python code in html files, which allows me to display different things on webpages based on data sent to the page by flask. Additionally, I can use jinja to create a base html template that all the rest of the pages use.

Part 3: Pandas and MatPlotLib

Then, on the statistics pages, the application gets a csv file from a form, and saves it into a JSON file. This file allows any webpage to access the data if need be. Then, based on user selections in the form, pandas will perform statistical analyses of the numerical data, or MatPlotLib can make simple scatterplots of the data.



For me, being successful was creating a web application that did statistical analyses on data inputted by the user, and I accomplished my goal!!!!!


Sources:
Pandas Learning
- https://www.freecodecamp.org/learn/data-analysis-with-python/data-analysis-with-python-course/data-analysis-example-a 


Flask Tutorial
- https://www.youtube.com/watch?v=mqhxxeeTbu0&list=PLzMcBGfZo4-n4vJJybUVV3Un_NFS5EOgX&ab_channel=TechWithTim


Debugging:
- Stack Overflow
- A Little ChatGPT


JSON Conversions
- https://sparkbyexamples.com/pandas/pandas-convert-dataframe-to json/#:~:text=You%20can%20convert%20pandas%20DataFrame,stands%20for%20JavaScript%20Object%20Notation%20 
- https://sparkbyexamples.com/pandas/pandas-convert-json-to-dataframe/ 


MatPlotLib in Flask
- https://www.youtube.com/watch?v=Vf2K6zYQmu8&ab_channel=code_with_yanglin 
