from django.test import TestCase
from asset_handling import views


class All(TestCase):

    def test_the_watchdog_stops_when_file_limit_reached(self):
        views.main_wd()
        self.assertTrue(False)
