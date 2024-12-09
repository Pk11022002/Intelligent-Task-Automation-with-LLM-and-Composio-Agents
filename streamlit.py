import streamlit as st
import webbrowser
from composio_authentication import create_url

# Define the Streamlit app
def main():
    st.title("App Authentication")

    # Display the username input box
    username = st.text_input("Enter your username:")

    # Display the "Sign Up" button
    if st.button("Sign Up"):
        if username:  # Check if the username is provided
            # Get the dynamic authentication URL
            auth_url = create_url(username)  # Pass the username to create_url

            if auth_url:
                # Open the URL in the user's default web browser
                webbrowser.open_new_tab(auth_url)
            else:
                st.write("You are already authenticated with Google Calendar.")
        else:
            st.write("Please enter a username.")

if __name__ == "__main__":
    main()
