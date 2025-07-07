from flask import current_app as app
from flask import render_template, request, redirect, url_for, flash, session
from .models import *
import matplotlib.pyplot as plt
import mpld3
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
        
        lots=Parking_lot.query.all()
        o={}
        for lot in lots:
            o[lot.id]=sum(1 for i in lot.spots if i.is_occupied)
            
        if request.method=='POST':
            q=request.form.get('search')
            lts=[]
            if q.isdigit():
                lts=Parking_lot.query.filter_by(pincode=int(q)).all()
                                    
            else: 
                lts=Parking_lot.query.filter(Parking_lot.prime_location.ilike(f"%{q}%")).all()  

            return render_template('admin.html', parking_lots=lts, o=o)
                
                
                
        return render_template('admin.html', parking_lots=lots, o=o)
    
    return redirect(url_for('user'))
   
        
        
@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))



@app.route("/users", methods=['GET','POST'])
def users():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.filter(User.id==session['user']).first()
    
    if u.is_admin==True:
        if request.method=='POST':
                q=request.form.get('search')
                usrs=[]
                if q.isdigit():
                    usrs.append(User.query.get(int(q)))
                
                elif '@' in q and '.' in q:
                    usrs=User.query.filter(User.email.ilike(f"%{q}%")).all()  
                                      
                else: 
                    usrs=User.query.filter(User.username.ilike(f"%{q}%")).all()  

                return render_template('users.html', users=usrs)
        all=User.query.all()[1:]
        return render_template('users.html', users=all)
    
    return redirect(url_for('user'))



@app.route("/summary")
def summary():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.filter(User.id==session['user']).first()
    
    if u.is_admin==True:
        plt.style.use("fivethirtyeight")
        colors = ['salmon','skyblue','limegreen', 'gold', 'orchid']
        pl=Parking_lot.query.all()
        data={p.prime_location:sum(b.cost for b in p.bookings if b.cost)+0 for p in pl}
        group_data = list(data.values())
        group_names = list(data.keys())
        fig, ax = plt.subplots()
        ax.barh(group_names, group_data, color=colors)
        ax.set(xlabel='Total Revenue (₹)', ylabel='Parking Lots')
        plt.savefig('static/plot.svg' ,dpi=600, bbox_inches='tight', transparent=True)
            
        return render_template('admin_summary.html')
    else:
        return render_template('user_summary.html')



@app.route("/addlot", methods=['GET','POST'])
def addlot():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.filter(User.id==session['user']).first()
    
    if u.is_admin==True:
        
        if request.method=='POST':
            prime = request.form.get("location").strip()
            add = request.form.get("address").strip()
            pin = int(request.form.get("pin"))
            prc = int(request.form.get("price"))
            spots = int(request.form.get("max"))
            
            if not prime or not add or not pin or not prc or not spots:
                flash('\\nPlease fill all the fields !!')
                return redirect(url_for('addlot'))
            if len(str(pin))!=6:
                flash('\\n INVALID Pincode !!')
                return redirect(url_for('addlot'))
            if spots>10000:
                flash('\\n Maximum Spots value is too big !!')
                return redirect(url_for('addlot'))
                
                
            l = Parking_lot.query.filter(Parking_lot.prime_location==prime).first()
            if l :
                flash('\\nPrime Location Already Exists !!')
                return redirect(url_for('addlot'))
            
            else:
                lot = Parking_lot(prime_location=prime, address=add, pincode=pin, price=prc, max_spots=spots)
                db.session.add(lot)
                db.session.commit()
                
                lt=Parking_lot.query.filter(Parking_lot.id==lot.id).first()
                for s in range(spots):
                    spot=Parking_spot(lot_id=lt.id)
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
    
    u=User.query.filter(User.id==session['user']).first()
    
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
                            db.session.commit()
        
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
                    
                    if not newprice and not maxspots:
                        flash("\\nPlease Provide values to Update !!")
                        return redirect(url_for('editlot', id=id))
                    if newprice:
                        lot.price=int(newprice)
                        db.session.commit()
                    if maxspots:
                        maxspots=int(maxspots)
                        if maxspots>10000:
                            flash('\\n value for Maximum Spots is too Big !!')
                            return redirect(url_for('editlot', id=id))
                        if maxspots< sum((1 for _ in spot if _.is_occupied)):
                            flash('\\n Updated Max_Parking_Spot is LESS than OCCUPIED spots !!')
                            return redirect(url_for('editlot', id=id))
                        if maxspots<len(spot):
                            spt=[s for s in spot if not s.is_occupied][:len(spot)-maxspots]
                            for s in spt:
                                db.session.delete(s)
                                db.session.commit()
                        if maxspots>len(spot):
                            for i in range(maxspots-len(spot)) :
                                s=Parking_spot(lot_id=lot.id, is_occupied=False)    
                                db.session.add(s)
                                db.session.commit()
                        lot.max_spots=int(maxspots)
                        db.session.commit()
                    
                    flash('\\nParking Lot UPDATED Successfully !!')
                    return redirect(url_for('editlot', id=id)) 
                 
            b={i.id:Booking.query.get(i.booking_id) for i in oqp}
            return render_template('editlot.html', lot=lot, spots=b)
        
        else:
            flash("\\nParking Lot Does NOT exists !!")
            return redirect(url_for('admin'))
        
    return redirect(url_for('user'))



@app.route("/users/<int:id>", methods=['GET','POST'])
def viewuser(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    u=User.query.filter(User.id==session['user']).first()
    
    if u.is_admin==True:
        usr=User.query.get(id)
        if usr:
            bk=reversed(usr.bookings)
            lt={b.lot_id:Parking_lot.query.get(b.lot_id) for b in usr.bookings}
            return render_template('viewuser.html',user=usr,lots=lt, bookings=bk)
        else:
            flash("\\nUser Does NOT exists !!")
            return redirect(url_for('admin'))
        
    return redirect(url_for('user'))
    

    

    