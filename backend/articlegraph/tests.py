from django.test import TestCase, Client

class BasicRequestTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        # Issue a GET request.
        response = self.client.get('/articlegraph/', {'title': 'Genetic algorithm: Review and application',
                                                      'authors': ','.join(['M Kumar', 'D Husain', 'N Upreti', 'D Gupta'])})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
