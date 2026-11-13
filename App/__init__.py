from flask import Flask, g, render_template, redirect, request, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from App.game import Game
from App.wordle import Wordle
from App.spellingBee import SpellingBee
from App.user import User
import werkzeug, psycopg2, json, datetime

def create_app(env = "development"):
    app = Flask(__name__)
    app.config.from_file(f"{env}.json", load=json.load)
    app.config.from_prefixed_env()
    if not app.secret_key:
        raise RuntimeError("Set FLASK_SECRET_KEY before starting the app.")
    login_manager = LoginManager()
    login_manager.init_app(app)

# DATABASE ---------------------------------------------------

    def get_db():
        '''
        Function that gets the db
        '''
        db = g.get("_database")
        if not db:
            g._database = psycopg2.connect(dbname = app.config["DBNAME"], user = app.config["DBUSER"], password = app.config["DBPASS"], host = app.config["DBHOST"], port = app.config["DBPORT"])
            db = g._database
        return db

    def run_query(query, params=()):
        '''
        Helper function that gets the cursor and executes the query
        '''
        conn = get_db()
        cur = conn.cursor()
        cur.execute(query, params)
        return cur

    @app.teardown_appcontext
    def cleanup(exception):
        db = g.get("_database")
        if db:
            db.close()

# ROOT --------------------------------------------------------

    @app.route("/")
    def root():
        '''
        GET route for root
        Renders welcome.html template
        '''
        if current_user.is_authenticated:
            return redirect(url_for("home"))
        return render_template("welcome.html")
    
# HOME --------------------------------------------------------

    @app.route("/home")
    def home():
        '''
        GET route for home
        Renders home.html template with games to display and game streaks
        '''
        games = get_games()
        if not games:
            flash("No games available at the moment!")
        if current_user.is_authenticated:
            return render_template("home.html", games = games, wordle_streak = current_user.wordle_streak, spelling_bee_streak = current_user.spelling_bee_streak)
        return render_template("home.html", games = games)
    
