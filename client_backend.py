#Импорт модулей стандартной библиотеки
import socket
import threading
import json
import sys
import hashlib

#Импорт сторонних модулей
import rsa

#импорт модулей месседжера
import messages

HOST = '127.0.0.1'
PORT = 9090
CODE = 'utf-8'

class Client():

    def __init__(self, host, port, pubkey, privkey):
        self.host = host
        self.port = port
        #статус авторизации клиента
        self.auth_status = False
        #статус подключения клиента
        self.connection_status = False
        # список с историей сообщений в текущей сессии
        self.history = {}
        #логин клиента
        self.login = None
        #список доступных контактов
        self.contacts = [None, ]
        #словарь с публичными ключами
        self.keys = {}
        #создаем объект клиентского сокета
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Гененрируем ключи для ассиметричного шифрования
        self.public_key, self.private_key = pubkey, privkey
    
    def connect(self):
        '''
        checking if client is connected to server. if not, trying to reconnect
        '''
        while True:
            if not self.connection_status:
                try:
                    self.sock.connect((self.host, self.port))
                    self.connection_status = True
                except:
                    continue
            else:
                continue

    def start_connection_thread(self):
        '''
        Starts self.connect is separate thread
        '''
        self.connection_thread = threading.Thread(target=self.connect)
        self.connection_thread.daemon = True
        self.connection_thread.start()

    def auth(self, login, password):
        '''
        sends authentication message to server. if server response with 202 code, return True, else none
        '''
        self.login = login
        self.passsword = hashlib.md5(password.encode()).hexdigest()
        message = messages.AuthMessage(self.login, self.passsword, self.public_key)
        if self.connection_status:
            self.sock.send(message.encode())
            try:
                encoded_auth_answer = self.sock.recv(1024)
            except Exception as e:
                print('Ошибка при прохождении аутентификации')
                print(e)
                sys.exit()
            auth_answer = json.loads(encoded_auth_answer.decode(CODE))
            if auth_answer['response'] == 202:
                self.auth_status = True
                self.contacts[0] = self.login
                return True
            else:
                return None
        else:
            return None

    def registrate(self, login, temp_password, password):
        '''
        sends registration message to server. If server response with code 202 returns True, else None
        '''
        hash_temp_password = hashlib.md5(temp_password.encode()).hexdigest()
        hash_password = hashlib.md5(password.encode()).hexdigest()
        message = messages.RegMessage(login, hash_temp_password, hash_password, self.public_key)
        if self.connection_status:
            self.sock.send(message.encode())
            try:
                encoded_reg_answer = self.sock.recv(1024)
            except Exception as e:
                print(e)
                print('Ошибка при прохождении регистрации')
                return None
            reg_answer = json.loads(encoded_reg_answer)
            if reg_answer['response'] == 202:
                return True
            else:
                return None
        else:
            return None

    def get_contacts(self):
        '''
        just returns contacts list
        '''
        return self.contacts

    def request_contacts(self):
        '''
        sends message to server to request online contacts
        '''
        msg = messages.GetContactsMessage(self.login)
        if self.auth_status:
            self.sock.send(msg.encode())
            return True
        else:
            return None

    def send_message(self, user_to, text):
        '''
        sends text message
        '''
        destination_public_key = self.keys.get(user_to)
        msg = messages.TextMessage(self.login, user_to, text, destination_public_key)
        if not self.history.get(user_to):
            self.history[user_to] = ['you: {}'.format(text), ]
        else:
            self.history[user_to].append('you: {}'.format(text))
        if self.auth_status:
            self.sock.send(msg.encode())
            return True
        else:
            return None

    def handle_incoming_messages(self):
        '''
        recive message and transfer it to suitable method
        '''
        msg = self.sock.recv(1024)
        if not msg:
            return None
        data = json.loads(msg.decode())
        action = data.get('action') or data.get('response')
        if not data:
            return None
        if action == 'probe':
            pass
        elif action == 'return_contacts':
            self.process_contacts(data)
        elif action == 202:
            pass
        elif action == 'msg':
            self.process_message(data)

    def process_contacts(self, data):
        contacts = data.get('contacts')
        self.contacts = list(contacts.keys())
        self.keys = {}
        for login in contacts:
            bin_key = messages.decode_binary_base64(contacts[login])
            key = rsa.PublicKey.load_pkcs1(bin_key)
            self.keys[login] = key

    def process_message(self, data):
        print('processing message')
        user_from = data.get('from')
        base64_encrypted_text = data.get('message')
        print(base64_encrypted_text)
        encrypted_text = messages.decode_binary_base64(base64_encrypted_text)
        print(encrypted_text)
        text = rsa.decrypt(encrypted_text, self.private_key).decode()
        print(text)
        if not self.history.get(user_from):
            self.history[user_from] = ['{}: {}'.format(user_from, text), ]
        else:
            self.history[user_from].append('{}: {}'.format(user_from, text))

    def main_loop(self):
        '''
        client application main loop
        '''
        while True:
            if self.connection_status:
                try:
                    self.handle_incoming_messages()
                except Exception as e:
                    continue

    def start_receive_thread(self):
        '''
        starts client application main loop in a separate thread
        '''
        self.receive_thread = threading.Thread(target=self.main_loop)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def stop(self):
        '''
        stops client and close socket
        '''
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except OSError:
            return

    def get_history(self, contact = None):
        '''
        gets message history to display in tui
        '''
        if contact:
            return self.history.get(contact, ['----------', ])
        else:
            return ['----------', ]