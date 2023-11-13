from flask_app.config.mysqlconnection import connectToMySQL
# for validation messages, import flash
from flask import flash
from flask_app.models import user
import re
# URL_REGEX=re.compile(r'^((https?|ftp|smtp):\/\/)?(www.)?[a-z0-9]+\.[a-z]+(\/[a-zA-Z0-9#]+\/?)*$')

class Project:
    db="gitMingle"

    def __init__(self, data):
        self.id=data["id"]
        self.user_id=data["user_id"]
        self.project_name=data["project_name"]
        self.short_description=data["short_description"]
        self.max_team=data["max_team"]
        self.current_team=data["current_team"]
        self.github_link=data["github_link"]
        self.long_description=data["long_description"]
        self.languages_used=data["languages_used"]
        self.help_needed=data["help_needed"]
        self.created_at=data["created_at"]
        self.updated_at=data["updated_at"]
        # NOT PART OF DB
        self.project_creator=None


# ******** ADD/CREATE NEW project*********
    @classmethod
    def create_new_project(cls, data):
        query = """
            INSERT INTO projects
            (user_id, project_name, short_description, max_team, current_team, github_link, long_description,languages_used, help_needed, created_at, updated_at)
            VALUES(%(user_id)s, %(project_name)s, %(short_description)s, %(max_team)s, %(current_team)s, %(github_link)s, %(long_description)s, %(languages_used)s, %(help_needed)s,NOW(), NOW() );
        """
        results= connectToMySQL(cls.db).query_db(query, data)
        return results
   
    
# ******** GET ALL PROJECTS *********
    @classmethod
    def get_all_projects(cls):
        query = """
            SELECT * FROM projects
            JOIN users ON projects.user_id=users.id;
            """

        results = connectToMySQL(cls.db).query_db(query)

        all_projects = []

        for record in results:
            one_project=cls(record)
            one_project.project_creator=user.User(parse_user_data(record))
            all_projects.append(one_project)
        return all_projects
# --GET ALL FTs END-----------------------------------

# ******** FOR SEARCH - GET ALL PROJECTS BY LANGUAGE USED *********
    # @classmethod
    # def get_by_language(cls, data):
    #     query = """
    #         SELECT * FROM projects
    #         WHERE projects.languages_used=%(languages_used)s;
    #         """
    #     lang_search_results = connectToMySQL(cls.db).query_db(query, data) 

    #     projects_by_languages_used = []

    #     if lang_search_results:
    #         for one_result in lang_search_results:
    #             one_project_with_result=cls(one_result)


    #             projects_by_languages_used.append(one_project_with_result)
    #             return projects_by_languages_used
    #     # print (projects_by_languages_used)
    #     return projects_by_languages_used


# ******** GET ONE PROJECT *********
    @classmethod
    def get_one_project(cls, data):
        query = """
            SELECT * FROM projects
            JOIN users ON projects.user_id=users.id
            WHERE projects.id = %(id)s;
        """
        results = connectToMySQL(cls.db).query_db(query, data) 
        
        one_project= cls(results[0])

        one_project.project_creator=user.User(parse_user_data(results[0]))

        return one_project

    
# ******** UPDATE PROJECT *********
    @classmethod
    def update_project(cls, data):
        query = """
            UPDATE projects
            SET project_name=%(project_name)s, short_description=%(short_description)s, max_team=%(max_team)s, current_team=%(current_team)s, github_link=%(github_link)s, long_description=%(long_description)s, languages_used=%(languages_used)s, help_needed=%(help_needed)s, updated_at=NOW() 
            WHERE id = %(id)s;
        """

        return connectToMySQL(cls.db).query_db(query,data)
    
# ******** DELETE PROJECT *********
    @classmethod
    def delete_project(cls, id):
        query="""
            DELETE FROM projects
            WHERE id=%(id)s;
        """
        data={"id": id}
        return connectToMySQL(cls.db).query_db(query, data)

