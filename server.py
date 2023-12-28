import socket
import threading

# Connection data
host = '127.0.0.1'
port = 55555

# starting server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists for clients and their nicknames
clients = []
nicknames = []
ban_list = []


# Sending messages to all connected clients
def broadcast(message):
    for client in clients:
        client.send(message)


# Handling message from clients
def handle(client):
    while True:
        try:
            # Broadcasting messages
            msg = message = client.recv(1024)
            if msg.decode('utf-8').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('utf-8')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('Command was refused.'.encode('utf-8'))
            elif msg.decode('utf-8').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('utf-8')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as file:
                        file.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned.')
                else:
                    client.send('Command was refused.'.encode('utf-8'))
            else:
                broadcast(message)

        except:
            # Removing and closing clients
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast('{} left server.'.format(nickname.encode('utf-8')))
                nicknames.remove(nickname)
                break


# Receiving function
def receive():
    while True:
        # Accept connection
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        # Request and store nickname
        client.send('Nick'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        with open('bans.txt', 'r') as file:
            bans = file.readlines()

        if nickname + '\n' in bans:
            client.send('BAN'.encode('utf-8'))
            client.close()
            continue

        if nickname == 'admin':
            client.send('Password'.encode('utf-8'))
            password = client.recv(1024).decode('utf-8')

            if password != 'adminpass':
                client.send('REFUSE'.encode('utf-8'))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)

        # Print and broadcast nickname
        print('Nickname: {}'.format(nickname))
        broadcast('{} joined server.'.format(nickname).encode('utf-8'))
        client.send('Connected to server.'.encode('utf-8'))

        # Start handling threads for client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by an admin.'.encode('utf-8'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by an admin.'.encode('utf-8'))


print('Server is listening')
receive()
