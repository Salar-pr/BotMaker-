import mysql.connector
import tkinter as tk
import sqlite3

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    # database = "mydatabase"
)


mycursor = mydb.cursor()


class PhonebookApp:
    def init(self, root):
        self.root = root
        self.root.title("Phonebook App")

        # Create and connect to the SQLite database
        self.conn = sqlite3.connect("phonebook.db")
        self.cursor = self.conn.cursor()

        # Create the phonebook table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS phonebook (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                phone_number TEXT,
                email TEXT,
                photo BLOB
            )
        """)
        self.conn.commit()

        # Create widgets
        self.first_name_label = tk.Label(root, text="First Name:")
        self.first_name_entry = tk.Entry(root)
        self.last_name_label = tk.Label(root, text="Last Name:")
        self.last_name_entry = tk.Entry(root)
        self.phone_number_label = tk.Label(root, text="Phone Number:")
        self.phone_number_entry = tk.Entry(root)
        self.email_label = tk.Label(root, text="Email:")
        self.email_entry = tk.Entry(root)
        self.photo_label = tk.Label(root, text="Photo (optional):")
        self.photo_button = tk.Button(root, text="Upload Photo", command=self.upload_photo)
        self.save_button = tk.Button(root, text="Save", command=self.save_contact)

        # Grid layout
        self.first_name_label.grid(row=0, column=0)
        self.first_name_entry.grid(row=0, column=1)
        self.last_name_label.grid(row=1, column=0)
        self.last_name_entry.grid(row=1, column=1)
        self.phone_number_label.grid(row=2, column=0)
        self.phone_number_entry.grid(row=2, column=1)
        self.email_label.grid(row=3, column=0)
        self.email_entry.grid(row=3, column=1)
        self.photo_label.grid(row=4, column=0)
        self.photo_button.grid(row=4, column=1)
        self.save_button.grid(row=5, columnspan=2)

    def upload_photo(self):
        # Implement photo upload logic here
        pass

    def save_contact(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        phone_number = self.phone_number_entry.get()
        email = self.email_entry.get()
        # Get photo data (if uploaded)

        # Insert data into the database
        self.cursor.execute("""
            INSERT INTO phonebook (first_name, last_name, phone_number, email, photo)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, phone_number, email, None))  # Replace None with actual photo data
        self.conn.commit()

        # Clear entry fields
        self.first_name_entry.delete(0, tk.END)
        self.last_name_entry.delete(0, tk.END)
        self.phone_number_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
if __name__ == 'main':
    root = tk.Tk()
    app =  PhonebookApp(root)
    root.mainloop()