# USERS ----------------------------------------------------------                                                                       
    def get_users():
        '''
        Function that gets the users from the db
        '''
        rows = run_query("SELECT id, username, pswd_hash, role, permission, wordle_streak, spelling_bee_streak, last_login_wordle, last_login_spelling_bee FROM users").fetchall()
        return map(lambda x: User(x[0],x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8]), rows)

    def get_username(user_id):
        username = run_query("SELECT * FROM users WHERE id = %s", (user_id,)).fetchone()
        return username[1]

    def can_play(user, game_type):
        '''
        Helper function that checks if the user is blocked for all
        or certain games
        '''
        if user.permission == "blocked":
            return False
        if user.permission == game_type:
            return False
        return True
    
    @app.route("/admin")
    @login_required
    def admin_view():
        '''
        GET route to render the admin template
        '''
        if not current_user.is_allowed('admin'):
            flash("You are not an admin!")
            return redirect(url_for("home"))
        users = []
        for user in get_users():
            if str(user.id) != str(current_user.id):
                users.append(user)
        return render_template("admin.html", users = users)
    
    @app.route("/mod")
    @login_required
    def mod_view():
        '''
        GET route to render the mod template
        '''
        if not current_user.is_allowed('admin') and not current_user.is_allowed('mod'):
            flash("You are not an admin or a mod!")
            return redirect(url_for("home"))
        users = []
        for user in get_users():
            if str(user.id) != str(current_user.id):
                users.append(user)
        return render_template("mod.html", users = users)
    
    @app.route("/admin/block/<int:user_id>", methods=["POST"])
    @login_required
    def block_user(user_id):
        '''
        GET route to block an user from all games
        '''
        if not current_user.is_allowed('admin'):
            flash("You are not an admin!")
            return redirect(url_for("home"))
        run_query("UPDATE users SET permission = %s WHERE id = %s", ("blocked", user_id))
        get_db().commit()
        username = get_username(user_id)
        flash(f"User {username} blocked from all games!")
        return redirect(url_for("admin_view"))
    
    @app.route("/admin/block-wordle/<int:user_id>", methods=["POST"])
    @login_required
    def block_wordle(user_id):
        '''
        GET route to block an user from Wordle
        '''
        if not current_user.is_allowed('admin'):
            flash("You are not an admin!")
            return redirect(url_for("home"))
        run_query("UPDATE users SET permission = %s WHERE id = %s", ("wordle", user_id))
        get_db().commit()
        username = get_username(user_id)
        flash(f"User {username} blocked from Wordle!")
        return redirect(url_for("admin_view"))
    
    @app.route("/admin/block-spelling/<int:user_id>", methods=["POST"])
    @login_required
    def block_spelling(user_id):
        '''
        GET route to block an user from Spelling bee
        '''
        if not current_user.is_allowed('admin'):
            flash("You are not an admin!")
            return redirect(url_for("home"))
        run_query("UPDATE users SET permission = %s WHERE id = %s",("spelling_bee", user_id))
        get_db().commit()
        username = get_username(user_id)
        flash(f"User {username} blocked from Spelling Bee!")
        return redirect(url_for("admin_view"))
    
    @app.route("/admin/unblock/<int:user_id>", methods=["POST"])
    @login_required
    def unblock_user(user_id):
        '''
        GET route to unblock a user
        '''
        if not current_user.is_allowed('admin'):
            flash("You are not an admin!")
            return redirect(url_for("home"))
        run_query("UPDATE users SET permission = %s WHERE id = %s",("ok", user_id))
        get_db().commit()
        username = get_username(user_id)
        flash(f"User {username} unblocked!")
        return redirect(url_for("admin_view"))
    
    @app.route("/admin/delete/<int:user_id>", methods=["POST"])
    @login_required
    def delete_user(user_id):
        '''
        GET route to delete a user
        '''
        if not current_user.is_allowed('admin'):
            flash("You are not an admin!")
            return redirect(url_for("home"))
        username = get_username(user_id)
        run_query("DELETE FROM users WHERE id = %s", (user_id,))
        get_db().commit()
        flash(f"User {username} deleted!")
        return redirect(url_for("admin_view"))
    
    @app.route("/admin/change-admin/<int:user_id>", methods=["POST"])
    @login_required
    def make_admin(user_id):
        '''
        GET route to change user role to admin
        '''
        if not current_user.is_allowed('admin'):
            flash("You are not an admin!")
            return redirect(url_for("home"))
        run_query("UPDATE users SET role = %s WHERE id = %s",("admin", user_id))
        get_db().commit()
        username = get_username(user_id)
        flash(f"User {username} is now an admin!")
        return redirect(url_for("admin_view"))

    @app.route("/admin/change-mod/<int:user_id>", methods=["POST"])
    @login_required
    def make_mod(user_id):
        '''
        GET route to change user role to mod
        '''
        if not current_user.is_allowed('admin'):
            flash("You are not an admin!")
            return redirect(url_for("home"))
        run_query("UPDATE users SET role = %s WHERE id = %s",("mod", user_id))
        get_db().commit()
        username = get_username(user_id)
        flash(f"User {username} is now a mod!")
        return redirect(url_for("admin_view"))
    
    @app.route("/admin/change-basic/<int:user_id>", methods=["POST"])
    @login_required
    def make_basic(user_id):
        '''
        GET route to change user role to basic
        '''
        if not current_user.is_allowed('admin'):
            flash("You are not an admin!")
            return redirect(url_for("home"))
        run_query("UPDATE users SET role = %s WHERE id = %s",("basic", user_id))
        get_db().commit()
        username = get_username(user_id)
        flash(f"User {username} is now a basic user!")
        return redirect(url_for("admin_view"))
    
    @app.route("/history")
    def history():
        '''
        GET route to display a user's history
        '''
        if current_user.is_authenticated:
            rows = run_query("SELECT games.type, games.day_to_play, game_sessions.state FROM games INNER JOIN game_sessions ON games.id = game_sessions.game_id WHERE game_sessions.user_id = %s", (current_user.id,)).fetchall()
            sessions = []
            for game_type, day, state in rows:
                if state:
                    sessions.append({ "type": game_type, "day": day, "state": json.loads(state) })
            return render_template("history.html", sessions = sessions)
        return render_template("history.html")
      
    @app.route("/mod/disable-wordle", methods=["POST"])
    @login_required
    def disable_wordle():
        '''
        GET route to disable wordle for everyone
        '''
        if not current_user.is_allowed('admin') and not current_user.is_allowed('mod'):
            flash("You are not an admin or a mod!")
            return redirect(url_for("home"))
        run_query("UPDATE games SET is_enabled = %s WHERE type = %s",(False, "wordle"))
        get_db().commit()
        flash("Wordle is now disabled!")
        if current_user.is_allowed('admin'):
            return redirect(url_for("admin_view"))
        else:
            return redirect(url_for("mod_view"))


    @app.route("/mod/disable-spelling-bee", methods=["POST"])
    @login_required
    def disable_spelling_bee():
        '''
        GET route to disable spelling bee for everyone
        '''
        if not current_user.is_allowed('admin') and not current_user.is_allowed('mod'):
            flash("You are not an admin or a mod!")
            return redirect(url_for("home"))
        run_query("UPDATE games SET is_enabled = %s WHERE type = %s",(False, "spelling_bee"))
        get_db().commit()
        flash("Spelling bee is now disabled!")
        if current_user.is_allowed('admin'):
            return redirect(url_for("admin_view"))
        else:
            return redirect(url_for("mod_view"))
    
    @app.route("/mod/enable-wordle", methods=["POST"])
    @login_required
    def enable_wordle():
        '''
        GET route to enable wordle for everyone
        '''
        if not current_user.is_allowed('admin') and not current_user.is_allowed('mod'):
            flash("You are not an admin or a mod!")
            return redirect(url_for("home"))
        run_query("UPDATE games SET is_enabled = %s WHERE type = %s",(True, "wordle"))
        get_db().commit()
        flash("Wordle is now enabled!")
        if current_user.is_allowed('admin'):
            return redirect(url_for("admin_view"))
        else:
            return redirect(url_for("mod_view"))

    @app.route("/mod/enable-spelling-bee", methods=["POST"])
    @login_required
    def enable_spelling_bee():
        '''
        GET route to enable spelling bee for everyone
        '''
        if not current_user.is_allowed('admin') and not current_user.is_allowed('mod'):
            flash("You are not an admin or a mod!")
            return redirect(url_for("home"))
        run_query("UPDATE games SET is_enabled = %s WHERE type = %s",(True, "spelling_bee"))
        get_db().commit()
        flash("Spelling bee is now enabled!")
        if current_user.is_allowed('admin'):
            return redirect(url_for("admin_view"))
        else:
            return redirect(url_for("mod_view"))


