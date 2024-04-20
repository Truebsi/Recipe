import streamlit as st
import json
import os
import pandas as pd

# Set page configuration
st.set_page_config(page_title="ShaRecipe", page_icon="🔪")

# GithubContents Klasse und Anpassungen (bitte sicherstellen, dass die Klasse definiert ist)
class GithubContents:
    def __init__(self, owner, repo, token):
        self.owner = owner
        self.repo = repo
        self.token = token
    
    def file_exists(self, filename):
        # Hier implementieren, ob die Datei existiert oder nicht
        pass
    
    def read_df(self, filename):
        # Hier implementieren, wie die DataFrame gelesen wird
        pass
    
    def write_df(self, filename, df, message):
        # Hier implementieren, wie die DataFrame geschrieben wird
        pass

# Initialisierung der GithubContents-Instanz
def init_github():
    """Initialize the GithubContents object."""
    if 'github' not in st.session_state:
        st.session_state.github = GithubContents(
            st.secrets["github"]["owner"],
            st.secrets["github"]["repo"],
            st.secrets["github"]["token"])

def get_csv_file_name():
    return 'user_data.csv'

def init_dataframe():
    """Initialize or load the dataframe."""
    filename = get_csv_file_name()
    if 'df' in st.session_state:
        pass
    elif st.session_state.github.file_exists(filename):
        st.session_state.df = st.session_state.github.read_df(filename)
    else:
        st.session_state.df = pd.DataFrame()

# Initialisierung des Session States für das neue Rezept
def init_new_recipe():
    if 'new_recipe' not in st.session_state:
        st.session_state.new_recipe = {"title": "", "ingredients": "", "instructions": ""}

# ------------------- Update functions -------------------
def update_mycontacts_table(new_entry):
    """Update the DataFrame and Github with a new entry."""
    init_dataframe() # make sure the DataFrame is up to date

    df = st.session_state.df
    new_entry_df = pd.DataFrame([new_entry])
    df = pd.concat([df, new_entry_df], ignore_index=True)
    st.session_state.df = df

    # Save the updated DataFrame to GitHub
    name = new_entry['name']
    filename = get_csv_file_name()
    msg = f"Add contact '{name}' to the file {filename}"
    st.session_state.github.write_df(filename, df, msg)

# Main function
def main():
    st.title("Rezept-Manager")
    
    # Laden der Rezepte aus der JSON-Datei oder Erstellen einer leeren Liste, wenn die Datei nicht existiert
    if os.path.exists("recipes.json"):
        with open("recipes.json", "r") as file:
            recipes = json.load(file)
    else:
        recipes = []
    
    # Initialisierung des Session States für Github
    init_github()
    
    # Initialisierung des Session States für DataFrame
    init_dataframe()
    
    # Initialisierung des Session States für das neue Rezept
    init_new_recipe()
    
    # Startseite mit Übersicht der hochgeladenen Rezepte
    show_recipe_overview(recipes)
    
    # Rezept hochladen Button in der oberen rechten Ecke platzieren
    st.write('<style>div.Widget.row-widget.stButton > div{flex: 0 0 auto;margin-left: auto;}</style>', unsafe_allow_html=True)
    if st.button("Rezept hochladen", key="upload_recipe_button"):
        upload_recipe(recipes)

def show_recipe_overview(recipes):
    st.header("Hochgeladene Rezepte")
    if not recipes:
        st.write("Keine Rezepte vorhanden.")
    else:
        for recipe in recipes:
            st.write(recipe["title"])

def upload_recipe(recipes):
    st.title("Neues Rezept erstellen")
    # Hier können Nutzer ein neues Rezept eingeben
    st.session_state.new_recipe["title"] = st.text_input("Titel", st.session_state.new_recipe.get("title", ""))
    st.session_state.new_recipe["ingredients"] = st.text_area("Zutaten", st.session_state.new_recipe.get("ingredients", ""))
    st.session_state.new_recipe["instructions"] = st.text_area("Anleitung", st.session_state.new_recipe.get("instructions", ""))

    if st.button("Rezept speichern"):
        if st.session_state.new_recipe["title"] and st.session_state.new_recipe["ingredients"] and st.session_state.new_recipe["instructions"]:
            recipes.append(st.session_state.new_recipe)
            save_recipes(recipes)
            st.success(f"Rezept '{st.session_state.new_recipe['title']}' erfolgreich gespeichert!")
            # Zurücksetzen des Session States für das neue Rezept
            st.session_state.new_recipe = {"title": "", "ingredients": "", "instructions": ""}
        else:
            st.error("Bitte füllen Sie alle Felder aus.")

def save_recipes(recipes):
    with open("recipes.json", "w") as file:
        json.dump(recipes, file)

if __name__ == "__main__":
    main()
