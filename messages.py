#импорты стандартной библиотеки
import json
import time
import base64

#импорты стороннихх библиотек
import rsa

CODE = 'utf-8'

#функция кодирования бинарных данных в строку с помощью BASE64
def encode_binary_base64(data):
    base64_encrypted_data = base64.b64encode(data)
    base64_string_data = base64_encrypted_data.decode(CODE)
    return(base64_string_data)

#функция декодирования бинарных данных в строку с помощью BASE64
def decode_binary_base64(data):
    base64_encrypted_data = data.encode(CODE)
    encrypted_data = base64.b64decode(base64_encrypted_data)
    return encrypted_data

#Классы для создания сообщений клиентской части
class Message():

    def __init__(self):
        self.data = None

    def encode(self):
        encoded_msg = json.dumps(self.data).encode(CODE)
        return encoded_msg

class AuthMessage(Message):

    def __init__(self, login, password, public_key):
        bin_key = public_key.save_pkcs1()
        key_base64string = encode_binary_base64(bin_key)
        self.login = login
        self.password = password
        self.data = {
            'action': 'auth',
            'time': time.time(),
            'user': {
                'login': self.login,
                'password': self.password,
                'public_key': key_base64string
            }
        }

class RegMessage(AuthMessage):

    def __init__(self, login, temp_password, password, public_key):
        super().__init__(login, password, public_key)
        self.data['action'] = 'reg'
        self.data['user']['temp_password'] = temp_password

class TextMessage(Message):

    def __init__(self, user_from, user_to, text, pubkey):
        self.user_from = user_from
        self.user_to = user_to
        self.text = text
        bin_text = text.encode()
        encrypted_text = rsa.encrypt(bin_text, pubkey)
        base64_text = encode_binary_base64(encrypted_text) 
        self.time = time.asctime()
        self.data = {
            'action': 'msg',
            'time':time.time(),
            'from': self.user_from,
            'to': self.user_to,
            'message': base64_text,
        }

    def format(self):
        pass

class PublicKeyMessage(Message):
    def __init__(self, user_from, key):
        self.data = {
            'action': 'key_transfer',
            'time': time.time(),
            'from': user_from,
            'key': key
        }

class GetContactsMessage(Message):
    def __init__(self, user_from):
        self.data = {
            'action': 'get_contacts',
            'time': time.time(),
            'from': user_from,
        }

class QuitMessage(Message):

    def __init__(self):
        self.data = {'action': 'quit'}

#классы сообщений серверной части
#Сообщение для проверки подключения пользователя к серверу
class ProbeMessage(Message):
    def __init__(self):
        self.data = {
            'action': 'probe',
            'time': time.time()
        }

class ReturnContactsMessage(Message):
    def __init__(self, contacts):
        self.data = {
            'action': 'return_contacts',
            'time': time.time(),
            'contacts': contacts
        }

#Сообщение-ответ на действие пользователя
class ServerResponce(Message):
    def __init__(self, code, message):
        self.data = {
            'response': code,
            'time': time.time()
        }
        if code >= 300:
            self.data['error'] = message
        else:
            self.data['alert'] = message
            
if __name__ == '__main__':
    m1 = AuthMessage('lol', 'kek').encode()
    m3 = TextMessage('kek1', 'kek2', 'olololo1111111').encode()
    m4 = RegMessage('Jean', 'temp_pass', 'pass').encode()
    print(m1, m3, m4, sep='\n')