# ******** ADD SAVED PROJECT *********
    @classmethod
    def save_project(cls, data):
        query="""
            INSERT INTO favorites (project_id, user_id) 
            VALUES (%(project_id)s, %(user_id)s)
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
# ******** DELETE SAVED PROJECT *********
    @classmethod
    def delete_saved_project(cls, id):
        query="""
            DELETE FROM favorites
            WHERE project_id=%(id)s;
        """
        data={"id": id}
        return connectToMySQL(cls.db).query_db(query, data)
    
# ******** JOIN TEAM/ REQUEST TO JOIN (DEFAULT STATUS IS "PENDING" ) *********
    @classmethod
    def join_team(cls, data):
        query="""
            INSERT INTO team_members (project_id, user_id, member_type, status, created_at, updated_at) 
            VALUES (%(project_id)s, %(user_id)s, "NONE", "PENDING", NOW(), NOW());
        """
        return connectToMySQL(cls.db).query_db(query, data)
    
# ******** DELETE TEAM MEMBER / LEAVE TEAM *********
    @classmethod
    def delete_member(cls, id):
        query="""
            DELETE FROM team_members
            WHERE project_id=%(id)s;
        """
        data={"id": id}
        return connectToMySQL(cls.db).query_db(query, data)


# -- STATIC METHODS BELOW -----------------------------------------------------------

    # ************ VALIDATE project ***************
    @staticmethod
    def validate_project(data):
        is_valid = True

        if len(data["project_name"]) <1:
            flash("Business Name cannot be left empty", "projects")
            is_valid = False

        if len(data["short_description"]) <1:
            flash("Brief description cannot be left empty.", "projects")
            is_valid = False

        if len(data["short_description"]) >110:
            flash("Brief description cannot be longer than 110 characters. (You can enter full description below.)", "projects")
            is_valid = False

        if len(data["max_team"]) <1:
            flash("Can't leave empty.", "project")
            is_valid = False        

        if len(data["current_team"]) <1:
            flash("Can't leave empty.", "project")
            is_valid = False                    

        # if int(data["max_team"]) <2:
        #     flash("Max # of team members must be at least 2.", "project")
        #     is_valid = False

        # if int(data["max_team"]) >10:
        #     flash("Max # of team members can't be more than 10.", "project")
        #     is_valid = False        

        # if int(data["current_team"]) <1:
        #     flash("Current # of team members must be at least 1.", "project")
        #     is_valid = False
        
        if len(data["github_link"]) == 0:
            flash(" ! GitHub repo URL cannot be left empty.", "projects")
            is_valid = False

        # if not URL_REGEX.match(data["github_link"]): 
        #     flash(" ! Invalid url format. Try again.", "projects")
        #     is_valid = False

        if len(data["long_description"]) <1:
            flash("Description cannot be left empty.", "projects")
            is_valid = False

        if len(data["languages_used"]) <1:
            flash("You must choose at least one language", "projects")
            is_valid = False

        if len(data["help_needed"]) <1:
            flash("You can't leave this empty.", "projects")
            is_valid = False

        return is_valid
    
# ************ VALIDATE project UPDATE ***************
    @staticmethod
    def validate_project_update(data):
        is_valid = True

        if len(data["project_name"]) <1:
            flash("Business Name cannot be left empty. Original info retained.", "project_update")
            is_valid = False

        if len(data["short_description"]) <1:
            flash("Description field cannot be left empty. Original info retained.", "project_update")
            is_valid = False


        
        if len(data["github_link"]) == 0:
            flash(" ! GitHub repo URL cannot be left empty.", "project_update")
            is_valid = False



        if len(data["long_description"]) <1:
            flash("Description cannot be left empty.", "project_update")
            is_valid = False

        if len(data["languages_used"]) <1:
            flash("You must choose at least one language", "project_update")
            is_valid = False

        if len(data["help_needed"]) <1:
            flash("You can't leave this empty.", "project_update")
            is_valid = False

        return is_valid

def parse_user_data(record):
    if "users.id" in record:
        user_data={
                "id":record["users.id"],
                "f_name":record["f_name"],
                "l_name":record["l_name"],
                "email":record["email"],
                "position_title":record["position_title"],
                "github_url":record["github_url"],
                "password":record["password"],
                "created_at":record["users.created_at"],
                "updated_at":record["users.updated_at"],
            }
    return user_data