CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  username TEXT NOT NULL,
  hash TEXT NOT NULL
);

CREATE UNIQUE INDEX username ON users (username);

CREATE TABLE podcast (
  id INTEGER PRIMARY KEY,
  language TEXT NOT NULL,
  program_name TEXT NOT NULL,
  chapter_number INTEGER,
  chapter_title TEXT NOT NULL,
  chunk INTEGER NOT NULL,
  total_chunks INTEGER NOT NULL,
  duration TEXT NOT NULL,
  year_production INTEGER,
  username_id INTEGER NOT NULL,
  was_added TEXT NOT NULL,
  FOREIGN KEY (username_id) REFERENCES users (id) 
);

CREATE TABLE podcast_genres (
  podcast_id INTEGER NOT NULL,
  genre_id INTEGER NOT NULL,
  FOREIGN KEY(podcast_id) REFERENCES podcast(id),
  FOREIGN KEY(genre_id) REFERENCES genres(genre_id)
);

CREATE TABLE genres (
  genre_id INTEGER PRIMARY KEY,
  genre_name TEXT NOT NULL
);

CREATE TABLE podcast_tags (
  podcast_id INTEGER NOT NULL,
  tag_id TEXT NOT NULL,
  FOREIGN KEY(podcast_id) REFERENCES podcast(id),
  FOREIGN KEY(tag_id) REFERENCES tags(tag_id)
);

CREATE TABLE tags (
  tag_id INTEGER PRIMARY KEY,
  tag_name TEXT NOT NULL
);

CREATE TABLE podcast_stations (
  podcast_id INTEGER NOT NULL,
  station_id TEXT NOT NULL,
  FOREIGN KEY(podcast_id) REFERENCES podcast(id),
  FOREIGN KEY(station_id) REFERENCES stations(station_id)
);

CREATE TABLE stations (
  station_id INTEGER PRIMARY KEY,
  station_name TEXT NOT NULL
);

CREATE TABLE podcast_locations (
  podcast_id INTEGER NOT NULL,
  location_id TEXT NOT NULL,
  FOREIGN KEY(podcast_id) REFERENCES podcast(id),
  FOREIGN KEY(location_id) REFERENCES locations(location_id)
);

CREATE TABLE locations (
  location_id INTEGER PRIMARY KEY,
  location_route TEXT NOT NULL
);
