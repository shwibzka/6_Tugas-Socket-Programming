import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Konfigurasi Client
BUFFER_SIZE = 1024

# Membuat socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def log_message(message):
    """Menyimpan pesan ke dalam file log berdasarkan username."""
    username_safe = username_entry.get().strip()  # Ambil username
    log_filename = f'{username_safe}_chat_log.txt'  # Nama file log berdasarkan username
    with open(log_filename, 'a') as log_file:
        log_file.write(message + "\n")

def receive_messages():
    """Menerima pesan dari server dan menampilkannya di GUI."""
    while True:
        try:
            message, _ = client_socket.recvfrom(BUFFER_SIZE)
            decoded_message = message.decode()
            display_message(decoded_message, align="left")  # Pesan dari client lain muncul di kiri
            log_message(decoded_message)  # Simpan ke file log client
        except OSError as e:
            display_message(f"[ERROR] Koneksi terputus: {e}", align="left")
            break

def display_message(message, align="left"):
    """Menampilkan pesan di area chat dengan perataan kiri/kanan."""
    chat_area.config(state=tk.NORMAL)
    if align == "left":
        chat_area.insert(tk.END, f"{message}\n", "left")  # Pesan dari orang lain
    else:
        chat_area.insert(tk.END, f"Anda: {message}\n", "right")  # Pesan dari diri sendiri
    chat_area.yview(tk.END)  # Scroll otomatis ke bawah
    chat_area.config(state=tk.DISABLED)

def send_message(event=None):
    """Kirim pesan ke server dan tampilkan di GUI sendiri."""
    message = message_entry.get().strip()
    if message:
        display_message(message, align="right")  # Tampilkan di kanan
        client_socket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))  # Kirim pesan ke server
        log_message(f"Anda: {message}")  # Simpan ke log client
        message_entry.delete(0, tk.END)  # Kosongkan input setelah kirim

def login():
    """Login dengan username dan password chatroom."""
    global SERVER_IP, SERVER_PORT
    SERVER_IP = server_ip_entry.get().strip()
    SERVER_PORT = int(server_port_entry.get().strip())
    
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    if username and password:
        client_socket.sendto(f"{username}:{password}".encode(), (SERVER_IP, SERVER_PORT))
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        response_message = response.decode()
        if "Welcome" in response_message or "User registered" in response_message:
            login_frame.pack_forget()  # Sembunyikan frame login
            chat_frame.pack(fill=tk.BOTH, expand=True)  # Tampilkan frame chat
            exit_button.place(relx=1.0, rely=0.0, anchor="ne")  # Munculkan tombol keluar
            threading.Thread(target=receive_messages, daemon=True).start()  # Mulai thread pesan
        else:
            messagebox.showerror("Login Gagal", response_message)
    else:
        messagebox.showwarning("Input Salah", "Username dan password tidak boleh kosong.")

def on_closing():
    """Kirim pesan keluar dan tutup aplikasi."""
    client_socket.sendto('__exit__'.encode(), (SERVER_IP, SERVER_PORT))  # Kirim pesan keluar
    root.quit()  # Tutup aplikasi

def center_window(window, width, height):
    """Pusatkan jendela di layar."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# GUI Utama
root = tk.Tk()
root.title("Client Chat Room")

# Pusatkan jendela di layar
center_window(root, 500, 400)

# Frame Login
login_frame = tk.Frame(root)
tk.Label(login_frame, text="Server IP").pack(pady=5)
server_ip_entry = tk.Entry(login_frame)
server_ip_entry.pack(pady=5)
tk.Label(login_frame, text="Server Port").pack(pady=5)
server_port_entry = tk.Entry(login_frame)
server_port_entry.insert(0, "12345")
server_port_entry.pack(pady=5)
tk.Label(login_frame, text="Username").pack(pady=5)
username_entry = tk.Entry(login_frame)
username_entry.pack(pady=5)
tk.Label(login_frame, text="Password").pack(pady=5)
password_entry = tk.Entry(login_frame, show="*")
password_entry.pack(pady=5)
tk.Button(login_frame, text="Login", command=login).pack(pady=10)
login_frame.pack(fill=tk.BOTH, expand=True)

# Frame Chat
chat_frame = tk.Frame(root)
chat_area = scrolledtext.ScrolledText(chat_frame, state=tk.DISABLED, wrap=tk.WORD)
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Tambahkan tag untuk perataan pesan (kiri dan kanan)
chat_area.tag_configure("left", justify="left")
chat_area.tag_configure("right", justify="right")

message_entry = tk.Entry(chat_frame)
message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
message_entry.bind("<Return>", send_message)  # Kirim dengan Enter

send_button = tk.Button(chat_frame, text="Kirim", command=send_message)
send_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Tombol Keluar (Hanya muncul di chat frame)
exit_button = tk.Button(root, text="Keluar", command=on_closing)

# Event untuk menutup jendela dengan benar
root.protocol("WM_DELETE_WINDOW", on_closing)

# Jalankan GUI
root.mainloop()