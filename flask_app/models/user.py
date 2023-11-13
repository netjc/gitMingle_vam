from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import project
# for validation messages, import flash
from flask import flash
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

URL_REGEX=re.compile(r'^((https?|ftp|smtp):\/\/)?(www.)?[a-z0-9]+\.[a-z]+(\/[a-zA-Z0-9#]+\/?)*$')

class User:
    db="gitMingle"

    def __init__(self, data):
        self.id=data["id"]

        self.f_name=data["f_name"]
        self.l_name=data["l_name"]
        self.email=data["email"]
        self.position_title=data["position_title"]
        self.github_url=data["github_url"]
        self.password=data["password"]
        self.created_at=data["created_at"]
        self.updated_at=data["updated_at"]
        # NOT PART OF DB
        self.listed_projects=[] 
        # PENDING - FOR PROJECT ADMIN 
        # self.join_project_requests=[]
        # self.projects_joined=[]


# ******** ADD/CREATE NEW user *********
    @classmethod
    def create_new_user(cls, data):
        query = """
            INSERT INTO users
            (f_name, l_name, email, position_title, github_url, password)
            VALUES(%(f_name)s, %(l_name)s, %(email)s, %(position_title)s, %(github_url)s, %(password)s);
        """
        results= connectToMySQL(cls.db).query_db(query, data)
        return results
    

# ******** GET INDIVIDUAL USER INFO *********
    @classmethod
    def get_user_info(cls, data):
        query = """
            SELECT * FROM users
            WHERE id = %(id)s;
        """
        results = connectToMySQL(cls.db).query_db(query, data) 
        return cls(results[0])
    
    @classmethod
    def get_user_by_email(cls, data):
        query = """
            SELECT * FROM users
            WHERE email = %(email)s;
        """
        results = connectToMySQL(cls.db).query_db(query, data) 
        if len(results)<1:
            return False
        
        return cls(results[0])

# ******** GET PROJECTS THE USER HAS LISTED/ADDED *********
    @classmethod
    def get_user_with_projects(cls, data):
        query = "SELECT * FROM users LEFT JOIN projects ON projects.user_id =users.id WHERE users.id = %(id)s;"
        
        results = connectToMySQL(cls.db).query_db(query, data )

        one_user = cls(results[0])

        for row in results:
            project_data = {
                "id": row["projects.id"],
                "user_id": row["user_id"],
                "project_name": row["project_name"],
                "short_description": row["short_description"],
                "max_team":row["max_team"],
                "current_team": row["current_team"],
                "github_link": row["github_link"],
                "long_description": row["long_description"],
                "languages_used": row["languages_used"],
                "help_needed": row["help_needed"],                
                "created_at": row["projects.created_at"],
                "updated_at": row["projects.updated_at"]
                }
            one_project=project.Project(project_data)
            one_user.listed_projects.append(one_project)
        return one_user
    
# ******** GET USERS WITH SAVED/LIKED PROJECTS *********** 
    @classmethod
    def get_user_with_saved_projects(cls,data):
        query="""
            SELECT * FROM users 
            JOIN favorites on users.id=favorites.user_id 
            JOIN projects ON favorites.project_id=projects.id 
            WHERE users.id=%(id)s;
            """
        results = connectToMySQL(cls.db).query_db(query, data )
        return results

# ******** GET USER WITH PROJECTS USER HAS JOINED*********** 
    @classmethod
    def get_user_with_joined_projects(cls,data):
        query="""
            SELECT * FROM users 
            JOIN team_members on users.id=team_members.user_id 
            JOIN projects ON team_members.project_id=projects.id 
            WHERE users.id=%(id)s;
            """
        results = connectToMySQL(cls.db).query_db(query, data )
        return results
    
# ******** SHOW ALL USERS *********
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"

        results = connectToMySQL(cls.db).query_db(query)

        all_users = []

        for user in results:
            all_users.append(cls(user))
        return all_users    

