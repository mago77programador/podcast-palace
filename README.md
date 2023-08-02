# PodcastPalace
#### Video Demo:  <https://youtu.be/nl4Xo-sTiXY>
#### Description:
Final project of the course: "CS50’s Introduction to Computer Science".

PodcastPalace is a web application developed using JavaScript, Python, Flask, and SQL.

The following functionalities have been added to the app:

- Register: The first step is to create a user. It checks that the entered user does not already exist.
- Login: The app allows multiple users, so that each person can have their own catalog of podcasts.
- Insert: The user creates his own podcast catalog. Therefore, in addition to the name of the program, chapter, duration, audio path and genre the user can use his own keywords: names, places, battles, books, movies, series, museums mentioned in the audios.
- Search: Search the database using various criteria (program name, chapter title, genre, tag)
- Results: Search results are provided with the ability to listen to the podcast..
- Favorites: User can find sites with more content to listen.
- Change: Change user password.

One of my greatest passions is listening to podcasts, especially those that delve into historical topics, and I love collecting intriguing audio content.

Some time ago, I came up with the idea of keeping a "journal" of these podcasts: noting the themes they covered, the historical figures who starred in the shows, the movies, books, or series mentioned, as well as the places and cities highlighted. For this purpose, I used to use a spreadsheet. So, I thought it would be a fantastic opportunity to incorporate this idea into my final project for the course.

For the sake of the argument, in the static/audio/ path there are three .mp3 files that you can listen to directly from the app by using the search function.

The backend server Flask was created fully in Python. It is a framework made up of Python modules and packages. With its characteristics, it is a lightweight Flask application that speeds up the development of backend apps.

To run the app, from the main folder:

```bash
flask –app <hello> run
flask run
python <app_name>.py
```
More in https://flask.palletsprojects.com/en/2.3.x/quickstart/#a-minimal-application

Sqlite3 database:

```bash
sqlite3 test.db
>> .read create_tables.sql
```

If you decide to clone the repository, there is already a database where you can perform tests. The user created in the app is "feo" and the password is "123" (write it down somewhere, it's easy to forget).

But...? Where is everybody?

![They have left me alone.](travoltadesierto.gif)
