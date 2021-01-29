from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient

from . import models


REPORTS_URL = reverse('bugreports:reports-list')


class ReportsCreationApiTest(TestCase):
    '''Test bug report.
    '''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@vpvn.ru',
            'tester'
        )
        self.client.force_authenticate(self.user)
        models.BuggyProject.objects.create(
            pk='test',
            name='Test buggy project')

    def test_create_report_successful(self):
        '''Test report creation.
        '''
        report = {
            'project_id': 'test',
            'exception_text': 'Test exception',
            'email': 'test@vpvn.ru',
            'ip': '127.0.0.1',
            'os': 'linux',
            'details': 'no details here',
        }
        self.client.post(
            REPORTS_URL, report, format='json')
        bug_exists = models.Bug.objects.filter(
            buguuid=models.buguuid(
                report['project_id'],
                report['exception_text']),
        ).exists()
        occasian_exists = models.Occasion.objects.filter(
            bug__buguuid=models.buguuid(
                report['project_id'],
                report['exception_text']),
            email=report['email'],
            os=report['os'],
            details=report['details'],
        ).exists()
        self.assertTrue(bug_exists and occasian_exists)
