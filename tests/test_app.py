"""
Test the app module
Author: Jillian Ivie (iviej@my.erau.edu)
"""
from unittest import TestCase # for creating new test cases
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest # for testing of streamlit applications

#create a class that inherits from TestCase
class Test(TestCase):
    """ This class inherits from TestCase and will be recognized by Python's unittest framework as a collection of test methods """
    
    def test_ui_title_and_header(self):
        """ This function tests if the UI displays the correct title and does not raise exceptions """
        #use from_file class method of AppTest to load streamlit app from the specified file path
        at = AppTest.from_file(".../src/app.py")
        at.run() #execute streamlit app as a test

        #ensure the app is displaying the correct title
        assert at.title[0].values.startswith("Spotify New Releases")
        #verify that no exceptions were raised during execution of the app
        assert not at.exception
        
    @patch('src.app.get_new_releases')
    def test_fetch_new_releases_button(self, mock_get_new_releases: MagicMock) -> None:
        """ This function tests if Fetch New Releases button works and displays mocked albums """
        
