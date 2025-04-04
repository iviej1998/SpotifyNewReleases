"""
Test the app module
Author: Jillian Ivie (iviej@my.erau.edu)
"""
from unittest import TestCase # for creating new test cases
from streamlit.testing.v1 import AppTest # for testing of streamlit applications

#create a class that inherits from TestCase
class Test(TestCase):
    """ This class inherits from TestCase and will be recognized by Python's unittest framework as a collection of test methods

    Args:
        TestCase
    """
    def test_ui_title_and_header(self):
        """This function tests the title of the user interface
        """
        #use from_file class method of AppTest to load streamlit app from the specified file path
        at = AppTest.from_file("./SpotifyNewReleases/src/app.py")
        at.run() #execute streamlit app as a test

        #ensure the app is displaying the correct title
        assert at.title[0].values.startswith("Spotify New Releases")
        #verify that no exceptions were raised during execution of the app
        assert not at.exception
