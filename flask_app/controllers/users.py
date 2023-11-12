from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask_app.models import user

# ******** ROOT ROUTE *********
@app.route("/")
def user_entry():
    return render_template("index.html")



# ******** ADD/CREATE NEW user *********
@app.route("/users/create_user", methods=["POST"])
def create_user():
    
    if not user.User.validate_user_registration(request.form):
        return redirect("/")
    
    hashed_pw=bcrypt.generate_password_hash(request.form["password"])

    data={
        "f_name":request.form["f_name"],
        "l_name":request.form["l_name"],
        "email":request.form["email"],
        "position_title":request.form["position_title"],        
        "github_url":request.form["github_url"],
        "password":hashed_pw,
    }

    one_user_id=user.User.create_new_user(data)
    session["logged_in_id"]=one_user_id
    flash("Registration successful. You are now logged in!", "user_registration_success")
    return redirect(f"/users/dashboard/{session['logged_in_id']}")   

# ******** user login *********
@app.route("/users/user_login", methods=["POST"])
def user_login():
    one_user= user.User.validate_login(request.form)

    if not one_user:
        return redirect("/")
    
    session["logged_in_id"]=one_user.id
    flash("Login successful!", "user_login_success")
    return redirect(f"/users/dashboard/{session['logged_in_id']}")


# ******** LOGOUT *********
@app.route("/users/user_logout")
def logout():
    session.clear()
    flash ("You are now LOGGED OUT!", "logout_success")
    return redirect("/")