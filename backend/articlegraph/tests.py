from django.test import TestCase, Client


class ArticlegraphRequestTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        # Issue a GET request.
        response = self.client.get('/articlegraph/', {'title': 'Genetic algorithm: Review and application',
                                                      'authors': ','.join(
                                                          ['M Kumar', 'D Husain', 'N Upreti', 'D Gupta'])})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Do request again to check if loading from the database works.
        response = self.client.get('/articlegraph/', {'title': 'Genetic algorithm: Review and application',
                                                      'authors': ','.join(
                                                          ['M Kumar', 'D Husain', 'N Upreti', 'D Gupta'])})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
