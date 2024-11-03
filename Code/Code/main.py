import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import random

# Connect to SQLite database
conn = sqlite3.connect("film_booking.db")
cursor = conn.cursor()

# Main Page
def main_page():
    root = tk.Tk()
    root.title("Welcome")

    tk.Button(root, text="Login", command=login_gui).pack(side=tk.LEFT, padx=10, pady=10)
    tk.Button(root, text="Register", command=register_gui).pack(side=tk.RIGHT, padx=10, pady=10)

    root.mainloop()

# Register system
def register_gui():
    register_window = tk.Toplevel()
    register_window.title("Register")

    tk.Label(register_window, text="Choose User ID:").grid(row=0, column=0, padx=10, pady=10)
    user_id_entry = tk.Entry(register_window)
    user_id_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(register_window, text="Choose Password:").grid(row=1, column=0, padx=10, pady=10)
    password_entry = tk.Entry(register_window, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Button(register_window, text="Register", command=lambda: attempt_register(user_id_entry.get(), password_entry.get(), register_window)).grid(row=2, columnspan=2, pady=10)

def attempt_register(user_id, password, window):
    if not user_id or not password:
        messagebox.showerror("Registration Failed", "User ID and password cannot be empty.")
        return
    
    try:
        cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        if cursor.fetchone() is not None:
            messagebox.showerror("Registration Failed", f"User ID {user_id} already exists.")
            return

        cursor.execute("INSERT INTO users (user_id, password, role) VALUES (?, ?, ?)", (user_id, password, "customer"))
        conn.commit()
        messagebox.showinfo("Registration Success", "You have successfully registered!")
        window.destroy()
    except sqlite3.IntegrityError:
        messagebox.showerror("Registration Failed", "An integrity error occurred.")
    except Exception as e:
        messagebox.showerror("Registration Failed", f"An error occurred: {str(e)}")

# Login system
def login(user_id, password):
    cursor.execute("SELECT role FROM users WHERE user_id=? AND password=?", (user_id, password))
    result = cursor.fetchone()
    return (result is not None, result[0] if result else "")

# GUI for login
def login_gui():
    login_window = tk.Toplevel()
    login_window.title("Login")

    tk.Label(login_window, text="User ID:").grid(row=0, column=0, padx=10, pady=10)
    user_id_entry = tk.Entry(login_window)
    user_id_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(login_window, text="Password:").grid(row=1, column=0, padx=10, pady=10)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    def attempt_login():
        user_id = user_id_entry.get()
        password = password_entry.get()
        success, user_type = login(user_id, password)
        if success:
            global current_user_id
            current_user_id = user_id  
            login_window.destroy()
            if user_type == "admin":
                admin_gui()
            elif user_type == "manager":
                manager_gui()
            elif user_type == "booking_staff":
                booking_staff_gui()
            else:
                customer_gui()
        else:
            messagebox.showerror("Login Failed", "Invalid user ID or password.")

    tk.Button(login_window, text="Login", command=attempt_login).grid(row=2, column=0, columnspan=2, pady=10)
    
    login_window.mainloop()

# GUI for customer view
def customer_gui():
    customer_window = tk.Toplevel()
    customer_window.title("Customer View")

    BookingTab(customer_window, cursor).pack(fill=tk.BOTH, expand=True)
    CancellationTab(customer_window, cursor).pack(fill=tk.BOTH, expand=True)

# Booking Tab
class BookingTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        ttk.Label(self, text="Film").grid(row=0, column=0, padx=10, pady=5)
        self.film_var = tk.StringVar()
        self.film_menu = ttk.Combobox(self, textvariable=self.film_var)
        self.film_menu.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self, text="Showtime").grid(row=1, column=0, padx=10, pady=5)
        self.showtimes_var = tk.StringVar()
        self.showtimes_menu = ttk.Combobox(self, textvariable=self.showtimes_var)
        self.showtimes_menu.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self, text="Seat Type").grid(row=2, column=0, padx=10, pady=5)
        self.seat_var = tk.StringVar()
        self.seat_menu = ttk.Combobox(self, textvariable=self.seat_var)
        self.seat_menu.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self, text="Cinema").grid(row=3, column=0, padx=10, pady=5)
        self.cinema_var = tk.StringVar()
        self.cinema_menu = ttk.Combobox(self, textvariable=self.cinema_var)
        self.cinema_menu.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self, text="Number of Tickets").grid(row=4, column=0, padx=10, pady=5)
        self.ticket_count_var = tk.IntVar(value=1)
        ttk.Entry(self, textvariable=self.ticket_count_var).grid(row=4, column=1, padx=10, pady=5)

        ttk.Button(self, text="Check Seats", command=self.check_seats).grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        self.booking_result = ttk.Label(self, text="")
        self.booking_result.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

    def load_data(self):
        self.display_films()
        self.display_seats()
        self.display_cinemas()
        self.film_menu.bind("<<ComboboxSelected>>", self.display_showtimes)

    def display_films(self):
        self.cursor.execute("SELECT title FROM films")
        films = [film[0] for film in self.cursor.fetchall()]
        self.film_menu.config(values=films)
        
    def display_cinemas(self):
        self.cursor.execute("SELECT name FROM cinemas")
        cinemas = [cinema[0] for cinema in self.cursor.fetchall()]
        self.cinema_menu.config(values=cinemas)
        
    def display_seats(self):
        self.seat_menu.config(values=["Lower Hall", "Upper Hall", "VIP"])

    def display_showtimes(self, event):
        selected_film = self.film_var.get()
        self.cursor.execute("SELECT showtimes FROM films WHERE title = ?", (selected_film,))
        showtimes = self.cursor.fetchone()
        
        if showtimes:
            showtimes_list = showtimes[0].split(', ')
            self.showtimes_menu.config(values=showtimes_list)

    def check_seats(self):
        selected_film = self.film_var.get()
        selected_seat = self.seat_var.get()
        selected_showtime = self.showtimes_var.get()
        
        if not selected_showtime:
            messagebox.showerror("Booking Failed", "Showtime must be selected.")
            return

        # Seat Price Calculation
        price = {"VIP": 39.99, "Lower Hall": 19.99, "Upper Hall": 9.99}.get(selected_seat, 9.99)
        
        if random.choice([True, False]):
            booking_ref = "MOV" + str(random.randint(100000000000, 999999999999))
            ticket_count = self.ticket_count_var.get()
            booking_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_price = price * ticket_count
            cinema = self.cinema_var.get()

            self.booking_result.config(
                text=f"Booking confirmed!\nReference: {booking_ref}\nFilm: {selected_film}\nShowtime: {selected_showtime}\nTickets: {ticket_count}\nCustomer Name: {current_user_id}\nBooking Date: {booking_date}\nTotal Price: ${total_price:.2f}"
            )

            # Insert booking into the database
            try:
                cursor.execute(
                    "INSERT INTO bookings (film, showtime, ticket_count, booking_reference, booking_date, total_price, cinema, customer_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (selected_film, selected_showtime, ticket_count, booking_ref, booking_date, total_price, cinema, current_user_id)
                )
                conn.commit()
            except Exception as e:
                messagebox.showerror("Booking Failed", f"An error occurred: {str(e)}")
        else:
            self.booking_result.config(text="Seats not available. Please try again later.")

