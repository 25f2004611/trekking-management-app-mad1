from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

#Database models
# class AdminProfile(db.Model):
#     __tablename__="admin_profile"
#     admin_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
#     username=db.Column(db.String(100),unique=True,nullable=False)
#     password=db.Column(db.String(50),nullable=False)


class UserCredentials(db.Model):
    __tablename__="user_credentials"
    user_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    email_id=db.Column(db.String(50),unique=True,nullable=False)
    password=db.Column(db.String(50),nullable=False)
    role=db.Column(db.Integer,nullable=False) #admin:0/user:1/staff:2

class UserDetails(db.Model):
    __tablename__="user_details"
    trekker_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user_credentials.user_id'))
    full_name=db.Column(db.String(100),nullable=False)
    email_id=db.Column(db.String(50),unique=True,nullable=False)
    password=db.Column(db.String(50),nullable=False)
    phone_num=db.Column(db.String(20),unique=True,nullable=False)
    address=db.Column(db.String(100),nullable=False)
    blacklist_status=db.Column(db.Boolean,default=False)

class TrekStaff(db.Model):
    __tablename__="trek_staff"
    staff_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user_credentials.user_id'))
    full_name=db.Column(db.String(100),nullable=False)
    email_id=db.Column(db.String(50),unique=True,nullable=False)
    password=db.Column(db.String(50),nullable=False)
    phone_num=db.Column(db.String(20),nullable=False)
    address=db.Column(db.String(100),nullable=False)
    approval_status=db.Column(db.Integer,nullable=False,default=0) #0-register,1-Approved
    blacklist_status=db.Column(db.Boolean,default=False)

class BookingDetails(db.Model):
    __tablename__='booking_details'
    booking_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user_details.user_id'))
    trek_id=db.Column(db.Integer,db.ForeignKey('trek_details.trek_id'))
    booking_date=db.Column(db.Date,nullable=False)
    booking_status=db.Column(db.Enum('Booked','Cancelled','Completed'),nullable=False)

class TrekDetails(db.Model):
    __tablename__='trek_details'
    trek_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    staff_id=db.Column(db.Integer,db.ForeignKey('trek_staff.staff_id'))
    trek_name=db.Column(db.String(100),nullable=False)
    location=db.Column(db.String(50),nullable=False)
    difficulty=db.Column(db.Enum('Easy','Moderate','Hard'),nullable=False)
    duration_days=db.Column(db.Integer,nullable=False)
    available_slots=db.Column(db.Integer,nullable=False)
    start_date=db.Column(db.Date,nullable=False)
    end_date=db.Column(db.Date,nullable=False)
    status=db.Column(db.Enum('Approved','Completed','Pending','Open','Closed'))
