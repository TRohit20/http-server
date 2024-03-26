import socket
import threading
import os
import sys

def handle_connection(client_socket, directory=None):
    try:
        message = client_socket.recv(1024)
        print(message)
        request_line = message.decode().split("\r\n")[0]
        method, path, _ = request_line.split(" ")
        if method == "POST":
            if path.startswith("/files"):
                file = path[7:]
                full_path = os.path.join(directory, file)
                content = message.split(b"\r\n\r\n")[-1]
                with open(full_path, "wb") as data:
                   data.write(content)
                response = (
                    "HTTP/1.1 201 Created\r\n"
                    "Content-Type: text/plain\r\n"
                    "Content-Length: 2\r\n\r\n"
                    "OK"
                )
                client_socket.send(response.encode())
                return
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                client_socket.send(response.encode())
                return
        if method == "GET" and path.startswith("/files/"):
            filename = path[len("/files/") :]
            filepath = os.path.join(directory, filename)

            if os.path.exists(filepath) and os.path.isfile(filepath):
                with open(filepath, "rb") as file:
                    file_contents = file.read()

                response_headers = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/octet-stream\r\n"
                    f"Content-Length: {len(file_contents)}\r\n\r\n"
                )
                client_socket.send(response_headers.encode())
                client_socket.send(file_contents)
                return
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
                client_socket.send(response.encode())
                return

        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif path.startswith("/echo/"):
            echo_text = path[len("/echo/") :]
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(echo_text)}\r\n\r\n"
                f"{echo_text}"
            )
        elif path == "/user-agent":
            user_agent = None
            for line in message.decode().split("\r\n"):
                if line.startswith("User-Agent:"):
                    user_agent = line.split("User-Agent: ")[1]
                    break
            if user_agent is not None:
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain\r\n"
                    f"Content-Length: {len(user_agent)}\r\n\r\n"
                    f"{user_agent}"
                )
            else:
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n"
        client_socket.send(response.encode())
    finally:
        client_socket.close()

def main():
    try:
        directory = sys.argv[2]
    except IndexError:
        directory = None
    print("Logs from your program will appear here!")
    server_socket = socket.create_server(("localhost", 4221))
    try:
        while True:
            try:
                client_socket, address_info = server_socket.accept()
                print(f"Connection from {address_info}")
                thread = threading.Thread(
                    target=handle_connection,
                    args=(
                        client_socket,
                        directory,
                    ),
                )
                thread.start()
            except Exception as e:
                print("Err: ", e)
                break
    finally:
        server_socket.close()


if __name__ == "__main__":
    main() 