""" 
Streamlit front-end application
Author: Jillian Ivie 
"""

import streamlit as st
import requests
import time #for managing token expiration
import data

@st.cache_data
def get_new_releases(access_token: str) -> list[dict]:
    """ This function gets the latest album releases """
    
    url = "https://api.spotify.com/v1/browse/new-releases"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, timeout=3)
    if response.status_code == 200:
        data = response.json()
        return data["albums"]["items"]
    else:
        st.error(f"Error {response.status_code}: {response.text}")
        return None

@st.cache_data
def get_album_tracks(access_token: str, album_id: str) -> list:
    """ This function fetches songs from a specific album by ID """
    
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, timeout=3)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        st.error(f"Error {response.status_code} fetching tracks: {response.text}")
        return []

def main():
    
    #add test mode to ensure streamlit won't sop early due to missing tokens when tests are running
    if "test_mode" in st.session_state:
        st.session_state.access_token = "mock_token"
        st.session_state.refresh_token = "mock_refresh_token"
        st.session_state.tokens_exchanged = True
        st.session_state.expires_in = 3600
        st.session_state.token_timestamp = time.time()
    
    
    st.title("Spotify New Releases")

    # initialize session state tokens and a flag to prevent reusing the authorization code
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "refresh_token" not in st.session_state:
        st.session_state.refresh_token = None
    if "tokens_exchanged" not in st.session_state:
        st.session_state.tokens_exchanged = False
    if "expires_in" not in st.session_state:
        st.session_state.expires_in = 3600
    if "token_timestamp" not in st.session_state:
        st.session_state.token_timestamp = time.time()

    # retrieve query parameters from the URL
    query_params = st.query_params.to_dict()

    # if token not exchanged yet and a 'code' is present, do the exchange
    if st.session_state.access_token is None and "code" in query_params and not st.session_state.tokens_exchanged:
        code = query_params["code"]
        st.write("Authorization code received. Exchanging for tokens...")
        token_info = data.exchange_code_for_token(code)
        if token_info:
            st.session_state.access_token = token_info.get("access_token")
            st.session_state.refresh_token = token_info.get("refresh_token")
            st.session_state.expires_in = token_info.get("expires_in", 3600)
            st.session_state.token_timestamp = time.time()
            st.session_state.tokens_exchanged = True  # set flag so we don't exchange again
            st.success("Token exchange successful!")
            st.query_params.clear() # clear the query parameters so the code won't be reused
        else:
            st.error("Token exchange failed.")

    # if no access token is available, prompt the user to authorize
    if st.session_state.access_token is None:
        st.write("Click the link below to authorize Spotify:")
        auth_url = data.get_auth_url()
        st.markdown(f"[Authorize Spotify]({auth_url})", unsafe_allow_html=True)
        st.stop()  # stop further execution until tokens are attained

    # display the access token
    st.write("Access Token:", st.session_state.access_token)

    # button to refresh the access token manually
    if st.button("Refresh Access Token Manually"):
        new_token_info = data.refresh_access_token(st.session_state.refresh_token)
        if new_token_info:
            st.session_state.access_token = new_token_info.get("access_token")
            st.session_state.expires_in = new_token_info.get("expires_in", st.session_state.expires_in)
            st.session_state.token_timestamp = time.time()
            st.success("Access token refreshed manually!")
        else:
            st.error("Failed to refresh access token.")
    
    # automatically refresh the token if needed
    data.refresh_if_needed()
    
    # debug session state
    st.write("Access Token", st.session_state.access_token)
    
    #display the access token
    st.write("Access Token:", st.session_state.access_token)

    # button to fetch and display new releases
    if st.button("Fetch New Releases"):
        fetch_func = st.session_state.get("get_new_releases", get_new_releases)
        albums = fetch_func(st.session_state.access_token)
        if albums:
            st.success(f"Found {len(albums)} albums!")
            for album in albums:
                with st.container():
                    cols = st.columns([1, 3])
                    if album.get("images"):
                        cols[0].image(album["images"][0]["url"], width=150)
                    with cols[1]:
                        st.subheader(album.get("name", "Unknown Album"))
                        artists = ", ".join([artist["name"] for artist in album.get("artists", [])])
                        st.write(f"**Artists:** {artists}")
                        st.write(f"**Release Date:** {album.get('release_date', 'N/A')}")
                    
                    with st.expander("Show Songs"):
                        track_func = st.session_state.get("get_album_tracks", get_album_tracks)
                        tracks = track_func(st.session_state.access_token, album["id"])
                        if tracks:
                            for index, track in enumerate(tracks, start=1):
                                st.write(f"{index}. {track.get('name', 'Unknown Track')}")
                        else:
                            st.write("No tracks found for this album.")
                    st.markdown("---")

if __name__ == '__main__':
    main()