# Cancellation Tab
class CancellationTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        ttk.Label(self, text="Booking Reference").grid(row=0, column=0, padx=10, pady=5)
        self.cancellation_ref = tk.StringVar()
        ttk.Entry(self, textvariable=self.cancellation_ref).grid(row=0, column=1, padx=10, pady=5)

        ttk.Button(self, text="Cancel Booking", command=self.cancel_booking).grid(row=1, column=0, columnspan=2, padx=10, pady=5)

        self.cancellation_result = ttk.Label(self, text="")
        self.cancellation_result.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    def cancel_booking(self):
        ref = self.cancellation_ref.get()

        if not ref:
            messagebox.showerror("Cancellation Failed", "Booking reference cannot be empty.")
            return

        try:
            cursor.execute("DELETE FROM bookings WHERE booking_reference = ?", (ref,))
            conn.commit()

            if cursor.rowcount > 0:
                self.cancellation_result.config(text=f"Booking {ref} has been cancelled.")
            else:
                self.cancellation_result.config(text="Invalid booking reference.")
        except Exception as e:
            messagebox.showerror("Cancellation Failed", f"An error occurred: {str(e)}")

# GUI for admin view
def admin_gui():
    admin_window = tk.Toplevel()
    admin_window.title("Admin View")
    
    # Create the cursor object
    cursor = conn.cursor()

    # Create an instance of the AdminTab class
    admin_tab = AdminTab(admin_window, cursor, conn)
    admin_tab.pack(fill=tk.BOTH, expand=True)

