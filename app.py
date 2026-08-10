from flask import Flask, render_template,request,redirect,url_for,session
from models import db,UserCredentials,UserDetails,TrekStaff,TrekDetails,BookingDetails
from datetime import datetime,date
from sqlalchemy import func

app=Flask(__name__)
app.secret_key='hello'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///trekking_database.sqlite3'
db.init_app(app)

#creating a super user (Admin)
def create_admin():
    with app.app_context():
        db.create_all()
        print("Database created")
        admin=UserCredentials.query.filter_by(email_id="admin@iitm.ac.in").first()
        if admin is None:
            admin=UserCredentials(user_id="1",email_id="admin@iitm.ac.in",password="12345",role="0") #role:0 (admin)
            db.session.add(admin)
            db.session.commit()

create_admin()


#login page
@app.route("/login",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        uname=request.form.get("email")
        pwd=request.form.get("pwd")
        role=request.form.get("utype")
        user=db.session.query(UserCredentials).filter(UserCredentials.email_id==uname).first()
        if user and int(role)==0:
            return redirect(url_for("admin_dash"))
        elif user and int(role)==1:
            session["user_email_id"]=user.email_id
            session['user_user_id']=user.user_id
            return redirect(url_for("user_dash"))
        elif user and int(role)==2:
            session["user_email_id"]=user.email_id
            staff = TrekStaff.query.filter_by(user_id=user.user_id).first()

            if staff:
              session["staff_id"]=staff.staff_id
              return redirect(url_for("staff_dash", staff_id=staff.staff_id))

            return "Staff details not found", 404
            # return render_template("staff_dashboard.html")
        else:
            return redirect(url_for('register'))
    else:
        return render_template("login_page.html")

#registration page
@app.route("/registration",methods=["GET","POST"])
def register():
    if request.method=="POST":
        uname=request.form.get("email")
        pwd=request.form.get("pwd")
        role=request.form.get("utype")
        user=db.session.query(UserCredentials).filter(UserCredentials.email_id==uname).first()
        if user:
            return render_template("register_page.html",err_msg="Sorry,email is already registered")
        else:
            #need to store in user_credentials
            uc=UserCredentials(email_id=uname,password=pwd,role=int(role))
            db.session.add(uc)
            db.session.commit() #save in db
            address=request.form.get("address")
            phno=request.form.get("phno")
            fname=request.form.get("fname")
            if int(role)==1:
                trekker=UserDetails(user_id=uc.user_id,email_id=uc.email_id,password=uc.password,full_name=fname,address=address,phone_num=phno)
                db.session.add(trekker) #if role is user(trekker)
            else:
                staff=TrekStaff(user_id=uc.user_id,password=uc.password,email_id=uc.email_id,full_name=fname,address=address,phone_num=phno)
                db.session.add(staff) #if role is staff
            db.session.commit() #save
            return redirect(url_for('signin'))

    else:
        #request type is get
        return render_template("register_page.html")
        
#admin dashboard
@app.route("/admin_dashboard")
def admin_dash():
    user_count=db.session.scalar(db.select(func.count(UserDetails.trekker_id)))
    staff_count=db.session.scalar(db.select(func.count(TrekStaff.staff_id)))
    booking_count=db.session.scalar(db.select(func.count(BookingDetails.booking_id)))
    trek_count=db.session.scalar(db.select(func.count(TrekDetails.trek_id)))
    stats={
        "total_users":user_count,"total_staff":staff_count,"total_bookings":booking_count,"total_treks":trek_count
    }
    return render_template("admin_dashboard.html",s=stats)

#user dashboard
@app.route("/user_dashboard")
def user_dash():
    book_data=db.session.query(TrekDetails).all()

    return render_template("user_dashboard.html",treks=book_data)

#staff dashboard
@app.route("/staff_dashboard")
def staff_dash():
    trek=TrekDetails.query.all()
    current_staff_id = session.get('staff_id')
    assigned_count=db.session.query(TrekDetails).filter_by(staff_id=current_staff_id).count()
    total_participants = db.session.query(func.count(BookingDetails.booking_id))\
        .join(TrekDetails, BookingDetails.trek_id == TrekDetails.trek_id)\
        .filter(TrekDetails.staff_id == current_staff_id)\
        .scalar() or 0
    open_treks_count = db.session.query(TrekDetails)\
        .filter(TrekDetails.staff_id == current_staff_id, TrekDetails.status == 1)\
        .count()

    return render_template("staff_dashboard.html",treks=trek,task_count=assigned_count,total_participants=total_participants,open_treks_count=open_treks_count)

#Admin manages Staff
@app.route("/manage_staff")
def admin_mng_staff():
    staff_members=TrekStaff.query.all()
    pending_req = db.session.scalar(db.select(func.count(TrekStaff.staff_id)).where(TrekStaff.approval_status == 0))
    approved_req = db.session.scalar(db.select(func.count(TrekStaff.staff_id)).where(TrekStaff.approval_status == 1))
    rejected_req = db.session.scalar(db.select(func.count(TrekStaff.staff_id)).where(TrekStaff.approval_status == 2))
    

    stats = {
        
        # Add the counts here to make them available in Jinja
        "pending_requests": pending_req,
        "approved_requests": approved_req,
        "rejected_requests": rejected_req
    }
    return render_template("admin_manage_staff.html",staff_list=staff_members,stats=stats)


#admin can approve or reject
@app.route('/trekstaff/approve', methods=['POST'])
def approve_staff():
    
    staff_id = request.form.get('staff_id')
    staff_member = TrekStaff.query.get(staff_id)
    
    if staff_member:
       
        staff_member.approval_status = '1' 
        db.session.commit() # Save changes to the DB file
        
    return redirect('/manage_staff') 

@app.route('/trekstaff/reject', methods=['POST'])
def reject_staff():
    staff_id = request.form.get('staff_id')
    staff_member = TrekStaff.query.get(staff_id)
    
    if staff_member:
        staff_member.approval_status = ''
        db.session.commit() # Save changes to the DB file
        
    return redirect('/manage_staff')


#Admin manage treks
@app.route("/manage_trek")
def admin_mng_trek():
    trek_info=TrekDetails.query.all()
    return render_template("admin_manage_treks.html",trek_list=trek_info)

#Admin functions(add/edit)
@app.route("/admin_func",methods=["GET","POST"])
def admin_modify():
    staff_list=TrekStaff.query.all()
    if request.method=="POST":
        tname=request.form.get("trek_name")
        location=request.form.get("location")
        difficulty=int(request.form.get("difficulty"))
        duration=int(request.form.get("duration"))
        av_slot=int(request.form.get("slot"))
        st_date=datetime.strptime(request.form.get("start_date"),"%Y-%m-%d").date()
        end_date=datetime.strptime(request.form.get("end_date"),"%Y-%m-%d").date()
        assign_st=int(request.form.get("assign"))
        st=(request.form.get("stat"))
        desc=request.form.get("description")
        booking=TrekDetails(trek_name=tname,location=location,difficulty=difficulty,duration_days=duration,available_slots=av_slot,
                            start_date=st_date,end_date=end_date,staff_id=assign_st,status=st,description=desc)
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for("admin_mng_trek"))
    
    return render_template("admin_add_edit.html",staff_list=staff_list)

