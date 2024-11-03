import sqlite3

# Connect to (or create) the SQLite database
conn = sqlite3.connect("film_booking.db")
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

cursor.execute("""
CREATE TABLE IF NOT EXISTS films (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    actors TEXT,
    genre TEXT,
    age_rating TEXT,
    showtimes TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS booking_report (
    id INTEGER PRIMARY KEY,
    film TEXT,
    showtime TEXT,
    tickets INTEGER,
    booking_reference TEXT,
    booking_date TEXT,
    total_price INTEGER,
    cinema TEXT,
    customer_name TEXT,
    status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY,
    film TEXT,
    showtime TEXT,
    ticket_count INTEGER,
    booking_reference TEXT,
    booking_date TEXT,
    total_price INTEGER,
    cinema TEXT,
    customer_name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cinemas (
    id INTEGER PRIMARY KEY,
    name TEXT,
    location TEXT,
    screens INTEGER
)
""")

# Insert sample data into users table
cursor.executemany('''
INSERT INTO users (user_id, password, role) VALUES (?, ?, ?)
''', [
    ('nahil', '1', 'admin'),
    ('ahsan', '1', 'manager'),
    ('faiz', '1', 'booking_staff'),
    ('user1', '1', 'user'),
    ('user2', '1', 'user')
])

# Insert sample data into films table
cursor.executemany('''
INSERT INTO films (title, description, actors, genre, age_rating, showtimes) VALUES (?, ?, ?, ?, ?, ?)
''', [
    ('Inception', 'A thief who enters the dreams of others to steal secrets from their subconscious is given a chance to have his criminal history erased as payment for implanting an idea into the mind of a CEO.', 'Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page', 'Science Fiction', 'PG-13', '2024-08-25 20:00'),
    ('The Matrix', 'A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.', 'Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss', 'Action', 'R', '2024-08-26 18:00'),
    ('Interstellar', 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.', 'Matthew McConaughey, Anne Hathaway, Jessica Chastain', 'Science Fiction', 'PG-13', '2024-08-27 21:00')
])

# Insert sample data into cinemas table
cursor.executemany('''
INSERT INTO cinemas (name, location, screens) VALUES (?, ?, ?)
''', [
    ('Cinema City', 'Downtown', 5),
    ('Starplex Cinema', 'Uptown', 7),
    ('Galaxy Theatres', 'Midtown', 10)
])

# Insert sample data into bookings table
cursor.executemany('''
INSERT INTO bookings (film, showtime, ticket_count, booking_reference, booking_date, total_price, cinema, customer_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', [
    ('Inception', '2024-08-25 20:00', 2, 'BR12345', '2024-08-24', 30, 'Cinema City', 'user1'),
    ('The Matrix', '2024-08-26 18:00', 4, 'BR12346', '2024-08-24', 60, 'Starplex Cinema', 'user2')
])

# Insert sample data into booking_report table
cursor.executemany('''
INSERT INTO booking_report (film, showtime, tickets, booking_reference, booking_date, total_price, cinema, customer_name, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', [
    ('Inception', '2024-08-25 20:00', 2, 'BR12345', '2024-08-24', 30, 'Cinema City', 'user1', 'Confirmed'),
    ('The Matrix', '2024-08-26 18:00', 4, 'BR12346', '2024-08-24', 60, 'Starplex Cinema', 'user2', 'Pending')
])

# Commit and close the connection
conn.commit()
conn.close()

print("Database setup and sample data insertion completed successfully.")


