import unittest

from grindstone.utils import generate_token


class UtilsTestCase(unittest.TestCase):
    def test_generate_token_default_case(self):
        token = generate_token()
        self.assertTrue(token)
        self.assertEquals(len(token), 16)
    
    def test_generate_token_different_length(self):
        token_length = 50
        token = generate_token(token_length)
        self.assertTrue(token)
        self.assertEquals(len(token), token_length)


if __name__ == '__main__':
    unittest.main()
