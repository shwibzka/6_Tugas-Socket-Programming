import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# Konfigurasi Server
SERVER_PORT = 12345
BUFFER_SIZE = 1024
CHATROOM_PASSWORD = "atharganteng123"

# Dapatkan IP device secara otomatis
hostname = socket.gethostname()
SERVER_IP = socket.gethostbyname(hostname)

# Membuat socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# Menyimpan informasi user dan client aktif
active_clients = {}

def log_message(message):
    """Menyimpan pesan ke dalam file log."""
    with open('server_chat_log.txt', 'a') as log_file:
        log_file.write(message + "\n")

def handle_messages():
    """Menangani pesan dari client dan menampilkan di GUI."""
    while True:
        try:
            message, client_address = server_socket.recvfrom(BUFFER_SIZE)
            decoded_message = message.decode()

            # Proses login atau pendaftaran client baru
            if client_address not in active_clients:
                username, password = decoded_message.split(":", 1)

                if password != CHATROOM_PASSWORD:
                    server_socket.sendto("Password salah.".encode(), client_address)
                    continue

                if username in active_clients.values():
                    server_socket.sendto("Username sudah dipakai.".encode(), client_address)
                    continue

                active_clients[client_address] = username
                display_message(f"[NEW CONNECTION] {username} connected from {client_address}.")
                server_socket.sendto(f"Welcome, {username}!".encode(), client_address)
                continue

            # Jika client keluar menggunakan tombol "Keluar"
            if decoded_message.lower() == '__exit__':
                username = active_clients.pop(client_address, None)
                if username:
                    display_message(f"[INFO] {username} left the chatroom.")
                continue

            # Tampilkan pesan dari client dan simpan ke log
            username = active_clients[client_address]
            log_message(f"[{username}] {decoded_message}")  # Simpan pesan ke log
            display_message(f"[{username}] {decoded_message}")

            # Teruskan pesan ke semua client lain
            forward_message = f"{username}: {decoded_message}"
            for client in active_clients:
                if client != client_address:
                    server_socket.sendto(forward_message.encode(), client)

        except Exception as e:
            display_message(f"[ERROR] {e}")

def display_message(message):
    """Menampilkan pesan di GUI."""
    log_area.config(state=tk.NORMAL)
    log_area.insert(tk.END, f"{message}\n")
    log_area.yview(tk.END)  # Scroll otomatis ke bawah
    log_area.config(state=tk.DISABLED)

def on_closing():
    """Menutup server dengan benar."""
    server_socket.close()
    root.quit()

def center_window(window, width, height):
    """Pusatkan jendela di layar."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# GUI Server
root = tk.Tk()
root.title("Server Chat Room")

# Pusatkan jendela di layar
center_window(root, 600, 400)

# Area log untuk menampilkan aktivitas client
log_area = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD)
log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Menampilkan IP dan Port server di log saat dijalankan
display_message(f"Server running on IP: {SERVER_IP}, Port: {SERVER_PORT}")

# Menangani saat jendela ditutup
root.protocol("WM_DELETE_WINDOW", on_closing)

# Jalankan thread untuk menangani pesan dari client
threading.Thread(target=handle_messages, daemon=True).start()

# Jalankan GUI Server
root.mainloop()