import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# ---------------- DATABASE ----------------
def connect_db():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            quantity INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issued_books (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            student_name TEXT
        )
    """)

    cursor.execute("SELECT * FROM users")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users VALUES ('admin', 'admin')")

    conn.commit()
    conn.close()

# ---------------- ADD BOOK ----------------
def add_book():
    win = tk.Toplevel()
    win.title("Add Book")
    win.geometry("300x300")

    tk.Label(win, text="Book Title").pack(pady=5)
    title_entry = tk.Entry(win)
    title_entry.pack()

    tk.Label(win, text="Author").pack(pady=5)
    author_entry = tk.Entry(win)
    author_entry.pack()

    tk.Label(win, text="Quantity").pack(pady=5)
    qty_entry = tk.Entry(win)
    qty_entry.pack()

    def save():
        title = title_entry.get()
        author = author_entry.get()
        qty = qty_entry.get()

        if title == "" or author == "" or qty == "":
            messagebox.showerror("Error", "All fields required")
            return

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)",
            (title, author, qty)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Book Added")
        win.destroy()

    tk.Button(win, text="Add Book", command=save).pack(pady=20)

# ---------------- VIEW BOOKS (TABLE) ----------------
def view_books():
    win = tk.Toplevel()
    win.title("View Books")
    win.geometry("650x350")

    columns = ("ID", "Title", "Author", "Quantity")
    table = ttk.Treeview(win, columns=columns, show="headings")
    table.pack(fill=tk.BOTH, expand=True)

    table.heading("ID", text="Book ID")
    table.heading("Title", text="Title")
    table.heading("Author", text="Author")
    table.heading("Quantity", text="Quantity")

    table.column("ID", width=80)
    table.column("Title", width=250)
    table.column("Author", width=200)
    table.column("Quantity", width=100)

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        table.insert("", tk.END, values=row)

# ---------------- ISSUE BOOK ----------------
def issue_book():
    win = tk.Toplevel()
    win.title("Issue Book")
    win.geometry("300x250")

    tk.Label(win, text="Book ID").pack(pady=5)
    book_entry = tk.Entry(win)
    book_entry.pack()

    tk.Label(win, text="Student Name").pack(pady=5)
    student_entry = tk.Entry(win)
    student_entry.pack()

    def issue():
        book_id = book_entry.get()
        student = student_entry.get()

        if book_id == "" or student == "":
            messagebox.showerror("Error", "All fields required")
            return

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        cursor.execute("SELECT quantity FROM books WHERE book_id=?", (book_id,))
        result = cursor.fetchone()

        if result is None:
            messagebox.showerror("Error", "Book not found")
            conn.close()
            return

        if result[0] <= 0:
            messagebox.showerror("Error", "Book not available")
            conn.close()
            return

        cursor.execute(
            "INSERT INTO issued_books (book_id, student_name) VALUES (?, ?)",
            (book_id, student)
        )
        cursor.execute(
            "UPDATE books SET quantity = quantity - 1 WHERE book_id=?",
            (book_id,)
        )

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Book Issued")
        win.destroy()

    tk.Button(win, text="Issue Book", command=issue).pack(pady=20)

# ---------------- RETURN BOOK ----------------
def return_book():
    win = tk.Toplevel()
    win.title("Return Book")
    win.geometry("300x250")

    tk.Label(win, text="Book ID").pack(pady=5)
    book_entry = tk.Entry(win)
    book_entry.pack()

    tk.Label(win, text="Student Name").pack(pady=5)
    student_entry = tk.Entry(win)
    student_entry.pack()

    def ret():
        book_id = book_entry.get()
        student = student_entry.get()

        conn = sqlite3.connect("library.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM issued_books WHERE book_id=? AND student_name=?",
            (book_id, student)
        )
        record = cursor.fetchone()

        if record is None:
            messagebox.showerror("Error", "No record found")
            conn.close()
            return

        cursor.execute("DELETE FROM issued_books WHERE issue_id=?", (record[0],))
        cursor.execute(
            "UPDATE books SET quantity = quantity + 1 WHERE book_id=?",
            (book_id,)
        )

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Book Returned")
        win.destroy()

    tk.Button(win, text="Return Book", command=ret).pack(pady=20)

# ---------------- DASHBOARD ----------------
def dashboard():
    win = tk.Tk()
    win.title("Library Dashboard")
    win.geometry("400x300")

    tk.Label(win, text="Library Management System", font=("Arial", 16, "bold")).pack(pady=20)

    tk.Button(win, text="Add Book", width=20, command=add_book).pack(pady=5)
    tk.Button(win, text="View Books", width=20, command=view_books).pack(pady=5)
    tk.Button(win, text="Issue Book", width=20, command=issue_book).pack(pady=5)
    tk.Button(win, text="Return Book", width=20, command=return_book).pack(pady=5)

    win.mainloop()

# ---------------- LOGIN ----------------
def login():
    user = user_entry.get()
    pwd = pass_entry.get()

    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (user, pwd)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        messagebox.showinfo("Success", "Login Successful")
        login_win.destroy()
        dashboard()
    else:
        messagebox.showerror("Error", "Invalid Credentials")

# ---------------- MAIN ----------------
connect_db()

login_win = tk.Tk()
login_win.title("Login")
login_win.geometry("300x200")

tk.Label(login_win, text="Username").pack(pady=5)
user_entry = tk.Entry(login_win)
user_entry.pack()

tk.Label(login_win, text="Password").pack(pady=5)
pass_entry = tk.Entry(login_win, show="*")
pass_entry.pack()

tk.Button(login_win, text="Login", command=login).pack(pady=15)

login_win.mainloop()