# Admin Tab
class AdminTab(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn
        
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        add_film_tab = AddFilmTab(notebook, cursor, conn)
        film_list_tab = FilmListTab(notebook, cursor)
        edit_film_tab = EditFilmTab(notebook, cursor, conn)
        user_list_tab = UserListTab(notebook, cursor)
        manage_staff_tab = ManageStaffTab(notebook, cursor, conn)
        booking_reports_tab = BookingReportsTab(notebook, cursor)
        revenue_reports_tab = RevenueReports(notebook, cursor)

        notebook.add(add_film_tab, text="Add Film")
        notebook.add(film_list_tab, text="Film List")
        notebook.add(edit_film_tab, text="Edit Film")
        notebook.add(user_list_tab, text="User List")
        notebook.add(manage_staff_tab, text="Manage Staff")
        notebook.add(booking_reports_tab, text="Booking Reports")
        notebook.add(revenue_reports_tab, text="Revenue Reports")

# Add Film Tab
class AddFilmTab(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn
        
        # Fields for managing films
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Film Title").grid(row=0, column=0, padx=10, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.title_var).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self, text="Description").grid(row=1, column=0, padx=10, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.description_var).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self, text="Actors").grid(row=2, column=0, padx=10, pady=5)
        self.actors_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.actors_var).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self, text="Genre").grid(row=3, column=0, padx=10, pady=5)
        self.genre_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.genre_var).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self, text="Age Rating").grid(row=4, column=0, padx=10, pady=5)
        self.age_rating_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.age_rating_var).grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(self, text="Show Times").grid(row=5, column=0, padx=10, pady=5)
        self.showtimes_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.showtimes_var).grid(row=5, column=1, padx=10, pady=5)

        ttk.Button(self, text="Add Film", command=self.add_film).grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        self.add_film_result = ttk.Label(self, text="")
        self.add_film_result.grid(row=7, column=0, columnspan=2, padx=10, pady=5)

    def add_film(self):
        new_film = {
            "title": self.title_var.get(),
            "description": self.description_var.get(),
            "actors": self.actors_var.get(),
            "genre": self.genre_var.get(),
            "age_rating": self.age_rating_var.get(),
            "showtimes": self.showtimes_var.get()
        }

        try:
            self.cursor.execute(
                "INSERT INTO films (title, description, actors, genre, age_rating, showtimes) VALUES (?, ?, ?, ?, ?, ?)",
                (new_film["title"], new_film["description"], new_film["actors"], new_film["genre"], new_film["age_rating"], new_film["showtimes"])
            )
            self.conn.commit()
            self.add_film_result.config(text=f"Film '{new_film['title']}' added successfully.", foreground="green")
        except Exception as e:
            self.add_film_result.config(text=f"Error adding film: {e}", foreground="red")

