import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, utc_time

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///audio_library.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show last added podcast episodes"""
    manager_id = session["user_id"]

    ## Show the last items added
    latest_additions = db.execute(
        "SELECT id, program_name, chapter_number, chapter_title, chunk, total_chunks FROM podcast WHERE username_id = ? ORDER BY id DESC LIMIT 6",
        manager_id,
    )

    return render_template(
        "index.html",
        latest_additions=latest_additions
    )


@app.route("/insert", methods=["GET", "POST"])
@login_required
def insert():
    """Insert podcast data"""

    # User reached route via POST (as by submitting a form via POST)
    manager_id = session["user_id"]

    # One of the categories into which each podcast can be divided is language.
    language_list = ["chinese", "spanish", "english", "arabic", "hindi", "bengali", "portuguese", "russian", "japanese", "french", "german", "italian"]
    language_list = sorted(language_list)

    if request.method == "POST":
        language = request.form.get("language")

        if language not in language_list:
            return apology("typo or not supported", 400)
        
        # Other fields that describe the audio
        program_name = request.form.get("program_name")
        chapter_number = int(request.form.get("chapter_number"))

        if chapter_number < 1:
            return apology("enter a positive number", 400)
        
        chapter_title = request.form.get("chapter_title")

        if not chapter_title:
            return apology("enter a title", 400)
        
        chunk = int(request.form.get("chunk"))
        total_chunks = int(request.form.get("total_chunks"))

        if chunk > total_chunks:
            return apology("the number must be equal to or less than the total chunks", 400)

        if chunk < 1 or total_chunks < 1 or chunk > 13 or total_chunks > 13:
            return apology("a range between 1 and 13 is supported", 400)
        
        duration = request.form.get("duration")       
        year_production = int(request.form.get("year_production"))

        if year_production < 1987 or year_production > 2046:
            return apology("year out of range", 400)

        # url, "mega", "google_drive", path
        location_route = request.form.get("location_route")
        # Radio company, reference website...
        station_name = request.form.get("station_name")

        """
        We prepare the data collected in the text areas before
        we can insert the data into the database 
        """
       
        genre = request.form.get("genre")
        genre = genre.replace(", ", ",")
        genre = genre.split(",")
       
        tag = request.form.get("tag")
        tag = tag.replace(", ", ",")
        tag = tag.split(",")
               
        # Data for the podcast table
        db.execute(
            "INSERT INTO podcast (language, program_name, chapter_number, chapter_title, chunk, total_chunks, duration, year_production, username_id, was_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            language.lower(),
            program_name,
            chapter_number,
            chapter_title.capitalize(),
            chunk,
            total_chunks,
            duration,
            year_production,
            manager_id,
            utc_time()
        )

        # Data for the locations table
        location_id = db.execute(
            "INSERT INTO locations (location_route) VALUES (?)", location_route
        )

        # Get podcast_id because it is needed in next steps
        podcast_id = db.execute(
            "SELECT id FROM podcast ORDER BY id DESC LIMIT 1"
        )
       
        podcast_id = podcast_id[0]["id"]
       
        # Data for podcast_locations table
        db.execute(
            "INSERT INTO podcast_locations (podcast_id, location_id) VALUES (?, ?)",
            podcast_id,
            location_id
        )

        # We check which stations we have in the database
        stations_included = db.execute(                
            "SELECT station_name FROM stations"
        )

        # Check if the station that we want to include exists or not in the database
        exist = False
        for dic in stations_included:
            for val in dic.values():
                if val == station_name:
                    exist = True
                    break

        if exist:
            station_id = db.execute(
                "SELECT station_id FROM stations WHERE station_name = ?", station_name
            )

            station_id = station_id[0]["station_id"]

            db.execute(
                "INSERT INTO podcast_stations (podcast_id, station_id) VALUES (?, ?)",
                podcast_id,
                station_id
            )

        else:
            db.execute(
                "INSERT INTO stations (station_name) VALUES (?)", station_name
            )

            station_id = db.execute(
                "SELECT station_id FROM stations WHERE station_name = ?", station_name
            )

            station_id = station_id[0]["station_id"]

            db.execute(
                "INSERT INTO podcast_stations (podcast_id, station_id) VALUES (?, ?)",
                podcast_id,
                station_id
            )

        # Genres insertion
        for g in genre:

            genres_included = db.execute(                
                "SELECT genre_name FROM genres"
                )
            
            # Check if it already exists or not
            exist = False
            for dic in genres_included:
                for val in dic.values():
                    if val == g:
                        exist = True
                        break

            if exist:
                genre_id = db.execute(
                    "SELECT genre_id FROM genres WHERE genre_name = ?", g
                )

                genre_id = genre_id[0]["genre_id"]

                db.execute(
                    "INSERT INTO podcast_genres (podcast_id, genre_id) VALUES (?, ?)",
                    podcast_id,
                    genre_id
                )

            # In case it was a new item
            else:
                db.execute(
                    "INSERT INTO genres (genre_name) VALUES (?)", g
                )

                genre_id = db.execute(
                    "SELECT genre_id FROM genres WHERE genre_name = ?", g
                )

                genre_id = genre_id[0]["genre_id"]

                db.execute(
                    "INSERT INTO podcast_genres (podcast_id, genre_id) VALUES (?, ?)",
                    podcast_id,
                    genre_id
                )

        # Tags insertion
        for t in tag:

            tags_included = db.execute (
                "SELECT tag_name FROM tags"
            )

            # Check if it already exists or not
            exist = False
            for dic in tags_included:
                for val in dic.values():
                    if val == t:
                        exist = True
                        break

            if exist:
                tag_id = db.execute(
                    "SELECT tag_id FROM tags WHERE tag_name = ?", t
                )

                tag_id = tag_id[0]["tag_id"]

                db.execute(
                    "INSERT INTO podcast_tags (podcast_id, tag_id) VALUES (?, ?)",
                    podcast_id,
                    tag_id
                )
            
            # In case it was a new item
            else:
                db.execute(
                    "INSERT INTO tags (tag_name) VALUES (?)", t
                )

                tag_id = db.execute(
                    "SELECT tag_id FROM tags WHERE tag_name = ?", t
                )

                tag_id = tag_id[0]["tag_id"]

                db.execute(
                    "INSERT INTO podcast_tags (podcast_id, tag_id) VALUES (?, ?)",
                    podcast_id,
                    tag_id
                )

        # Confirm insertion
        flash("Congratulations, added successfully!")

        return redirect("/")

    else:
        return render_template("insert.html", language_list=language_list)
    

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search the database"""
    # Get user id
    manager_id = session["user_id"]
   
    if request.method == "POST":
        # What the user is looking for 
        program_name = request.form.get("program_name")
        chapter_title = request.form.get("chapter_title")
        genre_name = request.form.get("genre_name")
        tag_name = request.form.get("tag_name")

        # Search by program name
        if program_name:

            results = db.execute(
               "SELECT locations.location_route, podcast.id, podcast.program_name, podcast.chapter_number, podcast.chapter_title, podcast.chunk, podcast.total_chunks FROM podcast JOIN users ON users.id=podcast.username_id JOIN podcast_locations ON podcast_locations.podcast_id=podcast.id JOIN locations ON locations.location_id=podcast_locations.location_id WHERE users.id = ? AND podcast.program_name LIKE ?",
                manager_id,
                "%" + program_name + "%"                
                )   

            if len(results) != 0:

                # Get genre and tags               
                for row in results:

                    genre_list = db.execute(
                        "SELECT genre_name FROM genres JOIN podcast_genres ON genres.genre_id = podcast_genres.genre_id JOIN podcast ON podcast_genres.podcast_id = podcast.id WHERE username_id = ? AND program_name LIKE ? and podcast.id = ?",
                        manager_id,
                        "%" + program_name + "%",
                        row["id"]
                    )

                    tag_list = db.execute(
                        "SELECT tag_name FROM tags JOIN podcast_tags ON tags.tag_id = podcast_tags.tag_id JOIN podcast ON podcast_tags.podcast_id = podcast.id WHERE username_id = ? AND program_name LIKE ? and podcast.id = ?",
                        manager_id,
                        "%" + program_name + "%",
                        row["id"]
                    ) 

                    # Now you can add the genres and tags that correspond to each particular podcast id
                    row["genre_list"] = genre_list
                    row["tag_list"] = tag_list

                return render_template("results.html",
                    results=results,
                )            

            else:
                # Not found
                flash("Not found!")
                return redirect("/search")
                
        # Search by chapter title
        if chapter_title:

            results = db.execute(
               "SELECT locations.location_route, podcast.id, podcast.program_name, podcast.chapter_number, podcast.chapter_title, podcast.chunk, podcast.total_chunks FROM podcast JOIN users ON users.id=podcast.username_id JOIN podcast_locations ON podcast_locations.podcast_id=podcast.id JOIN locations ON locations.location_id=podcast_locations.location_id WHERE users.id = ? AND podcast.chapter_title LIKE ?",
                manager_id,
                "%" + chapter_title + "%"                
                )   

            if len(results) != 0:

                # Get genre and tags               
                for row in results:
                    genre_list = db.execute(
                        "SELECT genre_name FROM genres JOIN podcast_genres ON genres.genre_id = podcast_genres.genre_id JOIN podcast ON podcast_genres.podcast_id = podcast.id WHERE username_id = ? AND chapter_title LIKE ? and podcast.id = ?",
                        manager_id,
                        "%" + chapter_title + "%",
                        row["id"]
                    )

                    tag_list = db.execute(
                        "SELECT tag_name FROM tags JOIN podcast_tags ON tags.tag_id = podcast_tags.tag_id JOIN podcast ON podcast_tags.podcast_id = podcast.id WHERE username_id = ? AND chapter_title LIKE ? and podcast.id = ?",
                        manager_id,
                        "%" + chapter_title + "%",
                        row["id"]
                    ) 

                    # Now you can add the genres and tags that correspond to each particular podcast id
                    row["genre_list"] = genre_list
                    row["tag_list"] = tag_list

                return render_template("results.html",
                    results=results,
                )            

            else:
                # Not found
                flash("Not found!")
                return redirect("/search")
      
        # Search by genre
        if genre_name:

            results = db.execute(
                "SELECT locations.location_route, podcast.id, podcast.program_name, podcast.chapter_number, podcast.chapter_title, podcast.chunk, podcast.total_chunks FROM genres JOIN podcast_genres ON podcast_genres.genre_id=genres.genre_id JOIN podcast ON podcast.id=podcast_genres.podcast_id JOIN users ON users.id=podcast.username_id JOIN podcast_locations ON podcast_locations.podcast_id=podcast.id JOIN locations ON locations.location_id=podcast_locations.location_id WHERE users.id = ? AND genres.genre_name LIKE ?",
                manager_id,
                "%" + genre_name + "%"
            )        

            if len(results) != 0:

                # Get genre and tags               
                for row in results:
                    genre_list = db.execute(                        
                        "SELECT genre_name FROM genres JOIN podcast_genres ON genres.genre_id = podcast_genres.genre_id JOIN podcast ON podcast_genres.podcast_id = podcast.id WHERE username_id = ? AND podcast.id = ?",
                        manager_id,
                        row["id"]
                    )

                    tag_list = db.execute(
                        "SELECT DISTINCT tag_name FROM tags JOIN podcast_tags ON tags.tag_id=podcast_tags.tag_id JOIN podcast ON podcast_tags.podcast_id=podcast.id WHERE username_id = ? and podcast.id = ?",
                        manager_id,
                        row["id"]
                    ) 

                    # Now you can add the genres and tags that correspond to each particular podcast id
                    row["genre_list"] = genre_list
                    row["tag_list"] = tag_list

                return render_template("results.html",
                    results=results,
                )            

            else:
                # Not found
                flash("Not found!")
                return redirect("/search")
           
        # Search by tag
        if tag_name:
             
            results = db.execute(
                "SELECT locations.location_route, podcast.id, podcast.program_name, podcast.chapter_number, podcast.chapter_title, podcast.chunk, podcast.total_chunks FROM tags JOIN podcast_tags ON podcast_tags.tag_id=tags.tag_id JOIN podcast ON podcast.id=podcast_tags.podcast_id JOIN users ON users.id=podcast.username_id JOIN podcast_locations ON podcast_locations.podcast_id=podcast.id JOIN locations ON locations.location_id=podcast_locations.location_id WHERE users.id = ? AND tags.tag_name LIKE ?",
                manager_id,
                "%" + tag_name + "%"
            )

            if len(results) != 0:

                # Get genre and tags
                for row in results:
                    genre_list = db.execute(                        
                        "SELECT genre_name FROM genres JOIN podcast_genres ON genres.genre_id = podcast_genres.genre_id JOIN podcast ON podcast_genres.podcast_id = podcast.id WHERE username_id = ? AND podcast.id = ?",
                        manager_id,
                        row["id"]
                    )

                    tag_list = db.execute(
                        "SELECT DISTINCT tag_name FROM tags JOIN podcast_tags ON tags.tag_id=podcast_tags.tag_id JOIN podcast ON podcast_tags.podcast_id=podcast.id WHERE username_id = ? and podcast.id = ?",
                        manager_id,
                        row["id"]
                    ) 

                    # Now you can add the genres and tags that correspond to each particular podcast id
                    row["genre_list"] = genre_list
                    row["tag_list"] = tag_list

                return render_template("results.html",
                    results=results,
                )            

            else:
                # Not found
                flash("Not found!")
                return redirect("/search")             
        
        else:
            return apology("You have to fill in one of the fields", 400)

    else:
        return render_template("/search.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Confirm user login
        flash("You were successfully logged in")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not confirmation:
            return apology("must provide confirmation", 400)

        # Ensure password and confirmation are equal
        elif password != confirmation:
            return apology("The password and confirmation are different.", 400)

        # Ensure username doesn't already exist
        rows = db.execute("SELECT username FROM users WHERE username = ?", username)

        if len(rows) != 0:
            return apology("That username already exists", 400)

        else:
            hash = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash
            )
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    """Change user password"""
    # User reached route via POST (as by submitting a form via POST)
    manager_id = session["user_id"]

    # Query database for current password
    rows = db.execute("SELECT * FROM users WHERE id = ?", manager_id)

    if request.method == "POST":
        password = request.form.get("password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Ensure current password was submitted
        if not password:
            return apology("must provide current password", 400)

        # Ensure current password is correct
        elif not check_password_hash(rows[0]["hash"], password):
            return apology("invalid password", 400)

        # Ensure new password was submitted
        elif not new_password:
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not confirmation:
            return apology("must provide confirmation", 400)

        # Ensure new password and confirmation are equal
        elif new_password != confirmation:
            return apology("The password and confirmation are different.", 400)

        # Ensure password and new password are distinct
        elif new_password == password:
            return apology("You just repeated the current password, change it", 400)

        else:
            hash = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, manager_id)

            # Confirm password
            flash("Password changed successfully.")

            return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change.html")


@app.route("/favorites")
def favorites():
    """If you're still hungry for podcast"""
    return render_template("favorites.html")