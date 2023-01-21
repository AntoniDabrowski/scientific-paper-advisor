from django.test import TestCase, Client


class ArticlegraphRequestTests(TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_basic_request(self):
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

    def test_special_characters_in_author_name(self):
        # Issue a GET request.
        response = self.client.get('/articlegraph/', {'title': 'Reducing the time complexity of the derandomized '
                                                               'evolution strategy with covariance '
                                                               'matrix adaptation (CMA-ES)',
                                                      'authors': ','.join(
                                                          ['N Hansen', 'SD Muller'])})

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
