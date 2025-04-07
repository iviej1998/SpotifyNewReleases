"""
Test the app module
Author: Jillian Ivie (iviej@my.erau.edu)
"""
#import time
import os
os.environ["ST_TEST_MODE"] = "1"
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
    
    @patch("src.app.get_album_tracks")    
    @patch("src.app.get_new_releases")
    def test_fetch_new_releases_button(self, mock_get_new_releases: MagicMock, mock_get_album_tracks: MagicMock) -> None:
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
        
        mock_get_album_tracks.return_value = [
            {"name": "Mock Song 1"},
            {"name": "Mock Song 2"}
        ]
        
        print("MOCK NEW RELEASES:", mock_get_new_releases.return_value)
        
        at = AppTest.from_file("src/app.py") #load the streamlit app fromthe specified file for testing
        
        #set session state to simulate authorized access
        at.session_state["access_token"] = "mock_token"
        at.session_state["refresh_token"] = "mock_refresh"
        at.session_state["tokens_exchanged"] = True
        at.session_state["token_timestamp"] = 0
        at.session_state["expires_in"] = 3600
        
        at.run() #simulate streamlit's starup state based on current session state
        
        # click "Fetch New Releases"
        fetch_button = next((b for b in at.button if "Fetch New Releases" in b.label), None)
        for b in at.button:
            print("Button:", b.label)
            
        self.assertIsNotNone(fetch_button, "Fetch New Releases button not found")

        fetch_button.click().run()
        

        print("Subheaders:", [s.value for s in at.subheader])
        print("Successes:", [s.value for s in at.success])
        
        # check the subheader shows the mock album name
        subheaders = [s.value for s in at.subheader]
        print("Subheaders:", subheaders)

        self.assertTrue(any("Mock Album" in s for s in subheaders), "Mock Album not found in subheaders")
    
    @patch("data.refresh_access_token")
    def test_manual_refresh_button(self, mock_refresh_access_token):
        """Test if Refresh Access Token Manually button updates the access token"""

        at = AppTest.from_file("src/app.py")
        
        at.session_state["access_token"] = "mock_token"
        at.session_state["refresh_token"] = "mock_refresh"
        at.session_state["tokens_exchanged"] = True
        at.session_state["token_timestamp"] = 0
        at.session_state["expires_in"] = 3600
        
        mock_refresh_access_token.return_value = {
        "access_token": "new_mock_token",
        "expires_in": 3600
        }
        
        at.run()

        # Find the refresh button safely
        refresh_button = next((b for b in at.button if "Refresh Access Token Manually" in b.label), None)
        self.assertIsNotNone(refresh_button, "Refresh Access Token Manually button not found")

        # Simulate the button click and rerun the app
        refresh_button.click().run()

        # Assert that the token was updated
        self.assertEqual(at.session_state["access_token"], "new_mock_token")