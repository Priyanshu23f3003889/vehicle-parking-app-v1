from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(), unique=True, nullable=False)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='user', lazy=True, order_by='Booking.parking')
    
class Parking_lot(db.Model):
    id = db.Column(db.Integer, primary_key=True ,autoincrement=True)
    max_spots = db.Column(db.Integer(), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    prime_location = db.Column(db.String(), unique=True, nullable=False)
    pincode = db.Column(db.Integer(), nullable=False)
    address = db.Column(db.String(), nullable=False)
    spots = db.relationship('Parking_spot', backref='parking_lot', lazy=True)
    bookings = db.relationship('Booking', backref='parking_lot', lazy=True, order_by='Booking.parking')

class Parking_spot(db.Model):
    id = db.Column(db.Integer, primary_key=True ,autoincrement=True)
    lot_id = db.Column(db.Integer(), db.ForeignKey('parking_lot.id'), nullable=False)
    booking_id=db.Column(db.Integer(), nullable=True)
    is_occupied = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='parking_spot', lazy=True, order_by='Booking.parking')

class Booking(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    lot_id = db.Column(db.Integer(), db.ForeignKey('parking_lot.id'), nullable=False)
    spot_id = db.Column(db.Integer(), db.ForeignKey('parking_spot.id'), nullable=False)
    parking = db.Column(db.DateTime(), nullable=False)
    leaving = db.Column(db.DateTime(), nullable=True)
    vehicle_no = db.Column(db.String(), nullable=False)
    cost = db.Column(db.Integer(), nullable= True)