# LOGIN --------------------------------------------------------

    @login_manager.user_loader
    def user_loader(id):
        '''
        User loader that initializes user for login
        '''
        record = run_query("SELECT username, pswd_hash, role, permission, wordle_streak, spelling_bee_streak, last_login_wordle, last_login_spelling_bee  FROM users WHERE id = %s LIMIT 1", (id,)).fetchone()
        if not record:
            return
        user = User(id, record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7])
        return user

    @app.route("/login", methods = ["GET"])
    def login_form():
        '''
        GET route for login form
        Renders login.html template 
        '''
        return render_template("login.html")

    @app.route("/login", methods = ["POST"])
    def login():
        '''
        POST route for login
        Gets username from form, tries to find it in database
        Checks to see if the hash matches the one in the database
        '''
        username = request.form["username"]
        record = run_query("SELECT id, pswd_hash, role, permission, wordle_streak, spelling_bee_streak, last_login_wordle, last_login_spelling_bee FROM users WHERE username = %s LIMIT 1", (username,)).fetchone()                                   
        if not record or not werkzeug.security.check_password_hash(record[1], request.form["username"] + request.form["password"]):
            flash("No user with this username and/or password found!")
            return redirect(url_for('login'))
        user = User(record[0], username, record[1], record[2], record[3], record[4], record[5], record[6], record[7])
        login_user(user)
        return redirect(url_for('home'))
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('root'))

