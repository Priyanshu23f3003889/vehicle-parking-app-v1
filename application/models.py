from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
class Parking_lot(db.Model):
    id = db.Column(db.Integer, primary_key=True ,autoincrement=True)
    max_spots = db.Column(db.Integer(), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    prime_location = db.Column(db.String(), unique=True, nullable=False)
    pincode = db.Column(db.Integer(), nullable=False)
    address = db.Column(db.String(), nullable=False)

class Parking_spot(db.Model):
    id = db.Column(db.Integer, primary_key=True ,autoincrement=True)
    lot_id = db.Column(db.Integer(), db.ForeignKey('parking_lot.id'), nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)

class Booking(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(), db.ForeignKey('user.id'), nullable=False)
    spot_id = db.Column(db.Integer(), db.ForeignKey('parking_spot.id'), nullable=False)
    parking = db.Column(db.DateTime(), nullable=False)
    leaving = db.Column(db.DateTime(), nullable=True)
    vehicle_no = db.Column(db.String(), nullable=False)
    cost = db.Column(db.Integer(), nullable= True)