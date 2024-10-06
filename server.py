"""
author: Alexey Aleshchenok
date: 2024-01-10
"""
import socket
import threading

IP = '0.0.0.0'
PORT = 49002
QUEUE_SIZE = 5
MAX_PACKET = 4
WORDS_PER_CORE = 10
LOCK = threading.Lock()

clients = []
start_range = 1
flag = True


def handle_client(client_socket, hash_to_check, client_in_list):
    """
    Function to handle communication with a connected client.
    It assigns a range of numbers to the client to check against the provided hash.
    """
    global start_range, flag, clients
    # Receive the number of CPU cores from the client
    cpu_cores = int(client_socket.recv(1024).decode())
    while flag:
        with LOCK:
            # Determine the range of numbers to send based on CPU cores
            num_range = range(start_range, start_range + (WORDS_PER_CORE * cpu_cores))
            client_socket.send(f"{hash_to_check} {num_range.start} {num_range.stop}".encode())

            # Receive the result from the client
            result = client_socket.recv(1024).decode()
            if result == "NOT_FOUND":
                start_range += (WORDS_PER_CORE * cpu_cores)
                continue
            elif result.startswith("FOUND"):
                print(f"The number is {result.split(' ')[1]}")
                flag = False
                break

    # Notify the client to stop
    clients[client_in_list].send("STOP".encode())
    clients[client_in_list].close()


def main():
    """Main function to initialize the server and handle incoming client connections."""
    target_hash = input("Enter number's hash: ")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print('Waiting for connection....')
        while flag:
            # Accept a new client connection
            client_socket, addr = server_socket.accept()
            print(f'Connection with {addr}')
            clients.append(client_socket)
            client_in_list = len(clients) - 1
            # Create a new thread to handle the client
            client_handler = threading.Thread(target=handle_client, args=(client_socket, target_hash, client_in_list))
            client_handler.start()
    except socket.error as msg:
        print('failed to open server socket - ' + str(msg))
    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