#staff manages trek 
@app.route("/staff_trek")
def staff_modify_trek():
    treks=TrekDetails.query.all()
    return render_template("staff-manage-trek.html",treks=treks)

#User trekking history
@app.route("/trekking_history")
def trek_history():
    treks=TrekDetails.query.all()
    return render_template("user_trekking_history.html",treks=treks)

#Staff can view participants
@app.route("/participants")
def staff_participants():
    participants_list = db.session.query(
        BookingDetails.booking_id,
        BookingDetails.booking_date,
        UserDetails.full_name,
        UserDetails.email_id
    ).join(UserDetails, BookingDetails.user_id == UserDetails.user_id).all()
    
    
    return render_template("staff_view_participants.html",participants=participants_list)

#Admin view bookings
@app.route("/admin_bookings")
def admin_mng_bookings():
    bookings=BookingDetails.query.all()
    return render_template("admin_bookings.html",bookings=bookings)

@app.route("/admin_trekkers")
def admin_users():
    user_data=db.session.query(UserDetails,BookingDetails,TrekDetails).join(BookingDetails,UserDetails.user_id==BookingDetails.user_id).join(
        TrekDetails,BookingDetails.trek_id==TrekDetails.trek_id
    ).all()
    return render_template('admin_view_users.html',user_data=user_data)

#Staff Profile
@app.route("/staff_pr")
def staff_profile():
    email=session.get("user_email_id")
    staff=TrekStaff.query.filter_by(email_id=email).first()
    return render_template("staff_profile.html",staff=staff)
    
#Trekker profile
@app.route("/trekker_profile")
def user_profile():
    email=session.get("user_email_id")
    user=UserDetails.query.filter_by(email_id=email).first()
    return render_template("user_profile.html",user=user)


#Additional python functions
def get_all_booking():
    book_data=db.session.query(BookingDetails).filter().all()
    return book_data


#search trek,staff,users
@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    treks = []
    staff = []
    users = []

    if query:
        search = f"%{query}%"

        # Search Treks
        treks = TrekDetails.query.filter(
            TrekDetails.trek_name.ilike(search)
        ).all()

        # Search Staff
        staff = TrekStaff.query.filter(
            (TrekStaff.full_name.ilike(search)) |
            (TrekStaff.email_id.ilike(search))
        ).all()

        # Search Users
        users = UserDetails.query.filter(
            (UserDetails.full_name.ilike(search)) |
            (UserDetails.email_id.ilike(search))
        ).all()

    return render_template(
        "search.html",
        query=query,
        treks=treks,
        staff=staff,
        users=users
    )

#search treks for users
@app.route("/search_trek")
def search_trek():
    query = request.args.get("q", "").strip()

    treks = []
    if query:
        search = f"%{query}%"

        # Search Treks
        treks = TrekDetails.query.filter(
            TrekDetails.trek_name.ilike(search)
        ).all()

    
    return render_template(
        "search_treks.html",
        query=query,
        treks=treks,
       
    )
@app.route('/book_trek/<int:trek_id>', methods=['POST'])
def book_trek(trek_id):

    # Get logged-in user's ID
    user_user_id = session.get('user_user_id')

    if not user_user_id:
        return redirect(url_for('signin'))

    # Find the selected trek
    trek = TrekDetails.query.get(trek_id)

    if not trek:
        return "Trek not found"

    # Check available slots
    if trek.available_slots <= 0:
        return "No slots available"

    # Create booking
    booking = BookingDetails(
        user_id=user_user_id,
        trek_id=trek_id,
        booking_date=date.today()
    )

    # Reduce available slots
    trek.available_slots -= 1

    # Save to database
    db.session.add(booking)
    db.session.commit()

    return redirect(url_for('user_dash'))



if __name__=="__main__":
    app.run(debug=True)