# REGISTER --------------------------------------------------------

    @app.route("/register", methods=["GET"])
    def register_form():
        '''
        GET route for register form
        Renders register.html template 
        '''
        return render_template("register.html")

    @app.route("/register", methods=["POST"])
    def register():
        '''
        POST route for register
        Gets username and password (and confirmed password) from form
        Does validation to see if existing username or passwords entered not the same
        Creates password hash
        Insert values into the database to create account
        '''
        username = request.form["username"]
        password = request.form["password"]
        confirmed_password = request.form["confirmPassword"]
        if confirmed_password != password:
            flash("The passwords you entered are not the same! Please enter the same password twice!")
            return redirect(url_for("register_form"))
        existing = run_query("SELECT id FROM users WHERE username = %s LIMIT 1",(username,)).fetchone()
        if existing:
            flash("This username already exists! Please pick another one!")
            return redirect(url_for("register_form"))
        password_hash = werkzeug.security.generate_password_hash(username + password)
        run_query("INSERT INTO users (username, pswd_hash, role, permission) VALUES (%s, %s, %s, %s)", (username, password_hash, 'basic', 'ok'))
        get_db().commit()
        flash("Account created! Now you can log in.")
        return redirect(url_for("login_form"))
    
# GAMES --------------------------------------------------------

    def get_games():
        '''
        Function that gets the games from the db depending on the day
        '''
        rows = run_query("SELECT type, day_to_play, is_enabled FROM games WHERE day_to_play = %s",(get_day(),)).fetchall()
        games = []
        descriptions= {
            "wordle": "Guess the hidden five-letter word in six tries",
            "spelling_bee": "Create as many words as possible using the given letters"
        }
        for game_type, day_to_play, is_enabled in rows:
            formatted_name= game_type.replace("_", " ").title()
            if is_enabled and (not current_user.is_authenticated or can_play(current_user, game_type)):
                games.append({ "type": game_type, "display_name": formatted_name, "day": day_to_play, "description": descriptions[game_type]})
        return games

    def get_day():
        '''
        Helper function that gets the day of the games to be played
        '''
        day = datetime.date.today().weekday() + 1
        return day
    
