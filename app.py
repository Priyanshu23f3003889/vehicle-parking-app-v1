from flask import Flask
from application.models import *


def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///parking.db"
    app.config['SECRET_KEY'] = 'The_secret_key'
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    return app
app=create_app()

a=User.query.filter(User.email == 'admin@email.com').first()
if not a:
    u = User(username='admin', email='admin@email.com', password='admin', is_admin=True)
    db.session.add(u)
    db.session.commit()

import application.controllers
app.run(debug=True, host='0.0.0.0', port=80)
