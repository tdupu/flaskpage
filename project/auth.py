from flask import Blueprint, render_template, redirect, url_for, request, flash

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from .models import db
from .models import User



auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login',methods=['POST'])
def login_post():
    email = request.form.get('email').lower()
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    
    #user = User.query.filter_by(email=email).first()
    user = db.session.query(User).filter(User.email==email).first()
    
    #check if the user actually exists
    #take the user-supplied password, hash it, compare to hashed password in the database
    if not user or not check_password_hash(user.password,password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) #if the user doesn't exist or gets wrong password
        
    #creates the session
    login_user(user,remember=remember)
    return redirect(url_for('prof.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup',methods=['POST'])
def signup_post():
    #code to validate and add user to database goes here
    email = request.form.get('email').lower()
    name = request.form.get('name')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email.lower()).first()
    
    if user:
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))
    
    #create a new user with form data
    new_user = User(email=email.lower(), name=name, password = generate_password_hash(password,method='sha256'))
    
    db.session.add(new_user)
    db.session.commit()
    
    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    return redirect(url_for('main.index'))
