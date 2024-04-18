import streamlit as st
import streamlit_authenticator as stauth    
import pandas as pd
from datetime import date

#https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/

#Sign in Interface:

user_credentials = {}

def register(username, password):
    """Registriere einen neuen Benutzer."""
    if username not in user_credentials:
        user_credentials[username] = password
        return True
    return False

def main():
    st.title("Sign-in Interface")

    # Benutzername und Passwort für die Registrierung eingeben
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")

    # Sign-in-Button
    if st.button("Sign in"):
        if register(username, password):
            st.success("Erfolgreich registriert als {}".format(username))
            # Füge hier den weiteren Code hinzu, den du nach der erfolgreichen Registrierung ausführen möchtest
        else:
            st.error("Benutzername bereits vergeben. Bitte wähle einen anderen.")

#Login Interface:

user_credentials = {
    'user1': 'password1',
    'user2': 'password2'
}

def authenticate(username, password):
    """Überprüfe die Benutzeranmeldeinformationen."""
    if username in user_credentials and user_credentials[username] == password:
        return True
    return False

def main():
    st.title("Login Interface")

    # Benutzername und Passwort eingeben
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")

    # Login-Button
    if st.button("Login"):
        if authenticate(username, password):
            st.success("Erfolgreich eingeloggt als {}".format(username))
            # Füge hier den weiteren Code hinzu, den du nach dem erfolgreichen Login ausführen möchtest
        else:
            st.error("Ungültige Anmeldeinformationen. Bitte versuche es erneut.")

if __name__ == "__main__":
    main()