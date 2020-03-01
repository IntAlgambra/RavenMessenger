#Импорт стандартной библиотеки
import socket
import time
import threading
import sys
import json
import hashlib

#импорт сторонних библиотек
import click

#Импорт модулей месседжера
import server_database
import messages

# HOST = '127.0.0.1'
# PORT = 9090

database = server_database.Database()

class Server():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)

    def add_client(self, login, connection):
        '''
        add client socket to self.clients dict
        '''
        self.clients[login] = connection

    def get_online_clients(self):
        '''
        returning dictionary, which is containg info about online clients. dictionary has cliets logins as keys and clients public keys as values
        '''
        clients = {}
        for login in self.clients.keys():
            clients[login] = messages.encode_binary_base64(database.get_public_key(login))
        return clients

    def remove_client(self, login):
        '''
        Call thist method when client close connection. this method remove client information from self.clients dict and close client socket on server side
        '''
        connection = self.clients.pop(login)
        connection.close()

    def auth_client(self, client, data):
        '''
        Call this method when new client has been connected
        
        Method is waiting authenticate message from client. Im message contains correct login and password, client is authenticated and client socket is added to self.clients dict. If login or password is incorrect server closes connection with client
        '''
        login = data.get('user').get('login')
        password = data.get('user').get('password')
        public_key_base64string = data.get('user').get('public_key')
        public_key = messages.decode_binary_base64(public_key_base64string)
        auth_status = database.auth_client(login, password, public_key)
        if auth_status:
            response = messages.ServerResponce(202, 'OK')
            client.send(response.encode())
            self.add_client(login, client)
            self.update_contacts()
            print('access granted')
            return login
        else:
            response = messages.ServerResponce(402, 'Wrong login or password')
            client.send(response.encode())
            print('access denied')
            return False

    def reg_client(self, client, data):
        '''
        Call this method to registrate new client

        Warning! This method doesn't add new client to the database. New client should be added to database first by server admin with command 'python server.py add-account'. Method only for changing temporary password to actual password first time client log in   
        '''
        login = data.get('user').get('login')
        password = data.get('user').get('password')
        temp_password = data.get('user').get('temp_password')
        reg_status = database.reg_client(login, temp_password, password)
        if reg_status:
            response = messages.ServerResponce(202, 'OK')
            client.send(response.encode())
            self.add_client(login, password)
            print('access granted')
            return None
        else:
            response = messages.ServerResponce(402, 'Wrong temporary password')
            client.send(response.encode())
            print('access denied')
            return False

    def handle_connection(self, client):
        '''
        Method handling connection.
        '''
        connection_msg = client.recv(1024)
        if not connection_msg:
            print('closing connection')
            client.close()
            return None
        else:
            connection_data = json.loads(connection_msg.decode('utf-8'))
            if connection_data.get('action') == 'auth':
                return self.auth_client(client, connection_data)
            elif connection_data.get('action') == 'reg':
                return self.reg_client(client, connection_data)
            else:
                return None

    def handle_message(self, msg):
        '''
        processing messages from clients
        '''
        data = json.loads(msg.decode())
        print(data)
        user_to = data.get('to')
        client = self.clients.get(user_to)
        if client:
            client.send(msg)
            return True
        else:
            return None

    def return_contacts(self, data):
        '''
        Sending back to client his online contacts
        '''
        user = data.get('from')
        client = self.clients.get(user)
        contacts = self.get_online_clients()
        response  = messages.ReturnContactsMessage(contacts)
        client.send(response.encode())

    def update_contacts(self):
        print('updating contacts')
        online_clients = self.get_online_clients()
        for connection in self.clients.values():
            online_clients_message = messages.ReturnContactsMessage(online_clients)
            connection.send(online_clients_message.encode())


    def handle_client(self, client):
        '''
        main loop for each client.
        '''
        login = None
        while not login:
            try:
                login = self.handle_connection(client)
            except ConnectionResetError:
                print('client closed connection')
                return
        while True:
            msg = client.recv(1024)
            if not msg:
                self.remove_client(login)
                return None
            msg_data = json.loads(msg.decode())
            action = msg_data.get('action')
            if action == 'msg':
                self.handle_message(msg)
            elif action == 'get_contacts':
                print('returning contacts')
                self.return_contacts(msg_data)

    def start_client_thread(self, client):
        client_thread = threading.Thread(target=self.handle_client, args=(client, ))
        client_thread.daemon = True
        client_thread.start()

    def stop(self):
        '''
        Method to stop server. does't work in linux now, tthis is to be fixed.
        '''
        if input('') == 'quit' or 'q':
            self.sock.close()
            sys.exit()
            
    def catch_stop(self):
        '''
        Thread to catch signal to stop server
        '''
        stop_thread = threading.Thread(target=self.stop)
        stop_thread.daemon = True
        stop_thread.start()

    def start(self):
        info = '''
        server started at {}
        port: {}
        to quot server type 'q' or 'quit' on windows or cntrl+C on linux
        '''.format(time.asctime(), self.port)
        print(info)
        self.catch_stop()
        while True:
            try:
                client, adress = self.sock.accept()
            except OSError as e:
                print('server stopped')
                break
            print('client with adress {} connected at {}'.format(adress, time.asctime()))
            self.start_client_thread(client)

@click.group()
def cli():
    pass

#Функция запускающая сервер
@cli.command(help='start server on this computter')
@click.option(
    '--port',
    '-p',
    type = int,
    default = 9090,
    help = 'server port (do not use reserver ports)'
)
@click.option(
    '--host',
    '-h',
    default = '',
    help = "ip adress of server. use '' to use all allowed interfaces", 
)
def start_server(port, host):
    server = Server(host, port)
    server.start()

#Функция, добавляющая аккаунт на сервер
@cli.command(help='add new account to the server database')
@click.option('--login', '-l', help='login for new account')
@click.option('--password', '-p', help='temporary password for new account')
def add_account(login, password):
    hash_password = hashlib.md5(password.encode()).hexdigest()
    database.add_client(login, hash_password)
    print('account added')

if __name__ == '__main__':
    cli() 