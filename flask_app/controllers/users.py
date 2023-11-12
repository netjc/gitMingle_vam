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

# ******** UPDATE PROFILE - render *********
@app.route("/users/my_profile/<int:id>")
def profile_page(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")
        return redirect("/")

    data={"id": session["logged_in_id"]
    }

    return render_template("profile.html", current_user=user.User.get_user_info(data))
    # return render_template("profile.html", one_user=user1, fav_projects=user.User.get_user_saved_projects(data), current_user=user.User.get_user_info(data2))

# ******** UPDATE PROFILE - post & redirect *********
@app.route("/users/update_user", methods=["POST"])
def update_user_info():
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")
        return redirect("/")
        
    if not user.User.validate_user_update(request.form):
        return redirect(f"/users/my_profile/{session['logged_in_id']}")
    
    data={
        "f_name":request.form["f_name"],
        "l_name":request.form["l_name"],
        "email":request.form["email"],
        "position_title":request.form["position_title"],        
        "github_url":request.form["github_url"],
    }

    user.User.update_user(request.form)
    flash("User update SUCCESSFUL!", "user_update_success")
    return redirect(f"/users/my_profile/{session['logged_in_id']}")

# ******** UPDATE PROFILE - post & redirect *********
@app.route("/users/update_pw", methods=["POST"])
def new_pw():
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")
        return redirect("/")
        
    if not user.User.validate_pw_update(request.form):
        return redirect(f"/users/my_profile/{session['logged_in_id']}")
    
    hashed_pw=bcrypt.generate_password_hash(request.form["password"])

    data={
        "password":hashed_pw
    }

    user.User.update_pw(request.form)
    flash("Password UPDATED!", "pw_update_success")
    return redirect(f"/users/my_profile/{session['logged_in_id']}")