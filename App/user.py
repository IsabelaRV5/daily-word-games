from flask_login import UserMixin
from datetime import date, timedelta


class User(UserMixin):
    def __init__(self, id, username, password_hash, role="basic", permission="ok", wordle_streak=0, spelling_bee_streak=0, last_login_wordle=None, last_login_spelling_bee=None):
        self.id= id
        self.username= username
        self.password_hash= password_hash
        self.role= role
        self.permission= permission

        self.wordle_streak= wordle_streak
        self.spelling_bee_streak= spelling_bee_streak
        self.last_login_wordle= last_login_wordle
        self.last_login_spelling_bee= last_login_spelling_bee


    ### GET WORDLE STREAK NUM ###
    def get_wordle_streak(self) :
        today= date.today()
        yesterday= today - timedelta(days=1)
        
        # if first time playing --> streak=0
        if self.last_login_wordle is None :
            self.wordle_streak= 0

        # if already logged in today --> do nothing
        elif self.last_login_wordle == today :
            pass

        # if logged in exactly yesterday --> streak+1
        elif self.last_login_wordle == yesterday :
            self.wordle_streak+= 1

        # if missed a day --> reset
        else :
            self.wordle_streak= 0

        self.last_login_wordle = today
        
        return self.wordle_streak
    

    ### GET SPELLING BEE STREAK NUM ###
    def get_spelling_bee_streak(self) :
        today= date.today()
        yesterday= today - timedelta(days=1)
        
        # if first time playing --> streak=0
        if self.last_login_spelling_bee is None :
            self.spelling_bee_streak= 0

        # if already logged in today --> do nothing
        elif self.last_login_spelling_bee == today :
            pass

        # if logged in exactly yesterday --> streak+1
        elif self.last_login_spelling_bee == yesterday :
            self.spelling_bee_streak+= 1

        # if missed a day --> reset
        else :
            self.spelling_bee_streak= 0

        self.last_login_spelling_bee = today
        
        return self.spelling_bee_streak
    
    ### GET USER ROLE ###
    def is_allowed(self, user_role):
        if self.role == user_role:
            return True
        else:
            return False