# Film List Tab
class FilmListTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor
        self.create_widgets()
        self.populate_treeview()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("Title", "Description", "Actors", "Genre", "Age Rating", "Showtimes"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Actors", text="Actors")
        self.tree.heading("Genre", text="Genre")
        self.tree.heading("Age Rating", text="Age Rating")
        self.tree.heading("Showtimes", text="Showtimes")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            self.cursor.execute("SELECT * FROM films")
            films = self.cursor.fetchall()
            for film in films:
                self.tree.insert("", "end", text=film[0], values=(film[1], film[2], film[3], film[4], film[5], film[6]))
        except Exception as e:
            print(f"Error fetching films: {e}")

# Edit Film Tab
class EditFilmTab(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn

        self.create_widgets()

    def create_widgets(self):
        # Components for selecting a film by ID
        ttk.Label(self, text="Enter Film ID to Edit:").grid(row=0, column=0, padx=10, pady=5)
        self.film_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.film_id_var).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self, text="Load Film", command=self.load_film).grid(row=0, column=2, padx=10, pady=5)
        self.edit_film_result = ttk.Label(self, text="")
        self.edit_film_result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Fields for editing film details
        ttk.Label(self, text="Title").grid(row=2, column=0, padx=10, pady=5)
        self.title_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.title_var).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self, text="Description").grid(row=3, column=0, padx=10, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.description_var).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self, text="Actors").grid(row=4, column=0, padx=10, pady=5)
        self.actors_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.actors_var).grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self, text="Genre").grid(row=5, column=0, padx=10, pady=5)
        self.genre_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.genre_var).grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(self, text="Age Rating").grid(row=6, column=0, padx=10, pady=5)
        self.age_rating_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.age_rating_var).grid(row=6, column=1, padx=10, pady=5)

        ttk.Label(self, text="Showtimes").grid(row=7, column=0, padx=10, pady=5)
        self.showtimes_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.showtimes_var).grid(row=7, column=1, padx=10, pady=5)

        ttk.Button(self, text="Update Film", command=self.update_film).grid(row=8, column=0, columnspan=3, padx=10, pady=5)

    def load_film(self):
        film_id = self.film_id_var.get()
        try:
            self.cursor.execute("SELECT * FROM films WHERE id=?", (film_id,))
            film = self.cursor.fetchone()

            if film:
                self.title_var.set(film[1])
                self.description_var.set(film[2])
                self.actors_var.set(film[3])
                self.genre_var.set(film[4])
                self.age_rating_var.set(film[5])
                self.showtimes_var.set(film[6])
                self.edit_film_result.config(text=f"Loaded film ID: {film_id}", foreground="green")
            else:
                self.edit_film_result.config(text="Film ID not found.", foreground="red")
        except Exception as e:
            self.edit_film_result.config(text=f"Error loading film: {e}", foreground="red")

    def update_film(self):
        film_id = self.film_id_var.get()
        updated_film = {
            "title": self.title_var.get(),
            "description": self.description_var.get(),
            "actors": self.actors_var.get(),
            "genre": self.genre_var.get(),
            "age_rating": self.age_rating_var.get(),
            "showtimes": self.showtimes_var.get()
        }

        try:
            self.cursor.execute("""
                UPDATE films
                SET title=?, description=?, actors=?, genre=?, age_rating=?, showtimes=?
                WHERE id=?
            """, (updated_film["title"], updated_film["description"], updated_film["actors"], updated_film["genre"], updated_film["age_rating"], updated_film["showtimes"], film_id))
            self.conn.commit()
            self.edit_film_result.config(text=f"Film ID {film_id} updated successfully.", foreground="green")
        except Exception as e:
            self.edit_film_result.config(text=f"Error updating film: {e}", foreground="red")

