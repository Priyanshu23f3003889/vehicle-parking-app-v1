from flask import current_app as app
from flask import render_template, request, redirect, url_for, flash, session
from .models import *
from datetime import datetime


@app.route("/", methods=['GET','POST'])
def login():
    alert=''
    if 'user' in session:
        return redirect(url_for('user'))
    
    if request.method=='POST':
        mail = request.form.get("email")
        passw = request.form.get("password")
        
        user = User.query.filter(User.email==mail, User.password==passw).first()
        
        if user:
            session["user"] =  user.id
            return redirect(url_for("user"))
        else:
            flash("\\nInvalid Username or Password !!")
            return redirect(url_for("login"))

    return render_template('login.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect(url_for('user'))
    
    if request.method=='POST':
        name = request.form.get("username")
        mail = request.form.get("email")
        passw = request.form.get("password")
        
        if (not mail) or (not passw) or (not name):
            flash('Please fill all the fields')
            return redirect(url_for('register'))
        
        u=User.query.filter(User.email==mail).first()
        
        if not u:
            user = User(email=mail, password=passw, username=name)
            db.session.add(user)
            db.session.commit()
            flash('\\nRegistration Successfull !!')
            return redirect(url_for('login'))
            
        else:
            flash('\\nEmail already exists !!')
            return redirect(url_for('register'))
        
    return render_template('register.html')


@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.filter(User.id==session['user']).first()
    
    if u.is_admin==True:
        return redirect(url_for('admin'))
    
    return render_template('user.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.filter(User.id==session['user']).first()
    
    if u.is_admin==True:
        return render_template('admin.html')
    
    return redirect(url_for('user'))
        
        
@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))


    