# WORDLE --------------------------------------------------------
    
    @app.route("/wordle", methods = ["GET"])
    def wordle():
        '''
        GET route for wordle based on the day.
        start game session for user if not started yet
        '''
        day = get_day()
        game = run_query("SELECT id, is_enabled FROM games WHERE type = %s AND day_to_play = %s",("wordle", day)).fetchone()
        if not game:
            return {"error": "Game not found"}, 404
        game_id = game[0]
        game_enabled = game[1]
        if not game_enabled:
            flash("Wordle is down! Try again later")
            return redirect(url_for("home"))
        if(current_user.is_authenticated):
            if not can_play(current_user, "wordle"):
                flash("You have been blocked from Wordle")
                return redirect(url_for("home"))
            wordle = Wordle(game_id, day)
            session = run_query("SELECT id FROM game_sessions WHERE user_id = %s AND game_id = %s", (current_user.id, game_id)).fetchone()
            if not session:
                state = wordle.get_state()
                run_query("INSERT INTO game_sessions (user_id, game_id, state) VALUES (%s, %s, %s)", (current_user.id, game_id, json.dumps(state)),)
                get_db().commit()
            return render_template("wordle.html", wordle_streak = current_user.wordle_streak)
        return render_template("wordle.html")
        
    
    @app.route("/api/wordle", methods=["POST"])
    def wordle_post():
        '''
        POST route for wordle based on the day.
        update user game session based on state
        '''
        day = get_day()
        data = request.get_json()
        saved_guesses = data["guesses"]
        current_guess = data["currentGuess"]
        result = {}
        game = run_query("SELECT id, is_enabled FROM games WHERE type = %s AND day_to_play = %s",("wordle", day)).fetchone()
        if not game:
            return {"error": "Game not found"}, 404
        game_id = game[0]
        game_enabled = game[1]
        if not game_enabled:
            return {"error": "Wordle is down! Try again later"}, 403
        wordle = Wordle(game_id, day)
        if(current_user.is_authenticated):
            if not can_play(current_user, "wordle"):
                return {"error": "Access denied"}, 403
            session = run_query("SELECT id, state FROM game_sessions WHERE user_id = %s AND game_id = %s", (current_user.id, game_id)).fetchone()
            if not session:
                return {"error": "Session not found"}, 404
            session_id = session[0]
            saved_state = session[1]
            if saved_state:
                state = json.loads(saved_state)
                wordle.guesses = state["guesses"]
                wordle.attempts = len(state["guesses"])
                wordle.status = state["status"]
                wordle.won = state["won"]
                wordle.is_over = state["status"] == "finished"
            result["guess_state"] = wordle.make_move(current_guess)
            result["user"] = current_user.is_authenticated
            if wordle.attempts == 1 :
                wordle_streak= current_user.get_wordle_streak()
                if wordle_streak == 0 and current_user.last_login_wordle == datetime.date.today() :
                    wordle_streak= 1
                run_query("UPDATE users SET wordle_streak = %s, last_login_wordle = %s WHERE id = %s",(wordle_streak, current_user.last_login_wordle, current_user.id))
                result["wordle_streak"]= wordle_streak
            run_query("UPDATE game_sessions SET state = %s WHERE id = %s", (json.dumps(wordle.get_state()), session_id),)
            get_db().commit()
        else:
            wordle.guesses = saved_guesses
            wordle.attempts = len(saved_guesses)
            result["guess_state"] = wordle.make_move(current_guess)
            result["user"] = current_user.is_authenticated
        if "error" in result["guess_state"]:
            return result["guess_state"], 400
        return result
    
    @app.route("/api/wordle", methods=["GET"])
    def get_wordle_state():
        '''
        GET route for wordle api to get 
        the game's state
        '''
        day = get_day()
        game = run_query("SELECT id, is_enabled FROM games WHERE type = %s AND day_to_play = %s", ("wordle", day)).fetchone()
        if not game:
            return {"error": "Game not found"}, 404
        game_id = game[0]
        game_enabled = game[1]
        if not game_enabled:
            return {"error": "Wordle is down! Try again later"}, 403
        wordle = Wordle(game_id, day)
        if(current_user.is_authenticated):
            if not can_play(current_user, "wordle"):
                return {"error": "Access denied"}, 403
            session = run_query("SELECT state FROM game_sessions WHERE user_id = %s AND game_id = %s", (current_user.id, game_id)).fetchone()
            if session and session[0]:
                state = json.loads(session[0])
                wordle.guesses = state["guesses"]
                wordle.attempts = len(state["guesses"])
                wordle.status = state["status"]
                wordle.won = state["won"]
                wordle.is_over = state["status"] == "finished"
        wordleState = {"wordle" : wordle.get_state(),"user" : current_user.is_authenticated}
        return json.dumps(wordleState)