# User List Tab
class UserListTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor
        self.create_widgets()
        self.populate_treeview()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("Username", "Email", "Role"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Role", text="Role")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())

        try:
            self.cursor.execute("SELECT * FROM users")
            users = self.cursor.fetchall()
            for user in users:
                self.tree.insert("", "end", text=user[0], values=(user[1], user[2], user[3]))
        except Exception as e:
            print(f"Error fetching users: {e}")

# Manage Staff Tab
class ManageStaffTab(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn

        self.create_widgets()

    def create_widgets(self):
        # Fields for managing staff roles
        ttk.Label(self, text="User ID").grid(row=0, column=0, padx=10, pady=5)
        self.user_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.user_id_var).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self, text="New Role").grid(row=1, column=0, padx=10, pady=5)
        self.role_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.role_var).grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(self, text="Update Role", command=self.update_role).grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        self.update_role_result = ttk.Label(self, text="")
        self.update_role_result.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    def update_role(self):
        user_id = self.user_id_var.get()
        new_role = self.role_var.get()

        try:
            self.cursor.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
            self.conn.commit()
            self.update_role_result.config(text=f"User ID {user_id} role updated to {new_role}.", foreground="green")
        except Exception as e:
            self.update_role_result.config(text=f"Error updating role: {e}", foreground="red")

# Booking Reports Tab
class BookingReportsTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        self.create_widgets()
        self.populate_treeview()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("Film", "Showtime", "Ticket_count", "Booking_refernce", "Booking_date"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Film", text="Film")
        self.tree.heading("Showtime", text="Showtime")
        self.tree.heading("Ticket_count", text="Ticket_count")
        self.tree.heading("Booking_refernce", text="Booking_refernce")
        self.tree.heading("Booking_date", text="Booking_date")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())

        try:
            self.cursor.execute("SELECT * FROM bookings")
            bookings = self.cursor.fetchall()
            for booking in bookings:
                self.tree.insert("", "end", text=booking[0], values=(booking[1], booking[2], booking[3], booking[4], booking[5]))
        except Exception as e:
            print(f"Error fetching bookings: {e}")

