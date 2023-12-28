import socket
import threading

# Nickname
nickname = input("Insert your nickname: ")
if nickname == 'admin':
    password = input('Enter admin password: ')

# Connecting to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

stop_thread = False


# Listening to server and sending nickname
def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            # Receive message from server
            # If 'Nick' send nickname
            message = client.recv(1024).decode('utf-8')
            if message == 'Nick':
                client.send(nickname.encode('utf-8'))
                next_message = client.recv(1024).decode('utf-8')
                if next_message == 'PASS':
                    client.send(password.encode('utf-8'))
                    if client.recv(1024).decode('utf-8') == 'REFUSE':
                        print('Connection was refused. Wrong password')
                        stop_thread = True
                elif next_message == 'BAN':
                    print('Connection refused. Banned by admin.')
                    client.close()
                    stop_thread = True
            else:
                print(message)
        except:
            # Close Connection when error
            print('error occurred')
            client.close()
            break


# Sending messages to server
def write():
    while True:
        if stop_thread:
            break
        message = f'{nickname}: {input("")}'
        if message[len(nickname) + 2:].startswith('/'):
            # /command
            if nickname == 'admin':
                if message[len(nickname) + 2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname) + 8:]}'.encode("utf-8"))
                elif message[len(nickname) + 2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname) + 7:]}'.encode("utf-8"))
            else:
                print('Access denied.')
        else:
            client.send(message.encode("utf-8"))


# Starting threads for listening and writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
