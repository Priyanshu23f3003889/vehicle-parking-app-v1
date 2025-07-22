from flask import current_app as app
from flask import render_template, request, redirect, url_for, flash, session
from .models import *
import matplotlib.pyplot as plt
from datetime import datetime

plt.style.use("fivethirtyeight")





@app.route("/", methods=['GET','POST'])
def login():
    
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
    
    u=User.query.get(session['user'])
    
    if u.is_admin:
        return redirect(url_for('admin'))
    
    bookings=list(reversed(u.bookings))[:5]
    lots=Parking_lot.query.all()
    lt={l.id:l for l in lots}
    
    o={}
    for lot in lots:
        o[lot.id]=sum(1 for i in lot.spots if i.is_occupied)
    
    if request.method=='POST':
        
        q=request.form.get('search')
        
        if q:
            lts=[]
            
            if q.isdigit():
                lts=Parking_lot.query.filter_by(pincode=int(q)).all()
                                    
            else: 
                lts=Parking_lot.query.filter(Parking_lot.address.ilike(f"%{q.strip()}%")).all()

            return render_template('user.html', user=u, bookings=bookings, parking_lots=lts, o=o, lt=lt)
        
        return redirect(url_for('user'))
        
    return render_template('user.html', user=u, bookings=bookings, parking_lots=lots, o=o, lt=lt)






@app.route("/user_history", methods=["GET","POST"])
def user_history():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    if u.is_admin:
        return redirect(url_for('admin'))
    
    bookings=list(reversed(u.bookings))
    lt={l.id:l for l in Parking_lot.query.all()}
    
    return render_template("user_history.html", bookings=bookings, lt=lt, user=u)
    





