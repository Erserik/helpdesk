# tests.py
from django.test import TestCase
from django.core.mail import send_mail, outbox

class EmailTestCase(TestCase):
    def test_send_mail(self):
        # Call the send_mail function
        send_mail(
            'Welcome to Our Site',
            'Thanks for signing up!',
            'from@example.com',
            ['erserikdaryn82@gmail.com'],
            fail_silently=False,
        )

        # Check that one email was sent
        self.assertEqual(len(outbox), 1)

        # Verify email details
        email = outbox[0]
        self.assertEqual(email.subject, 'Welcome to Our Site')
        self.assertEqual(email.body, 'Thanks for signing up!')
        self.assertEqual(email.from_email, 'from@example.com')
        self.assertEqual(email.to, ['erserikdaryn82@gmail.com'])
