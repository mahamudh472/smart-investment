from django.test import TestCase

# Create your tests here.
class TestingTest(TestCase):
    def setUp(self):
        self.name="Mahmud"
    def test_check_name(self):
        self.assertEqual(self.name, "Mahmud")