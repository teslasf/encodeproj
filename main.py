from flask import Flask, render_template
from flask import request
from flask import Flask, flash, url_for, redirect
from flask import Blueprint, url_for, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask
from sqlalchemy import Column, String
from sqlalchemy import *
#from sqlalchemy.orm import relation, sessionmaker
from sqlalchemy import Column, Integer, String
import sqlite3
import sqlalchemy as db
from flask_sqlalchemy import SQLAlchemy
import smtplib
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime, TIMESTAMP, text
from datetime import datetime

#con = sqlite3.connect('example.db')
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends4.db'
db = SQLAlchemy(app)


class students6(db.Model):
   #__tablename__ = 'students6'
   id = db.Column('id1',db.Integer, primary_key=True)
   name = db.Column(db.String(100))
   email = db.Column(db.String(100))
   password = db.Column(db.String(100))
   comments = db.Column(db.String(200))
   created_on = db.Column(db.DateTime, nullable=False)



   def __init__(self, name,email,password,comments):
      self.name = name
      self.email = email
      self.password = password
      self.comments = comments
      self.created_on = datetime.now()
 
@app.route('/article-details')
def articledetails():
    return render_template('article-details.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacypolicy():
    return render_template('privacy-policy.html')



@app.route('/halilbayraktar')
def hb():
    return render_template('halilbayraktar.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/user/<name>')
def hello_name(name):
   user=name
   if user:
      return render_template('user.html',user=user)

@app.route('/login')
def login():
   return render_template('log-in.html')

@app.route('/signup1')
def signup1():
   return render_template('sign-up.html')


@app.route('/login1', methods=['GET', 'POST'])
def login1():
   error = None
   if request.method == 'POST':
         print ("Creating data2")
         email = request.form.get("email")
         password = request.form.get("password")
         if not (password and email):
            return render_template("register.html", message="All fields are required.")
         user=students6.query.filter_by(email=email).first()
         if user:
            if user.password==password:
               print (user.name)
               return render_template('user.html',user=user.name)
            else:
               return 'Incorrect password'
         else:
            print('email does not exist')
   return render_template('index.html')



@app.route('/register', methods = ['GET', 'POST'])
def register():
   
   print ("Creating data")
   if request.method=='POST':
      print ("Creating data2")
      name = request.form.get("name")
      email = request.form.get("email")
      password = request.form.get("password")
      comments = request.form.get("comments")
      if not (name and password and email):
         return render_template("sign-up.html", msg="All fields are required.")
      

     # student = students6(request.form['name'],request.form['email'],request.form['password'])
      student = students6(name,email,password,comments)
      print (name)
      print(email)
      print ("Creating database table now...")
      db.session.add(student)
      db.session.commit()
      msg = 'You have successfully registered!'
      print ("Creating data3")
      return render_template('sign-up.html', msg = 'You have successfully registered!')


if __name__ == '__main__':
    with app.app_context():
      db.create_all()
    app.run(debug=False)
