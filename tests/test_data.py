"""
Test the data module
Author: Jillian Ivie (iviej@my.erau.edu)
"""

import urllib.parse #to convert REDIRECT_URI to URL encoded string
from unittest import TestCase # to create individual test cases
from unittest import main # to run tests correctly
from unittest.mock import patch # to temporarily replace real objects with mock objects during tests
from unittest.mock import MagicMock # to create mock objects with customizable behaviors
import data

class TestSpotifyData(TestCase):
    """ This class inherits from TestCase """

    def test_get_auth_url(self) -> None:
        """ This function tests is the authorization URL is generated correctly """
        #get the authentication URL
        url = data.get_auth_url()
        
        #asert that the generated URL includes all necessary components
        self.assertIn("https://accounts.spotify.com/authorize", url)
        self.assertIn(f"client_id={data.CLIENT_ID}" , url)
        self.assertIn("response_type=code", url)
        self.assertIn(f"redirect_uri={urllib.parse.quote(data.REDIRECT_URI, safe='')}", url)
        self.assertIn(f"scope={data.SCOPE}", url)
        
    @patch("data.requests.post") #decorator to mock the requests.post method used inside func
    def test_exchange_code_for_token_success(self, mock_post: MagicMock) -> None:
        """ This function tests successful token exhange """
        
        #set up mock response to mimic a successful Spotify API token exchange response
        mock_response = MagicMock() #create a mock object
        mock_response.status_code = 200 # successful status code
        mock_response.json.return_value = { #mock the response from a spotify API call (POST request)
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response # return the mock_reponse object instead of actually making a request
        
        #call original function with a valid auth code
        result = data.exchange_code_for_token("valid_code")
        # assert the correct tokens are returned
        self.assertIsNotNone(result)
        self.assertEqual(result["access_token"], "test_access_token")
        self.assertEqual(result["refresh_token"], "test_refresh_token")
        
    @patch("data.requests.post")
    def test_exchange_code_for_token_failure(self, mock_post: MagicMock) -> None:
        """ This function tests token exhange failure handling """
        
        mock_response = MagicMock()
        mock_response.status_code = 400 # failure status code
        mock_response.text = "Invalid authorization code" #customize what the test's fake HTTP response will say
        mock_post.return_value = mock_response
        #call original func with invalid auth code
        result = data.exchange_code_for_token("invalid_code")
        #confirm function returns None upon failure
        self.assertIsNone(result)
        
    @patch("data.requests.post")
    def test_refresh_access_token_success(self, mock_post: MagicMock) -> None:
        """ This function tests successfull token refresh """
        #mock spotify API request for refreshing access tokens
        #create a successfull mock refresh response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        #check refresh function preoperly processes a valid refresh token
        result = data.refresh_access_token("valid_refresh_token")
        self.assertIsNotNone(result)
        self.assertEqual(result["access_token"], "new_access_token")
        
    @patch("data.requests.post")
    def test_refresh_access_token_failure(self, mock_post: MagicMock) -> None:
        """ This function token refresh failure handling """
        
        #set up mock failure response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid refresh token"
        mock_post.return_value = mock_response
        
        #confirm function handles failures
        result = data.refresh_access_token("invalid_refresh_token")
        self.assertIsNone(result)

    #decorators are applied bottom to top in execution
    @patch("data.st", autospec=True)
    @patch("data.time.time")
    @patch("data.refresh_access_token")
    def test_refresh_if_needed(self, mock_refresh: MagicMock, mock_time: MagicMock, mock_st: MagicMock) -> None:
        """" test refresh if needed button """
        # Setup mock time to simulate expiration
        mock_time.return_value = 3700

        # Setup refresh response
        mock_refresh.return_value = {
            "access_token": "refreshed_access_token",
            "expires_in": 3600
        }

        # Use real dict to mimic session state
        session = {
            "access_token": "old_token",
            "expires_in": 3600,
            "token_timestamp": 0,
            "refresh_token": "valid_refresh_token"
        }

        # Assign dict to mock_st.session_state directly
        mock_st.session_state = session

        # Call function under test
        data.refresh_if_needed()

        # Assert updates actually happened in the real dict
        self.assertEqual(session["access_token"], "refreshed_access_token")
        self.assertEqual(session["expires_in"], 3600)
        self.assertTrue("token_timestamp" in session)

# Run the test cases
if __name__ == "__main__":
    main()