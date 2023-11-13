
from flask_app import app

from flask import Flask, render_template, redirect, request, session, flash

from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask_app.models import user, project



# ******** ROOT ROUTE *********
@app.route("/users/dashboard/<int:id>")
def user_page(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    

    data2={
        "id": session["logged_in_id"]
    }

    return render_template("dashboard.html", all_projects=project.Project.get_all_projects(), one_user=user.User.get_user_info(data2), all_users=user.User.get_all())

# ******** ADD new projects - render *********
@app.route("/projects/new_project")
def new_project():
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    data={
        "id": session["logged_in_id"]
    }
    return render_template("create_project.html", one_user=user.User.get_user_info(data))

# ******** ADD new project - POST & redirect *********
@app.route("/projects/list_project", methods=["POST"])
def create_project():
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    
    if not project.Project.validate_project(request.form):
        return redirect("/projects/new_project")

    one_project_id=project.Project.create_new_project(request.form)

    data2={
        "id": session["logged_in_id"]
    }
    flash("Project added!", "project_add_success")
    return redirect(f"/users/dashboard/{session['logged_in_id']}")
    # return redirect(f"/projects/show_project/{one_project_id}")

# ******** UPDATE project - render *********
@app.route("/projects/edit_project/<int:id>")
def project_update_form(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    data={
        "id": id
    }

    return render_template("update_project.html", project_to_update=project.Project.get_one_project(data))
    
# ******** UPDATE project - POST & redirect *********
@app.route("/projects/update_project", methods=["POST"])
def project_update():
    if not project.Project.validate_project_update(request.form):
        return redirect(f"/projects/edit_project/{request.form['id']}")
    data={
        "id": request.form['id']
    }
    project.Project.update_project(request.form)

    flash("Project successfully updated!", "project_update_success")
    return redirect(f"/users/dashboard/{session['logged_in_id']}")



# ******** SHOW ONE project *********
@app.route("/projects/show_project/<int:id>")
def project_page(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/")
    
    data={"id": id}
    data2={
        "id": session["logged_in_id"]
    }


    return render_template("show_project.html", project1=project.Project.get_one_project(data), user1=user.User.get_user_info(data2))


# ******** DELETE project *********
@app.route("/projects/delete_project/<int:id>")
def delete(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/")
    data={"id": id}
    project.Project.delete_project(id)
    return redirect(f"/users/dashboard/{session['logged_in_id']}")


# *********** SAVE PROJECT ***********
@app.route("/projects/favorites/<int:id>")
def fav_project(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    data={
        "project_id":id,
        "user_id":session['logged_in_id']
    }
    project.Project.save_project(data)
    return redirect(f"/users/dashboard/{session['logged_in_id']}")

# ******** DELETE SAVED PROJECT *********
@app.route("/projects/delete_saved/<int:id>")
def delete_fav(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    data={"id": id}
    project.Project.delete_saved_project(id)
    return redirect(f"/users/profile/{session['logged_in_id']}")

# *********** JOIN PROJECT ***********
@app.route("/projects/join_project/<int:id>")
def join_project_team(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    data={
        "project_id":id,
        "user_id":session['logged_in_id']
    }
    project.Project.join_team(data)
    return redirect(f"/users/profile/{session['logged_in_id']}")

# ******** DELETE MEMBER / LEAVE PROJECT *********
@app.route("/projects/delete_member/<int:id>")
def leave_team(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    
    data={"id": id}
    project.Project.delete_member(id)
    return redirect(f"/users/profile/{session['logged_in_id']}")


# search by languages_used

# @app.route("/projects/search_results/<int:languages_used>")
# def results_page(languages_used):
#     if "logged_in_id" not in session:
#         flash("You must be logged in to view the requested page.", "login_required")        
#         return redirect("/")
    
#     data={
#         "languages_used":languages_used
#     }
#     return render_template("search_results.html", langs_used_search=project.Project.get_by_language(data))

# @app.route("/projects/project_languages_search", methods=["POST"])
# def lang_search():
#     if "logged_in_id" not in session:
#         flash("You must be logged in to view the requested page.", "login_required")        
#         return redirect("/")

#     return redirect(f"/projects/search_results/{request.form['languages_used']}")