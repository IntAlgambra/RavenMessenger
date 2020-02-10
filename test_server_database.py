import unittest
import server_database as database

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = database.Database()
        cls.clients = [
            ['John', '12345'],
            ['James', 'qwerty'],
            ['Luke', 'starwars']
        ]

    def setUp(self):
        self.db.update_all()
        for record in self.clients:
            self.db.add_client(record[0], record[1])

    def tearDown(self):
        pass

    def test_check_client(self):
        check = self.db.check_client('John')
        self.assertTrue(check)

if __name__ == '__main__':
    unittest.main()