#Revenue Reports Tab
class RevenueReports(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        # Set up the treeview for displaying revenue reports
        self.tree = ttk.Treeview(self, columns=("Cinema", "Money Earned"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Cinema", text="Cinema")
        self.tree.heading("Money Earned", text="Money Earned")
        self.tree.grid(row=1, column=0, columnspan=4, sticky="nsew")

        # Set up a scrollbar for the treeview
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=1, column=4, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Set up a dropdown (Combobox) for cinema selection
        ttk.Label(self, text="Cinema").grid(row=0, column=0, padx=10, pady=5)
        self.cinema_var = tk.StringVar()
        self.cinema_menu = ttk.Combobox(self, textvariable=self.cinema_var)
        self.cinema_menu.grid(row=0, column=1, padx=10, pady=5)

        # Load the cinemas into the dropdown
        self.display_cinemas()

        # Bind the Combobox selection event
        self.cinema_menu.bind('<<ComboboxSelected>>', lambda e: self.load_filtered())

        # Generate Report Button
        ttk.Button(self, text="Generate Revenue Report", command=self.generate_report).grid(row=0, column=2, padx=10, pady=5)

    def display_cinemas(self):
        try:
            self.cursor.execute("SELECT name FROM cinemas")
            cinemas = [cinema[0] for cinema in self.cursor.fetchall()]
            self.cinema_menu['values'] = cinemas
        except Exception as e:
            print(f"Error loading cinemas: {e}")

    def load_filtered(self):
        self.tree.delete(*self.tree.get_children())

        selected_cinema = self.cinema_var.get()
        try:
            self.cursor.execute("""
                SELECT cinemas.name, SUM(total_price) AS revenue
                FROM bookings
                JOIN cinemas ON bookings.cinema = cinemas.name
                WHERE cinemas.name = ?
                GROUP BY cinemas.name
            """, (selected_cinema,))
            results = self.cursor.fetchall()
            for result in results:
                self.tree.insert("", "end", text="",
                                 values=(result[0], f"${result[1]:.2f}"))
        except Exception as e:
            print(f"Error loading revenue report: {e}")

    def generate_report(self):
        self.load_filtered()

# Manager GUI - For managing cinemas
def manager_gui():
    manager_window = tk.Toplevel()
    manager_window.title("Manager View")
    
    # Create the cursor object
    cursor = conn.cursor()

    # Create an instance of the ManagerTab class
    manager_tab = ManagerTab(manager_window, cursor, conn)
    manager_tab.pack(fill=tk.BOTH, expand=True)

# Manager Tab - Managing Cinemas
class ManagerTab(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn
        
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        add_cinema_tab = AddCinemaTab(notebook, cursor, conn)
        edit_cinema_tab = EditCinemaTab(notebook, cursor, conn)

        notebook.add(add_cinema_tab, text="Add Cinema")
        notebook.add(edit_cinema_tab, text="Edit Cinema")

# Add Cinema Tab
class AddCinemaTab(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn
        
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Cinema Name").grid(row=0, column=0, padx=10, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self, text="Location").grid(row=1, column=0, padx=10, pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.location_var).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self, text="Total Screens").grid(row=2, column=0, padx=10, pady=5)
        self.screens_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.screens_var).grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(self, text="Add Cinema", command=self.add_cinema).grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.add_cinema_result = ttk.Label(self, text="")
        self.add_cinema_result.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    def add_cinema(self):
        new_cinema = {
            "name": self.name_var.get(),
            "location": self.location_var.get(),
            "screens": self.screens_var.get()
        }

        try:
            self.cursor.execute("INSERT INTO cinemas (name, location, screens) VALUES (?, ?, ?)", 
                                (new_cinema["name"], new_cinema["location"], new_cinema["screens"]))
            self.conn.commit()
            self.add_cinema_result.config(text=f"Cinema '{new_cinema['name']}' added successfully.", foreground="green")
        except Exception as e:
            self.add_cinema_result.config(text=f"Error adding cinema: {e}", foreground="red")

# Edit Cinema Tab
class EditCinemaTab(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn

        self.create_widgets()

    def create_widgets(self):
        # Components for selecting a cinema by ID
        ttk.Label(self, text="Enter Cinema ID to Edit:").grid(row=0, column=0, padx=10, pady=5)
        self.cinema_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.cinema_id_var).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self, text="Load Cinema", command=self.load_cinema).grid(row=0, column=2, padx=10, pady=5)
        self.edit_cinema_result = ttk.Label(self, text="")
        self.edit_cinema_result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Fields for editing cinema details
        ttk.Label(self, text="Name").grid(row=2, column=0, padx=10, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self, text="Location").grid(row=3, column=0, padx=10, pady=5)
        self.location_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.location_var).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self, text="Total Screens").grid(row=4, column=0, padx=10, pady=5)
        self.screens_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.screens_var).grid(row=4, column=1, padx=10, pady=5)

        ttk.Button(self, text="Update Cinema", command=self.update_cinema).grid(row=5, column=0, columnspan=3, padx=10, pady=5)

    def load_cinema(self):
        cinema_id = self.cinema_id_var.get()
        try:
            self.cursor.execute("SELECT * FROM cinemas WHERE id=?", (cinema_id,))
            cinema = self.cursor.fetchone()

            if cinema:
                self.name_var.set(cinema[1])
                self.location_var.set(cinema[2])
                self.screens_var.set(cinema[3])
                self.edit_cinema_result.config(text=f"Loaded cinema ID: {cinema_id}", foreground="green")
            else:
                self.edit_cinema_result.config(text="Cinema ID not found.", foreground="red")
        except Exception as e:
            self.edit_cinema_result.config(text=f"Error loading cinema: {e}", foreground="red")

    def update_cinema(self):
        cinema_id = self.cinema_id_var.get()
        updated_cinema = {
            "name": self.name_var.get(),
            "location": self.location_var.get(),
            "screens": self.screens_var.get()
        }

        try:
            self.cursor.execute("""
                UPDATE cinemas
                SET name=?, location=?, screens=?
                WHERE id=?
            """, (updated_cinema["name"], updated_cinema["location"], updated_cinema["screens"], cinema_id))
            self.conn.commit()
            self.edit_cinema_result.config(text=f"Cinema ID {cinema_id} updated successfully.", foreground="green")
        except Exception as e:
            self.edit_cinema_result.config(text=f"Error updating cinema: {e}", foreground="red")