# ******** UPDATE USER PROFILE *********
    @classmethod
    def update_user(cls, data):
        query = """
            UPDATE users
            SET f_name=%(f_name)s, l_name=%(l_name)s, email=%(email)s, position_title=%(position_title)s, github_url=%(github_url)s, updated_at=NOW() 
            WHERE id = %(id)s;
        """
        return connectToMySQL(cls.db).query_db(query,data)
    
# ******** UPDATE PW*********
    @classmethod
    def update_pw(cls, data):
        query = """
            UPDATE users
            SET password=%(password)s, updated_at=NOW() 
            WHERE id = %(id)s;
        """
        return connectToMySQL(cls.db).query_db(query,data)    

# ************ VALIDATIONS ***************
    @staticmethod
    def validate_user_registration(data):
        is_valid = True 

        one_user=User.get_user_by_email(data)
        if one_user:
            is_valid=False
            flash(" ! Account already exists. Try logging in instead.", "user_registration")

        if len(data["f_name"]) < 3:
            flash(" ! First Name must be at least 3 characters.", "user_registration")
            is_valid = False

        if len(data["l_name"]) < 3:
            flash(" ! Last Name must be at least 3 characters.", "user_registration")
            is_valid = False

        if len(data["email"]) == 0:
            flash(" ! Email cannot be left empty.", "user_registration")
            is_valid = False

        if len(data["email"]) < 8:
            flash(" ! Email must be at least 8 characters.", "user_registration")
            is_valid = False

        if not EMAIL_REGEX.match(data["email"]): 
            flash(" ! Invalid email format. Try again.", "user_registration")
            is_valid = False

        if len(data["github_url"]) == 0:
            flash(" ! Github user URL cannot be left empty.", "user_registration")
            is_valid = False

        if not URL_REGEX.match(data["github_url"]): 
            flash(" ! Invalid url format. Try again.", "user_registration")
            is_valid = False

        if len(data["password"]) < 8:
            flash(" ! Password must be at least 8 characters.", "user_registration")
            is_valid = False

        if data["password"] != data["confirm_pw"]:
            is_valid=False
            flash(" ! Passwords do not match. Try again!", "user_registration")
        return is_valid
    
    @staticmethod
    def validate_login(data):
        is_valid = True
        one_user=User.get_user_by_email(data)

        if not one_user:
            flash(" ! Invalid email and/or password.", "user_login")
            return False

        if len(data["email"]) == 0:
            flash(" ! Email cannot be left empty.", "user_login")
            return False
        
        if len(data["password"]) == 0:
            flash( "! Password cannot be left empty.", "user_login")
            return False

        if not bcrypt.check_password_hash(one_user.password, data["password"]):
            flash(" ! Invalid email and/or password.", "user_login")
            return False

        return one_user
    
    @staticmethod
    def validate_user_update(data):
        is_valid = True

        if len(data["f_name"]) < 3:
            flash(" ! First Name must be at least 3 characters. Original data retained.", "user_update")
            is_valid = False

        if len(data["l_name"]) < 3:
            flash(" ! Last Name must be at least 3 characters. Original data retained.", "user_update")
            is_valid = False

        if len(data["email"]) == 0:
            flash(" ! Email cannot be left empty. Original data retained.", "user_update")
            is_valid = False

        if len(data["email"]) < 8:
            flash(" ! Email must be at least 8 characters. Original data retained.", "user_update")
            is_valid = False

        if not EMAIL_REGEX.match(data["email"]): 
            flash(" ! Invalid email format. Original data retained.", "user_update")
            is_valid = False

        if len(data["github_url"]) == 0:
            flash(" ! Github user URL cannot be left empty. Original data retained.", "user_update")
            is_valid = False

        if not URL_REGEX.match(data["github_url"]): 
            flash(" ! Invalid url format. Try again.", "user_update")
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_pw_update(data):
        is_valid = True

        if len(data["password"]) < 8:
            flash(" ! Password must be at least 8 characters. Password NOT updated.", "pw_update")
            is_valid = False

        if data["password"] != data["confirm_pw"]:
            is_valid=False
            flash(" ! Passwords do not match. Try again!", "pw_update")

        return is_valid    

