import socket
import hashlib
import threading
import os

SERVER_IP = '127.0.0.1'
SERVER_PORT = 49002
MAX_PACKET = 1024

threads = []
result_event = threading.Event()
result = None


def get_cpu_cores():
    """Returns the number of CPU cores available on the client machine."""
    return os.cpu_count()


def md5_hash(number):
    """Calculates the MD5 hash of a given number."""
    return hashlib.md5(str(number).encode()).hexdigest()


def check_numbers(target_hash, num_range):
    """
    Function to check a range of numbers against the target hash.
    Sets the result and result_event if the target hash is found.
    """
    global result_event, result
    for num in num_range:
        if result_event.is_set():
            return
        if md5_hash(num) == target_hash:
            result_event.set()
            result = num
            return


def main():
    """Main function to handle client-server communication."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print('You have connected to the server ')
        cpu_cores = get_cpu_cores()
        client_socket.send(str(cpu_cores).encode())
        while True:
            data = client_socket.recv(1024).decode()
            if data == "STOP":
                break
            target_hash, start, end = data.split(' ')
            num_range = range(int(start), int(end))

            # Create and start threads to check numbers in parallel
            for i in range(cpu_cores):
                t = threading.Thread(target=check_numbers, args=(target_hash, num_range[i::cpu_cores]))
                threads.append(t)
                t.start()
                if result_event.is_set():
                    break

            # Wait for all threads to complete
            for t in threads:
                t.join()

            # Send the result to the server
            if result_event.is_set():
                report = "FOUND " + str(result)
                client_socket.send(report.encode())
            else:
                client_socket.send("NOT_FOUND".encode())
    except socket.error as msg:
        print('Failed to open server socket - ' + str(msg))
    finally:
        client_socket.close()


if __name__ == '__main__':
    main()
