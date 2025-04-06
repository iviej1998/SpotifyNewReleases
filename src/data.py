"""
    Data Aquisition for Spotify Data
    Author: Jillian Ivie
"""

import urllib.parse
import requests
import base64
import streamlit as st
import time

# Spotify Client Credentials
CLIENT_ID = "8c19c2a6086d4f72bd03996391a93652"
CLIENT_SECRET = "e77e7a0fa8694f79a99f05cddcd0633e"
REDIRECT_URI = "https://new-releases-spotify.streamlit.app/" #redirect to streamlit app after spotify authentification
SCOPE = "user-top-read" #adjust scope

def get_auth_url() -> str:
    """ 
    Generate the Spotify authorization URL.
    Direct the user to this URL to authorize the app.
    """
    auth_url = "https://accounts.spotify.com/authorize"
    
    parameters = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }
    return f"{auth_url}?{urllib.parse.urlencode(parameters)}"

def exchange_code_for_token(code: str) -> dict:
    """ 
    Exchange the authorization code for access to refresh tokens 
    
    Returns: 
        A dictionary containing access_token, refresh_token, expires_in..
        or None if there was an error
    """
    token_url = "https://accounts.spotify.com/api/token"
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(token_url, headers=headers, data=data, timeout=3)
    if response.status_code == 200: #successfull request
        return response.json()  # Contains access_token, refresh_token, expires_in, etc.
    else:
        st.error("Error exchanging code for token: " + response.text)
        return None

def refresh_access_token(refresh_token: str) -> dict:
    """
    Refresh the access token using the provided refresh token.
    
    Returns:
        A dictionary containing the new access_token, expires_in, etc.,
        or None if there was an error.
    """
    token_url = "https://accounts.spotify.com/api/token"
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(token_url, headers=headers, data=data, timeout=3)
    if response.status_code == 200:
        token_info = response.json()  # Contains the new access_token and expires_in, etc.
        if "access_token" in token_info:
            return token_info
    else:
        return None

def refresh_if_needed():
    """Automatically refresh the access token if it's nearly expired."""
    if ("access_token" in st.session_state and
        "expires_in" in st.session_state and
        "token_timestamp" in st.session_state):
        current_time = time.time()
        elapsed = current_time - st.session_state["token_timestamp"]
        # refresh 60 seconds before expiration
        if elapsed >= st.session_state["expires_in"] - 60:
            st.write("Access token is expiring. Refreshing automatically...")
            new_token_info = refresh_access_token(st.session_state["refresh_token"])
            if new_token_info:
                st.session_state["access_token"] = new_token_info.get("access_token")
                # spotify may return a new expires_in value; update it
                st.session_state["expires_in"] = new_token_info.get("expires_in", st.session_state["expires_in"])
                st.session_state["token_timestamp"] = time.time()
                st.success("Access token refreshed automatically!")
            else:
                st.error("Failed to refresh access token.")


if __name__ == "__main__":
    
    # for testing purposes, print the authorization URL
    print("Visit the following URL to authorize the app:")
    print(get_auth_url())