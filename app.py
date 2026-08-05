from flask import Flask
from flask import render_template
app=Flask(__name__)


#login page
@app.route("/login")
def signin():
    return render_template("login_page.html")

#registration page
@app.route("/registration")
def register():
    return render_template("register_page.html")

@app.route("/admin_dashboard")
def admin_dash():
    return render_template("admin_dashboard.html")


if __name__=="__main__":
    app.run(debug=True)