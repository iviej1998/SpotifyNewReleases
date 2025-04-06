"""
Test the app module
Author: Jillian Ivie (iviej@my.erau.edu)
"""
#import time
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
        at.session_state["token_timestamp"] = 0
        at.session_state["expires_in"] = 3600

        at.run() #simulate streamlit's starup state based on current session state
        
        fetch_button = next((b for b in at.button if "Fetch New Releases" in b.label), None)
        self.assertIsNotNone(fetch_button) #ensure button exists before clicking
        fetch_button.click().run() #simulate clicking the "Fetch New Releases" and rerun the app

        found_texts = [m.value for m in at.markdown]
        print("DEBUG: Markdown content:", found_texts)
        assert any("Found 2 albums!" in m for m in found_texts)
        subheaders = [s.value for s in at.subheader]
        assert any("Mock Album" in s for s in subheaders)

    @patch("app.get_auth_url")
    @patch("app.refresh_access_token")
    def test_manual_refresh_button(self, mock_refresh_access_token: MagicMock, mock_get_auth_url: MagicMock) -> None:
        """ This functions tests if Refresh Access Token Manually button updates the access token"""
        
        #set up mock test to refresh the access token
        mock_refresh_access_token.return_value = {
            "access_token": "new_mock_token",
            "expires_in": 3600
        }
        
        mock_get_auth_url.return_value = "https://mock-auth-url"

        at = AppTest.from_file("src/app.py")
        # Patch the internal session state used by Streamlit runtime
        with patch.dict("streamlit.runtime.scriptrunner.script_run_context.get_script_run_ctx().session_state", {
            "access_token": "old_token",
            "refresh_token": "mock_refresh",
            "expires_in": 3600,
            "token_timestamp": 0,
            "tokens_exchanged": True,
        }, clear=True):
            at.run()
        
        # Locate the button by label to be safer
        refresh_btn = next((b for b in at.button if "Refresh Access Token" in b.label), None)
        assert refresh_btn is not None, "Refresh Access Token Manually button not found"
        refresh_btn.click().run()

        #confirm the manual refresh logic updates the session state access token to the new mocked value
        assert at.session_state["access_token"] == "new_mock_token"
