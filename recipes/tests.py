from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from django.test.utils import override_settings
import json

class AIRecipeFinderTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.url = reverse('ai_recipe_finder_api')

    def test_anonymous_user_redirected(self):
        """Anonymous user should be redirected to login page."""
        response = self.client.post(self.url, data=json.dumps({'ingredients': 'chicken'}), content_type='application/json')
        self.assertEqual(response.status_code, 302)  # login_required redirect

    @override_settings(GROQ_API_KEY='test_key')
    def test_get_request_not_allowed(self):
        """GET request should return 400 Bad Request."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'POST request required.'})

    @override_settings(GROQ_API_KEY='')
    def test_missing_api_key(self):
        """Missing Groq API Key should return 500 Internal Server Error."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(self.url, data=json.dumps({'ingredients': 'chicken'}), content_type='application/json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('Groq API Key is not configured', response.json().get('error', ''))

    @override_settings(GROQ_API_KEY='test_key')
    def test_missing_ingredients(self):
        """Missing ingredients parameter should return 400 Bad Request."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(self.url, data=json.dumps({'ingredients': '', 'dietary_preference': 'keto'}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Ingredients list is required.'})

    @override_settings(GROQ_API_KEY='test_key')
    @patch('requests.post')
    def test_successful_recipe_finding(self, mock_post):
        """Successful API call to Groq should return 3 recipe suggestions."""
        self.client.login(username='testuser', password='password123')
        
        # Mock API Response from Groq matching our new schema
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps({
                        'recipes': [
                            {
                                'title': 'AI Chicken Salad',
                                'description': 'A delicious salad',
                                'ingredients': ['1 lb chicken', 'Lettuce'],
                                'instructions': ['1. Toss ingredients']
                            },
                            {
                                'title': 'AI Chicken Wrap',
                                'description': 'A quick wrap',
                                'ingredients': ['Chicken', 'Tortilla'],
                                'instructions': ['1. Wrap chicken']
                            },
                            {
                                'title': 'AI Garlic Chicken',
                                'description': 'Garlicky goodness',
                                'ingredients': ['Chicken', 'Garlic'],
                                'instructions': ['1. Cook chicken with garlic']
                            }
                        ]
                    })
                }
            }]
        }
        mock_post.return_value = mock_response

        response = self.client.post(
            self.url,
            data=json.dumps({'ingredients': 'chicken', 'dietary_preference': ''}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertIn('recipes', res_data)
        self.assertEqual(len(res_data['recipes']), 3)
        self.assertEqual(res_data['recipes'][0]['title'], 'AI Chicken Salad')
        self.assertEqual(res_data['recipes'][1]['title'], 'AI Chicken Wrap')
        self.assertEqual(res_data['recipes'][2]['title'], 'AI Garlic Chicken')


