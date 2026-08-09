from flask import Flask, render_template,request,redirect,url_for
from models import db,UserCredentials,UserDetails,TrekStaff,TrekDetails,BookingDetails
from datetime import datetime

app=Flask(__name__)
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
            return render_template("admin_dashboard.html")
        elif user and int(role)==1:
            return render_template("user_dashboard.html")
        elif user and int(role)==2:
            staff = TrekStaff.query.filter_by(user_id=user.user_id).first()

            if staff:
              return redirect(url_for("staff_dash", staff_id=staff.staff_id))

            return "Staff details not found", 404
            return render_template("staff_dashboard.html")
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
    book_data=get_all_booking()
    return render_template("admin_dashboard.html",book_data=book_data)

#user dashboard
@app.route("/user_dashboard")
def user_dash():

    return render_template("user_dashboard.html")

#staff dashboard
@app.route("/staff_dashboard")
def staff_dash(staff_id):
    # staff=TrekStaff.query.get(staff_id)
    # if staff is None:
    #     return "Staff Not Found",404
    return render_template("staff_dashboard.html")

#Admin manages Staff
@app.route("/manage_staff")
def admin_mng_staff():
    return render_template("admin_manage_staff.html")

#Admin manage treks
@app.route("/manage_trek")
def admin_mng_trek():
    return render_template("admin_manage_treks.html")

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
        assign_st=int(request.form.get("staff_id"))
        st=int(request.form.get("stat"))
        desc=request.form.get("description")
        booking=TrekDetails(trek_name=tname,location=location,difficulty=difficulty,duration_days=duration,available_slots=av_slot,
                            start_date=st_date,end_date=end_date,staff_id=assign_st,status=st)
        db.session.add(booking)
        db.session.commit()
        return redirect(url_for("admin_mng_trek"))
    
    return render_template("admin_add_edit.html",staff_list=staff_list)

#staff manages trek 
@app.route("/staff_trek")
def staff_modify_trek():
    return render_template("staff-manage-trek.html")

#User booking details
@app.route("/booking_info")
def booking_details():
    return render_template("user_bookings.html")

#User trekking details
@app.route("/user_trek")
def user_trekking():
    return render_template("user_trek_details.html")

#User trekking history
@app.route("/trekking_history")
def trek_history():
    return render_template("user_trekking_history.html")

#Staff can view participants
@app.route("/participants")
def staff_participants():
    return render_template("staff_view_participants.html")

@app.route("/admin_bookings")
def admin_mng_bookings():
    return render_template("admin_bookings.html")

@app.route("/admin_trekkers")
def admin_users():
    return render_template('admin_view_users.html')

@app.route("/staff_pr")
def staff_profile(staff_id):
    staff=db.session.query(TrekStaff).filter(TrekStaff.staff_id==staff_id).first()
    if staff is None:
        return "Staff not found", 404

    return render_template("staff_profile.html", staff=staff)
    

@app.route("/trekker_profile")
def user_profile():
    return render_template("user_profile.html")


#Additional python functions
def get_all_booking():
    book_data=db.session.query(BookingDetails).filter().all()
    return book_data

# def get_all_staff_details():
#     staff=db.session.query(TrekStaff).filter().all()
#     return staff

if __name__=="__main__":
    app.run(debug=True)