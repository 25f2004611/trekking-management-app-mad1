from flask import Flask, render_template,request,redirect,url_for
from models import db,UserCredentials,UserDetails,TrekStaff,TrekDetails,BookingDetails

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///trekking_database.sqlite3'
db.init_app(app)

#creating a super user (Admin)
# def create_admin():
#     with app.app_context():
#         db.create_all()
#         print("Database created")
#         admin=AdminProfile.query.filter_by(username="admin").first()
#         if admin is None:
#             admin=AdminProfile(username="admin",password="12345")
#             db.session.add(admin)
#             db.session.commit()

# create_admin()


#login page
@app.route("/login")
def signin():
    if request.method=="POST":
        uname=request.form.get("email")
        pwd=request.form.get("pwd")
        user=db.session.query(UserCredentials).filter(UserCredentials.email_id==uname,UserCredentials.password==pwd)
        if user and user.role==0:
            return render_template("admin_dashboard.html")
        elif user and user.role==1:
            return render_template("user_dashboard.html")
        elif user and user.role==2:
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

    else:
        #request type is get
        return render_template("register_page.html")
        
#admin dashboard
@app.route("/admin_dashboard")
def admin_dash():
    return render_template("admin_dashboard.html")

#user dashboard
@app.route("/user_dashboard")
def user_dash():
    return render_template("user_dashboard.html")

#staff dashboard
@app.route("/staff_dashboard")
def staff_dash():
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
@app.route("/admin_func")
def admin_modify():
    return render_template("admin_add_edit.html")

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
def trek_history():
    return render_template("user_trekking_history.html")

if __name__=="__main__":
    with app.app_context():
        db.create_all()
    print("Database created")
    app.run(debug=True)