@app.route('/release/<int:id>', methods=['GET', 'POST'])
def release(id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    if u.is_admin:
        return redirect(url_for('admin'))
    
    b={bk.id:bk for bk in u.bookings}
    booking=b[id] if id in b else None

    if booking and not booking.leaving:
        lot={p.id:p for p in Parking_lot.query.all()}

        curr=datetime.now()
        d=(curr-booking.parking).total_seconds()/3600
        hrs=round(d) if d > 1 else 1
        cost=booking.price * hrs

        if request.method=="POST":
            spot=Parking_spot.query.get(booking.spot_id)

            booking.leaving=curr
            booking.cost=cost
            spot.is_occupied=False

            db.session.commit()

            flash("Parked Out Successfully !!")
            return redirect(url_for('user'))

        return render_template('release.html', lot=lot,booking=booking, total=cost, leave=curr,hr=hrs)
    
    else:
        flash("\nAlready Parked Out !! ")
        return redirect(url_for('user'))





@app.route("/book/<int:id>", methods=["GET","POST"])
def book(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    if u.is_admin:
        return redirect(url_for('admin'))
    
    lot=Parking_lot.query.get(id)
    time=datetime.now()

    spot=None

    for s in lot.spots:
        if not s.is_occupied:
            spot=s
            break

    if not spot:
        flash("Parking Lot is full")
        return redirect(url_for('user'))
    
    if request.method=='POST':
        vehicle=request.form.get('vehicle')
        if not vehicle or  len(vehicle) > 12  or len(vehicle) < 6:
            flash("Invalid Vehicle No. !!")
            return redirect(url_for('book', id=id))
        
        if not spot.is_occupied:

            booking=Booking(user_id=session['user'], lot_id=id, spot_id=spot.id, parking=time, vehicle_no=vehicle, price=lot.price)
            db.session.add(booking)
            db.session.commit()

            spot.is_occupied=True
            # spot.booking_id=booking.id
            db.session.commit()

            flash("Booking Successfull!!")
            return redirect(url_for('user'))
        
        else:
            return redirect(url_for('book', id=id))

    return render_template("book.html", lot=lot, time=time, spot=spot)





@app.route('/admin', methods=['GET', 'POST'])
def admin():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    if u.is_admin==True:
        
        lots=Parking_lot.query.all()
        
        o={}
        for lot in lots:
            o[lot.id]=sum(1 for i in lot.spots if i.is_occupied)
            
        if request.method=='POST':
            
            q=request.form.get('search')
            
            if q:
                lts=[]
                
                if q.isdigit():
                    lts=Parking_lot.query.filter_by(pincode=int(q)).all()
                                        
                else: 
                    lts=Parking_lot.query.filter(Parking_lot.address.ilike(f"%{q.strip()}%")).all()  

                return render_template('admin.html', parking_lots=lts, o=o)
            
            return redirect(url_for('admin'))
                
        return render_template('admin.html', parking_lots=lots, o=o)
    
    return redirect(url_for('user'))
   




@app.route("/users", methods=['GET','POST'])
def users():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    if u.is_admin==True:
        
        if request.method=='POST':
            
                q=request.form.get('search')
                
                if q:
                    usrs=[]
                    
                    if q.isdigit():
                        usrs.append(User.query.get(int(q)))
                    
                    elif '@' in q and '.' in q:
                        usrs=User.query.filter(User.email.ilike(f"%{q.strip()}%")).all()  
                                        
                    else: 
                        usrs=User.query.filter(User.username.ilike(f"%{q.strip()}%")).all()  

                    return render_template('users.html', users=usrs)
                
                return redirect(url_for('users'))
            
        all=User.query.all()[1:]
        
        return render_template('users.html', users=all)
    
    return redirect(url_for('user'))






@app.route("/summary")
def summary():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    colors = ['salmon','skyblue','limegreen', 'gold', 'orchid']
    fig, ax = plt.subplots()
    pl=Parking_lot.query.all()
    
    if u.is_admin==True:

        data={",".join(p.address.split(',')[:2]):sum(b.cost for b in p.bookings if b.cost)+0 for p in pl}
        group_data = list(data.values())
        group_names = list(data.keys())
        
        ax.barh(group_names, group_data, color=colors)
        ax.set(xlabel='\nTotal Revenue (₹)', ylabel='Parking Lots\n')
        
        plt.savefig('static/plot.svg' ,dpi=600, bbox_inches='tight', transparent=True)
            
        return render_template('admin_summary.html')
    
    else:
        bks=u.bookings
        plts={p.id:p for p in pl}
        
        data={}
        for b in bks:
            i=b.lot_id
            if i:
                data[",".join(plts[i].address.split(',')[:2])]=data.get(",".join(plts[i].address.split(',')[:2]),0)+1

        group_data = list(data.values())
        group_names = list(data.keys())
        
        ax.barh(group_names, group_data, color=colors)
        ax.set(xlabel='\nFrequency', ylabel='Parking Lots\n')

        plt.savefig('static/uplot.svg' ,dpi=600, bbox_inches='tight', transparent=True)
        
        return render_template('user_summary.html', user=u)





@app.route("/addlot", methods=['GET','POST'])
def addlot():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    if u.is_admin==True:
        
        if request.method=='POST':
            prime = request.form.get("location").strip()
            add = request.form.get("address").strip()
            pin = abs(int(request.form.get("pin")))
            prc = abs(int(request.form.get("price")))
            spots = abs(int(request.form.get("max")))
            
            if not prime or not add or not pin or not prc or not spots:
                flash('\\nPlease fill all the fields !!')
                return redirect(url_for('addlot'))
            
            if len(str(pin))!=6:
                flash('\\n INVALID Pincode !!')
                return redirect(url_for('addlot'))
            
            
            
            lot = Parking_lot(prime_location=prime, address=add, pincode=pin, price=prc, max_spots=spots)
            db.session.add(lot)
            db.session.commit()
            
            for _ in range(spots):
                spot=Parking_spot(lot_id=lot.id)
                db.session.add(spot)
                
            db.session.commit()
                
            flash("\\nParking Lot and Spots Added Successfully !! ")
            return redirect(url_for('addlot'))
                
        return render_template('addlot.html')
    
    else:
        return redirect(url_for('user'))
        




@app.route("/editlot/<int:id>", methods=['GET','POST'])
def editlot(id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    if u.is_admin==True:
        lot=Parking_lot.query.filter(Parking_lot.id==id).first()

        if lot:
            spot=lot.spots
            oqp=[s for s in spot if s.is_occupied]
            
            
            if request.method=='POST':
                
                act = request.form.get('action')
                
                if act=='delete':
                    
                    if not oqp:
                        
                        for s in spot:
                            db.session.delete(s)
                            
                        db.session.delete(lot)
                        
                        db.session.commit()
                        
                        flash('\\nParking Lot DELETED Successfully !!')
                        return redirect(url_for('admin',id=id))
                    
                    else:
                        flash("\\nCan NOT Delete Parking lot with Occupied Spots !!")
                        return redirect(url_for('editlot',id=id))
                
                elif act == 'update':
                    newprice=request.form.get('newprice')
                    maxspots=request.form.get('newmaxspots')
                    addr=request.form.get('addr').strip()
                    prime=request.form.get('prime').strip()
                    pin=request.form.get('pin')
                    
                    f1=f2=f3=f4=""

                    if newprice:
                        lot.price=abs(int(newprice))
                        
                    if maxspots:
                        maxspots=abs(int(maxspots))
                        
                        if maxspots< len(oqp):
                            f1="\\nMax Parking Spots Can NOT be LESS than OCCUPIED spots !!"
                        
                        elif maxspots<len(spot):
                            
                            spt=[s for s in spot if not s.is_occupied][:len(spot)-maxspots]
                            
                            for s in spt:
                                db.session.delete(s)
                            lot.max_spots=int(maxspots)
                                
                        elif maxspots>len(spot):
                            
                            for i in range(maxspots-len(spot)) :
                                s=Parking_spot(lot_id=lot.id, is_occupied=False)    
                                db.session.add(s)   
                            lot.max_spots=int(maxspots)

                    db.session.commit()

                    if addr:
                        if lot.address != addr:
                            if not oqp:
                                lot.address=addr
                                db.session.commit()
                            else:
                                f2="\\nCan NOT change Address with occupied spots !!"
                    
                    if prime:
                        if lot.prime_location != prime:
                            if not oqp:
                                lot.prime_location=prime
                                db.session.commit()
                            else:
                                f3="\\nCan NOT change Prime_location with occupied spots !!"
                    
                    if pin:
                        if lot.pincode != int(pin):
                            if not oqp and  len(pin)==6:
                                lot.pincode=int(pin)
                                db.session.commit()
                            else:
                                f4="\\nCan NOT change Pin!!"
                            
                        
                    
                    flash(f1+f2+f3+f4+'\\nParking Lot UPDATED !!')
                    return redirect(url_for('editlot', id=id)) 
        
                elif act.isdigit():
                    sp=Parking_spot.query.get(int(act))
                    
                    if not sp.is_occupied:
                        db.session.delete(sp)
                        lot.max_spots-=1
                        
                        db.session.commit()
                        
                        flash('\\nParking spot DELETED Successfully !!')
                        return redirect(url_for('editlot', id=id)) 
                    
                    else:
                        flash('\\nCan NOT DELETE Occupied Spot !!')
                        return redirect(url_for('editlot', id=id))
                    
                    
            b=lot.spots
            o=len(oqp)
            bkins={b.id:b for b in lot.bookings}
            
            return render_template('editlot.html', lot=lot, spots=b, bookings=bkins, o=o)
        
        else:
            flash("\\nParking Lot Does NOT exists !!")
            return redirect(url_for('admin'))
        
    return redirect(url_for('user'))





@app.route("/users/<int:id>", methods=['GET','POST'])
def viewuser(id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    if u.is_admin==True:
        usr=User.query.get(id)
        
        if usr:
            bk=reversed(usr.bookings)
            lt={lot.id:lot for lot in Parking_lot.query.all()}
            
            return render_template('viewuser.html',user=usr,lots=lt, bookings=bk)
        
        else:
            flash("\\nUser Does NOT exists !!")
            return redirect(url_for('admin'))
        
    return redirect(url_for('user'))


    
    
    
@app.route('/bookings', methods=["GET","POST"])
def bookings():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    if u.is_admin==True:
        b=reversed(Booking.query.order_by(Booking.parking).all())
        return render_template('bookings.html', bookings=b)
    
    return redirect(url_for('user'))





@app.route('/booking/<int:id>', methods=["GET","POST"])
def viewbooking(id):
    
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.get(session['user'])
    
    if u.is_admin==True:
        b=Booking.query.get(id)
        if b:
            return render_template('viewbooking.html', booking=b)
        else:
            flash("Invalid booking ID")
            return redirect(url_for("admin"))
    
    return redirect(url_for('user'))
    
    



@app.route('/logout')
def logout():
    
    if 'user' in session:
        session.pop('user')
        
    return redirect(url_for('login')) 