# SPELLING BEE ---------------------------------------------------

    @app.route("/spelling-bee", methods = ["GET"])
    def spelling_bee():
        '''
        GET route for spelling bee based on the day.
        start game session for user if not started yet
        '''
        day = get_day()
        game = run_query("SELECT id, is_enabled FROM games WHERE type = %s AND day_to_play = %s",("spelling_bee", day)).fetchone()
        if not game:
            return {"error": "Game not found"}, 404
        game_id = game[0]
        game_enabled = game[1]
        if not game_enabled:
            flash("Spelling Bee is down! Try again later")
            return redirect(url_for("home"))
        spelling_bee = SpellingBee(game_id, day)
        if(current_user.is_authenticated):
            if not can_play(current_user, "spelling_bee"):
                flash("You have been blocked from Spelling Bee")
                return redirect(url_for("home"))
            session = run_query("SELECT id FROM game_sessions WHERE user_id = %s AND game_id = %s", (current_user.id, game_id)).fetchone()
            if not session:
                state = spelling_bee.get_state()
                run_query("INSERT INTO game_sessions (user_id, game_id, state) VALUES (%s, %s, %s)", (current_user.id, game_id, json.dumps(state)),)
                get_db().commit()
            return render_template("spellingBee.html", spelling_bee_streak = current_user.spelling_bee_streak)
        return render_template("spellingBee.html")

    @app.route('/api/spelling-bee')
    def get_spelling_bee_state():
        '''
        GET route for spelling bee api to get 
        the game's state
        '''
        day = get_day()
        game= run_query('SELECT id, is_enabled FROM games WHERE type = %s AND day_to_play = %s', ('spelling_bee', day)).fetchone()
        if not game :
            return {"error": "Game not found"}, 404
        game_id= game[0]
        game_enabled = game[1]
        if not game_enabled:
            return {"error": "Spelling Bee is down! Try again later"}, 403
        spelling_bee = SpellingBee(game_id, day)
        if(current_user.is_authenticated):
            if not can_play(current_user, "spelling_bee"):
                return {"error": "Access denied"}, 403
            session= run_query('SELECT state FROM game_sessions WHERE user_id = %s AND game_id = %s', (current_user.id, game_id)).fetchone()
            if session and session[0]:
                state = json.loads(session[0])
                spelling_bee.tier = state["tier"]
                spelling_bee.letters= state["letters"]
                spelling_bee.score = state["score"]
                spelling_bee.guesses = state["guesses"]
                spelling_bee.status = state["status"]
                spelling_bee.is_over = state["status"] == "finished"
        spellingBee_State = {"spellingBee" : spelling_bee.get_state(), "user" : current_user.is_authenticated}
        if current_user.is_authenticated:
            spellingBee_State["spelling_bee_streak"] = current_user.spelling_bee_streak
        return json.dumps(spellingBee_State)

    @app.route("/api/spelling-bee", methods=["POST"])
    def spelling_bee_post():
        '''
        POST route for spelling bee based on the day.
        update user game session based on state
        '''
        day = get_day()
        data = request.get_json()
        user_guess = data["user_guess"]

        # For guest only ------------
        guesses = data["guesses"]
        score = data["score"]
        is_over = data["is_over"]
        # ---------------------------

        result = {}
        game = run_query("SELECT id, is_enabled FROM games WHERE type = %s AND day_to_play = %s",("spelling_bee", day)).fetchone()
        if not game:
            return {"error": "Game not found"}, 404
        game_id = game[0]
        game_enabled = game[1]
        if not game_enabled:
            return {"error": "Spelling Bee is down! Try again later"}, 403
        
        spelling_bee = SpellingBee(game_id, day)

        # If user is logged in
        if(current_user.is_authenticated):
            if not can_play(current_user, "spelling_bee"):
                return {"error": "Access denied"}, 403
            session = run_query("SELECT id, state FROM game_sessions WHERE user_id = %s AND game_id = %s", (current_user.id, game_id)).fetchone()
            if not session:
                return {"error": "Session not found"}, 404
            session_id = session[0]
            saved_state = session[1]
            if saved_state:
                state = json.loads(saved_state)
                spelling_bee.tier = state["tier"]
                spelling_bee.letters= state["letters"]
                spelling_bee.score = state["score"]
                spelling_bee.guesses = state["guesses"]
                spelling_bee.status = state["status"]
                spelling_bee.is_over = state["status"] == "finished"
            result["guess_state"] = spelling_bee.make_move(user_guess)
            result["user"] = current_user.is_authenticated
            if len(spelling_bee.guesses) == 1 :
                spelling_bee_streak= current_user.get_spelling_bee_streak()
                if spelling_bee_streak == 0 and current_user.last_login_spelling_bee == datetime.date.today() :
                    spelling_bee_streak= 1
                run_query("UPDATE users SET spelling_bee_streak = %s, last_login_spelling_bee = %s WHERE id = %s",(spelling_bee_streak, current_user.last_login_spelling_bee, current_user.id))
                result["spelling_bee_streak"]= spelling_bee_streak
            run_query("UPDATE game_sessions SET state = %s WHERE id = %s", (json.dumps(spelling_bee.get_state()), session_id),)
            get_db().commit()

        # If user is guest
        else:
            spelling_bee.guesses = guesses
            spelling_bee.score = score
            spelling_bee.is_over = is_over
            result["guess_state"] = spelling_bee.make_move(user_guess)
            result["user"] = current_user.is_authenticated
        if "error" in result["guess_state"]:
            return result["guess_state"], 400
        
        return result

    return app
