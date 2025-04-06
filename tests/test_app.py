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
        at = AppTest.from_file("src/app.py")
        
        #simulate authentification success
        at.session_state["access_token"] = "mock_token"
        at.session_state["refresh_token"] = "mock_refresh"
        at.session_state["tokens_exchanged"] = True
        
        at.run() #execute streamlit app as a test

        #ensure the app is displaying the correct title 
        #check if any of the title calls starts with..
        assert any(title.startswith("Spotify New Releases") for title in at.title.values)
        #verify that no exceptions were raised during execution of the app
        assert not at.exception
        
    @patch('app.get_new_releases')
    def test_fetch_new_releases_button(self, mock_get_new_releases: MagicMock) -> None:
        """ This function tests if Fetch New Releases button works and displays mocked albums """
        
        #set up mock test to get the new releases from spotify
        mock_get_new_releases.return_value= [
            {
                "name" : "Mock Album",
                "artists" : [{"name": "Mock Artist"}],
                "release_date": "2024-04-19",
                "images": [{"url": "https://example.com/image.jpg"}],
                "id": "123"
            }
        ]
        at = AppTest.from_file("src/app.py") #load the streamlit app fromthe specified file for testing
        
        #set session state to simulate authorized access
        at.session_state["access_token"] = "mock_token"
        at.session_state["refresh_token"] = "mock_refresh"
        at.session_state["tokens_exchanged"] = True

        at.run() #simulate streamlit's starup state based on current session state
        
        assert "Fetch New Releases" in [b.label for b in at.button] #ensure button exists before clicking
        at.button("Fetch New Releases").click().run() #simulate "Fetch New Releases" button

        assert "Found 1 albums!" in at.markdown[0].values
        assert "Mock Album" in at.subheader[0].values

    @patch("app.refresh_access_token")
    def test_manual_refresh_button(self, mock_refresh_access_token):
        """ This functions tests if Refresh Access Token Manually button updates the access token"""
        
        #set up mock test to refresh the access token
        mock_refresh_access_token.return_value = {
            "access_token": "new_mock_token",
            "expires_in": 3600
        }

        at = AppTest.from_file("src/app.py")
        
        #set session state to test manual refresh feature
        at.session_state["access_token"] = "old_token"
        at.session_state["refresh_token"] = "mock_refresh"
        at.session_state["tokens_exchanged"] = True
        at.session_state["expires_in"] = 3600
        at.session_state["token_timestamp"] = 0

        at.run()
        assert "Refresh Access Token Manually" in [b.label for b in at.button] #ensure button exists before clicking
        at.button("Refresh Access Token Manually").click().run() #simulate clicking the "Refresh Access Token Manually" and rerun the app

        #confirm the manual refresh logic updates the session state access token to the new mocked value
        assert at.session_state["access_token"] == "new_mock_token"
