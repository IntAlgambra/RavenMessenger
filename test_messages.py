import unittest

import rsa

import messages

def encode_crypto_data(data):
    base64_encrypted_data = base64.b64encode(data)
    base64_string_data = base64_encrypted_data.decode()
    return(base64_string_data)

def decode_crypto_data(data):
    base64_encrypted_data = data.encode()
    encrypted_data = base64.b64decode(base64_encrypted_data)
    return encrypted_data

class TestMessages(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_text_message(self):
        text = 'hello world'
        

        pass

if __name__ == '__main__':
    pubkey, privkey = rsa.newkeys(512, poolsize=8)
    unittest.main()