# GUI for Booking Staff View
def booking_staff_gui():
    bookings_window = tk.Toplevel()
    bookings_window.title("Booking Staff View")

    # Create the cursor object
    cursor = conn.cursor()

    # Create an instance of the Booking_Staff_Tab class
    bookings_tab = Booking_Staff_Tab(bookings_window, cursor)
    bookings_tab.pack(fill=tk.BOTH, expand=True)

# Booking Staff Tab
class Booking_Staff_Tab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        # Create a search bar for bookings
        ttk.Label(self, text="Search Booking ID:").grid(row=0, column=0, padx=10, pady=5)
        self.booking_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.booking_id_var).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self, text="Search", command=self.search_booking).grid(row=0, column=2, padx=10, pady=5)

        # Create a Treeview to display booking details
        self.tree = ttk.Treeview(self, columns=("Booking ID", "User ID", "Film ID", "Showtime", "Price", "Status"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Booking ID", text="Booking ID")
        self.tree.heading("User ID", text="User ID")
        self.tree.heading("Film ID", text="Film ID")
        self.tree.heading("Showtime", text="Showtime")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Status", text="Status")
        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=1, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Add a label to display search results
        self.search_result_label = ttk.Label(self, text="")
        self.search_result_label.grid(row=2, column=0, columnspan=4, padx=10, pady=5)

        self.populate_treeview()  # Initial population of the Treeview

    def search_booking(self):
        booking_id = self.booking_id_var.get().strip()
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            if booking_id:
                self.cursor.execute("SELECT * FROM booking_report WHERE booking_id = ?", (booking_id,))
            else:
                self.cursor.execute("SELECT * FROM booking_report")
            bookings = self.cursor.fetchall()
            if bookings:
                for booking in bookings:
                    self.tree.insert("", "end", text=booking[0], values=(booking[1], booking[2], booking[3], booking[4], booking[5], booking[6]))
                self.search_result_label.config(text=f"{len(bookings)} booking(s) found.")
            else:
                self.search_result_label.config(text="No bookings found.")
        except Exception as e:
            self.search_result_label.config(text=f"Error searching bookings: {e}")

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            self.cursor.execute("SELECT * FROM booking_report")
            bookings = self.cursor.fetchall()
            for booking in bookings:
                self.tree.insert("", "end", text=booking[0], values=(booking[1], booking[2], booking[3], booking[4], booking[5], booking[6]))
        except Exception as e:
            print(f"Error loading bookings: {e}")

# Admin Tab
class Booking_Staff_Tab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor
        
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        # Create tabs
        bookings_list_tab = BookingsTab(notebook, cursor)
        approve_booking_tab = ManageBookings(notebook, cursor, conn)
        
        # Add tabs to notebook
        notebook.add(bookings_list_tab, text="Bookings List")
        notebook.add(approve_booking_tab, text="Approve/Reject Bookings")

class BookingsTab(ttk.Frame):
    def __init__(self, parent, cursor):
        super().__init__(parent)
        self.cursor = cursor

        # Treeview to display bookings
        self.tree = ttk.Treeview(self, columns=("Film", "Showtime", "Tickets", "Booking Reference Number", "Date", "Total Price", "Cinema", "Username"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Film", text="Film")
        self.tree.heading("Showtime", text="Showtime")
        self.tree.heading("Tickets", text="Tickets")
        self.tree.heading("Booking Reference Number", text="Booking Reference Number")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Total Price", text="Total Price")
        self.tree.heading("Cinema", text="Cinema")
        self.tree.heading("Username", text="Username")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar for Treeview
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.populate_treeview()

    def populate_treeview(self):
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        try:
            self.cursor.execute("SELECT * FROM bookings")
            bookings = self.cursor.fetchall()
            for booking in bookings:
                self.tree.insert("", "end", text=booking[0], values=(booking[1], booking[2], booking[3], booking[4], booking[5], booking[6], booking[7], booking[8]))
        except Exception as e:
            print(f"Error fetching bookings: {e}")

class ManageBookings(ttk.Frame):
    def __init__(self, parent, cursor, conn):
        super().__init__(parent)
        self.cursor = cursor
        self.conn = conn

        # Components for selecting and managing bookings
        ttk.Label(self, text="Enter Booking ID to Edit:").grid(row=0, column=0, padx=10, pady=5)
        self.booking_id_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.booking_id_var).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self, text="Load Booking", command=self.load_booking).grid(row=0, column=2, padx=10, pady=5)
        self.edit_booking_result = ttk.Label(self, text="")
        self.edit_booking_result.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Fields for editing booking details
        self.create_form_fields()

        # Buttons for approving and rejecting bookings
        ttk.Button(self, text="Approve Booking", command=self.approve_booking).grid(row=10, column=0, columnspan=3, padx=10, pady=5)
        ttk.Button(self, text="Reject Booking", command=self.reject_booking).grid(row=11, column=0, columnspan=3, padx=10, pady=5)

    def create_form_fields(self):
        fields = [
            ("Film", "film_var"),
            ("Showtime", "showtime_var"),
            ("Tickets", "tickets_var"),
            ("Booking Reference Number", "ref_var"),
            ("Date", "date_var"),
            ("Total Price", "total_var"),
            ("Cinema", "cinema_var"),
            ("Username", "username_var")
        ]
        
        for index, (label, var_name) in enumerate(fields):
            ttk.Label(self, text=label).grid(row=index + 2, column=0, padx=10, pady=5)
            setattr(self, var_name, tk.StringVar())
            ttk.Entry(self, textvariable=getattr(self, var_name), width=50).grid(row=index + 2, column=1, padx=10, pady=5)

        # Status variable
        self.status_var = tk.StringVar()

    def load_booking(self):
        booking_id = self.booking_id_var.get()
        try:
            self.cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
            booking = self.cursor.fetchone()
            if booking:
                # Populate form fields with booking details
                self.populate_form_fields(booking)
                self.status_var.set("approved")
                self.edit_booking_result.config(text=f"Loaded Booking ID '{booking_id}'")
            else:
                self.edit_booking_result.config(text="No Booking found with that ID.")
        except Exception as e:
            self.edit_booking_result.config(text=f"Error loading Booking: {e}")

    def populate_form_fields(self, booking):
        fields = [
            ("film_var", booking[1]),
            ("showtime_var", booking[2]),
            ("tickets_var", booking[3]),
            ("ref_var", booking[4]),
            ("date_var", booking[5]),
            ("total_var", booking[6]),
            ("cinema_var", booking[7]),
            ("username_var", booking[8])
        ]
        for var_name, value in fields:
            getattr(self, var_name).set(value)

    def approve_booking(self):
        self.update_booking_status("approved")

    def reject_booking(self):
        self.update_booking_status("rejected")

    def update_booking_status(self, status):
        booking_id = self.booking_id_var.get()
        fields = [
            ("film_var", "film"),
            ("showtime_var", "showtime"),
            ("tickets_var", "tickets"),
            ("ref_var", "booking_reference"),
            ("date_var", "booking_date"),
            ("total_var", "total_price"),
            ("cinema_var", "cinema"),
            ("username_var", "customer_name")
        ]
        
        values = [getattr(self, var_name).get() for var_name, _ in fields]

        try:
            self.cursor.execute(
                "INSERT INTO booking_report (film, showtime, tickets, booking_reference, booking_date, total_price, cinema, customer_name, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (*values, status)
            )
            self.conn.commit()
            self.edit_booking_result.config(text=f"Booking ID '{booking_id}' has been {status}.")
        except Exception as e:
            self.edit_booking_result.config(text=f"Error updating booking: {e}")

# Main function to start the application
if __name__ == "__main__":
    main_page()

def main():
    login_gui()


