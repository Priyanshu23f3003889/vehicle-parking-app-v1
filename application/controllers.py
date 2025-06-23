from flask import current_app as app
from flask import render_template, request, redirect, url_for, flash, session
from .models import *
from datetime import datetime

@app.route("/")
def home():
    return render_template('home.html')

