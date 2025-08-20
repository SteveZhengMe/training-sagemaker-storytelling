import unittest

class AlwaysPassTestCase(unittest.TestCase):
    def test_true_is_true(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
