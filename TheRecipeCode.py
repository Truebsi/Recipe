# in python reade a csv with recepies coulums ID, Title, ingredients, instructions and imagelink and show a page using streamlit allowing to filter the recepies based on a search text

import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
import os
import io
import re
import ast
import random
from github_contents import GithubContents  # Stellen Sie sicher, dass die Klasse definiert ist
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# Set page configuration
st.set_page_config(page_title="ShaRecipe", page_icon="🔪")

# Hauptfarbe: Koralle
main_color = "#FF7F50"
# Akzentfarbe: Goldgelb
accent_color = "#FFD700"
# Hintergrundfarbe: Hellorange
background_color = "#FFE4B5"
# Textfarbe: Braun
text_color = "#8B4513"

csv_file_name = "recipes.csv"

# Initialize an empty DataFrame
COLUMNS = ['id', 'rezeptname', 'zutaten', 'anleitung', 'link', 'imageurl', 'vegetarisch', 'vegan','dessert','hauptgang','apero','fleisch', 'zmorge']
categories_dict = {"vegetarisch": "Vegetarisch", "vegan": "Vegan", "dessert": "Dessert", "hauptgang": "Hauptgang",
                   "apero": "Apéro / Vorspeise", "fleisch": "Fleisch", "zmorge": "Zmorge"}
categories_keys = ["vegetarisch", "vegan", "dessert", "hauptgang", "apero", "fleisch", "zmorge"]

# recipes = pd.DataFrame(columns=COLUMNS)


# CSS-Stil für die Anpassung der Farben
custom_css = f"""
    body {{
        color: {text_color};
        background-color: {background_color};
    }}
    .stTextInput, .stTextArea {{
        /* background-color: {background_color}; */
        border-color: {accent_color};
    }}

    .stSelectbox, .stMultiSelect {{
        background-color: {background_color};
    }}
    .stSelectbox::selection, .stMultiSelect::selection {{
        background-color: {main_color};
        color: white;
    }}
    .stSlider, .stSlider .horizontal {{
        color: {main_color};
    }}
"""

# Anwenden des benutzerdefinierten CSS-Stils
st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# Initialisierung der GithubContents-Instanz
def init_github():
    """Initialize the GithubContents object."""
    if 'github' not in st.session_state:
        st.session_state.github = GithubContents(
            st.secrets["github"]["owner"],
            st.secrets["github"]["repo"],
            st.secrets["github"]["token"],
            st.secrets["github"]["branch"])

def zeilenschaltung_zu_html(text):
    test_string = f'{text}'
    test_string = test_string.replace('\n', '<br>')
    test_string = test_string.replace('\r', '')
    test_string = test_string.replace('\t', '&emsp;')
    test_string = test_string.replace(',', '&#44;')
    return str(test_string)

def html_zu_zeilenschaltung(text):
    test_string = f'{text}'
    test_string = test_string.replace('<br>', '\n')
    test_string = test_string.replace('&#44;', ',')
    return test_string

# Function to highlight search text in a string
def highlight_text(text, search_text):
    # Use re.sub to replace the search string with the highlighted version
    highlighted_text = re.sub(f'({search_text})', r'<span style="color:red">\1</span>', text, flags=re.IGNORECASE)
    return highlighted_text

def delete_recipe(row):
    init_dataframe_git()  # make sure the DataFrame is up to date

    recipes = st.session_state.recipes
    recipes = recipes[recipes['id'] != row['id']]

    save_recipes_to_git(recipes, f"Rezept {row['rezeptname']} wurde gelöscht.")


def save_recipes_to_git(recipes,message):
    init_dataframe_git()  # make sure the DataFrame is up to date

    # Save the updated dataframe to the CSV file
    # recipes.to_csv(csv_file_name, index=False)
    st.session_state.recipes = recipes

    # Save the updated DataFrame to GitHub
    st.session_state.github.write_df(csv_file_name, recipes, message)

def init_dataframe_local():
    # Load the CSV file
    recipes = pd.read_csv('recipes.csv')
    st.session_state.recipes = recipes

def init_dataframe_git():
    """Initialize or load the dataframe."""
    if 'recipes' not in st.session_state:
        if st.session_state.github.file_exists(csv_file_name):
            recipes = st.session_state.github.read_df(csv_file_name)

            # Replace <br> with \n in the 'ingredients' column
            st.session_state.recipes = recipes
        else:
            st.session_state.recipes = pd.DataFrame(columns=COLUMNS)

def image_to_byte_array(image: Image) -> bytes:
  # BytesIO is a file-like buffer stored in memory
  imgByteArr = io.BytesIO()
  # image.save expects a file-like as a argument
  image.save(imgByteArr, format=image.format)
  # Turn the BytesIO object back into a bytes object
  imgByteArr = imgByteArr.getvalue()
  return imgByteArr

# Initialisierung der GithubContents-Instanz
def init_github():
    """Initialize the GithubContents object."""
    if 'github' not in st.session_state:
        st.session_state.github = GithubContents(
            st.secrets["github"]["owner"],
            st.secrets["github"]["repo"],
            st.secrets["github"]["token"])

def update_mycontacts_table(new_recipe):
    """Update the DataFrame and Github with a new entry."""
    init_dataframe_git()  # make sure the DataFrame is up to date

    recipes = st.session_state.recipes
    a_new_recipe = pd.DataFrame([new_recipe])
    recipes = pd.concat([recipes, a_new_recipe], ignore_index=True)
    st.session_state.recipes = recipes

    # Save the updated DataFrame to GitHub
    name = new_recipe['rezeptname']
    msg = f"Add recipe '{name}' to the file {csv_file_name}"
    st.session_state.github.write_df(csv_file_name, recipes, msg)

def sidebar():
    # Create a text input for the search term
    if st.sidebar.button(f"Was Koche ich heute"):
        recipes = st.session_state.recipes
        index = int(random.randrange(len(recipes)))
        rezeptname = recipes['rezeptname'][index]
        st.session_state.search_term = html_zu_zeilenschaltung(rezeptname)
        
def sidebar():
    # Initialize session state variables if they don't exist
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ""

    if 'selected_categories' not in st.session_state:
        st.session_state.selected_categories = [False] * len(categories_keys)

    # Create a text input for the search term
    if st.sidebar.button(f"Was koche ich heute?"):
        recipes = st.session_state.recipes
        index = int(random.randrange(len(recipes)))
        rezeptname = recipes['rezeptname'][index]
      #set search term only if rezeptname is defined
        if rezeptname:
            st.session_state.search_term = html_zu_zeilenschaltung(rezeptname)    
    st.sidebar.title("Suchen")
    st.session_state.search_term = st.sidebar.text_input(" ",value=st.session_state.search_term)

    st.sidebar.text(" ")
    # Sidebar für Filteroptionen
    st.sidebar.title("Filtern nach Kategorien")
    st.sidebar.text(" ")
    selected_categories = []

    for category_key in categories_keys:
        selected_categories.append(st.sidebar.checkbox(categories_dict[category_key], key=category_key))

    st.session_state.selected_categories = selected_categories
    #if st.sidebar.button("Filter anwenden"):
    #    show_filtered_recipes()

    st.sidebar.title("Neues Rezept")

    # Define the button behavior
    def toggle_new_recipe_form():
        st.session_state['show_new_recipe_form'] = not st.session_state['show_new_recipe_form']

    # Display different content based on the button state
    if st.session_state['show_new_recipe_form']:
        showNewRecipeFormTitle = 'Alle Rezepte Anzeigen'
    else:
        showNewRecipeFormTitle = 'Rezept hochladen'

    # Create a sidebar button
    if st.sidebar.button(showNewRecipeFormTitle, on_click=toggle_new_recipe_form):
        pass

def categories_for_recipe(row):
    categories_string = ''

    for category_key in categories_keys:
        if row[category_key] == True:
            if categories_string != '':
                categories_string += f', {categories_dict[category_key]}'
            else:
                categories_string += f'{categories_dict[category_key]}'

    return categories_string

def show_filtered_recipes():
    recipes = st.session_state.recipes # st.session_state['recipes']
    search_term = zeilenschaltung_zu_html(st.session_state.search_term)
    selected_categories = st.session_state.selected_categories
    # Filter the dataframe based on the search term
    filtered_recipes_filtered = recipes[recipes['rezeptname'].str.contains(search_term, case=False) | recipes['zutaten'].str.contains(search_term, case=False) | recipes['anleitung'].str.contains(search_term, case=False)]

    # idee wenn eine category angeklickt wurde und True ist, dann filtere alle Rezepte die bei dieser Kategory True sind
    #   if selected_categories[0] == True:
    #       filtered_recipes_filtered = filtered_recipes_filtered[(filtered_recipes_filtered['vegetarisch'])]

    # gleiche idee nur über alle Kategorien
    for index, value in enumerate(selected_categories):
        if value == True:
            category_key = categories_keys[index]
            filtered_recipes_filtered = filtered_recipes_filtered[(filtered_recipes_filtered[category_key])]

    filtered_recipes = filtered_recipes_filtered
    # st.write(f"Gefilterte Kategorien: {st.session_state.selected_categories}")

    if filtered_recipes.empty == False:
        # Set up pagination
        items_per_page = 3
        num_pages = len(filtered_recipes) // items_per_page
        if len(filtered_recipes) % items_per_page:
            num_pages += 1  # Add one page if there are any remaining items
        page_num = st.number_input('Page number', min_value=1, max_value=num_pages, value=1, step=1)

        # Display the items for the selected page
        start = (page_num - 1) * items_per_page
        end = start + items_per_page
        for index, row in filtered_recipes.iloc[start:end].iterrows():
            title = row['rezeptname']
            # Format the input string
            ingredient = zeilenschaltung_zu_html(row['zutaten'])
            instructions = zeilenschaltung_zu_html(row['anleitung'])
            
            if search_term:
                title = highlight_text(title, search_term)
                ingredient = highlight_text(ingredient, search_term)
                instructions = highlight_text(instructions, search_term)

            title = re.sub(f'({title})', r'<span style="font-weight:600">\1</span>', title, flags=re.IGNORECASE)

        # Display the highlighted text in Streamlit
            st.markdown(title, unsafe_allow_html=True)

            st.write("Kategorien: ", categories_for_recipe(row))

            st.markdown(f"Zutaten: {ingredient}", unsafe_allow_html=True)
            st.markdown(f"Anleitung: {instructions}", unsafe_allow_html=True)

            st.write("Link ", row['link'])
            # st.write("imageurl: ", row['imageurl'])
            if pd.isna(row['imageurl']):
                st.write(f"Rezept '{row['rezeptname']}' hat kein Bild.")
            else:
                if os.path.isfile(row['imageurl']):
                    # file exists
                    st.image(row['imageurl'])
                else:
                    #file not local yet get it from git
                    if st.session_state.github.file_exists(row['imageurl']):
                        image_bytes, _ = st.session_state.github.read(row['imageurl'])
                        #image = Image.open(io.BytesIO(image_bytes))
                        #image.save(row['imageurl'], 'wb')
                        st.image(image_bytes)
                    else:
                        st.write(f"Rezept '{row['rezeptname']}' hat kein Bild.")
            # Create a button for each row to allow it to be deleted
            if st.button(f"Rezept '{row['rezeptname']}' löschen"):
                delete_recipe(row)
                st.success(f"Rezept '{row['rezeptname']}' wurde gelöscht.")
    else:
        st.write('Rezept nicht gefunden.')

def new_recipe_form():
    st.title("Neues Rezept erstellen")
    # Hier können Nutzer ein neues Rezept eingeben
    # Create a form
    with st.form(key='recipe_form'):
        title = st.text_input('Rezeptname')

        selected_categories = []
        for category_key in categories_keys:
            selected_categories.append(st.checkbox(categories_dict[category_key], key=f'recipe_form_{category_key}'))

        ingredient = st.text_area(label='Zutaten')
        instructions = st.text_area(label='Anleitung')
        link = st.text_input('Link')
        # imageurl = st.text_input('Bildlink')
        uploaded_file = st.file_uploader("Bild wählen...", type=["png", "jpg", "webp"])
         # Create directory if it doesn't exist
         
        os.makedirs('images', exist_ok=True)
        submit_button = st.form_submit_button(label='Rezept speichern')

    # If the form is submitted, add the new recipe to the DataFrame
    if submit_button:
        if title and ingredient and instructions and link:
            recipes = st.session_state.recipes

            # Get the last item of the dataframe
            last_item = recipes.tail(1)
            newid = last_item['id'].values[0].astype(int) + 1
            ingredient = zeilenschaltung_zu_html(ingredient)
            instructions = zeilenschaltung_zu_html(instructions)

            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                # To save the uploaded image locally
                with open(os.path.join('images', uploaded_file.name), 'wb') as file:
                    file.write(uploaded_file.getvalue())

                # To save the image to git
                imageurlGit = f"images/{uploaded_file.name}"
                msg = f"Add image of recipe '{title}'"
                image_bytes = image_to_byte_array(image)
                st.session_state.github.write(imageurlGit, image_bytes, commit_message=msg)
                imageurl = f"images/{uploaded_file.name}"
            else:
                imageurl = ''

            new_data = {'id': newid, 'rezeptname': title, 'zutaten': ingredient, 'anleitung': instructions,
                        'link': link, 'imageurl': imageurl}

            # Add categories to dataset
            for index, value in enumerate(selected_categories):
                category_key = categories_keys[index]
                new_data[category_key] = value

            update_mycontacts_table(new_data)
            st.success(f"Rezept '{title}' erfolgreich gespeichert!")

            # Todo Zurücksetzen des Session States für das neue Rezept
            title = ''
            ingredient = ''
            instructions = ''
            link = ''
            imageurl = ''
            # st.session_state.new_recipe = {"title": "", "ingredients": "", "instructions": "", "link": ""}
        else:
            st.error("Bitte füllen Sie alle Felder aus.")

# Logo gemäss https://stackoverflow.com/questions/73251012/put-logo-and-title-above-on-top-of-page-navigation-in-sidebar-of-streamlit-multi 
# You can always call this function where ever you want


def display_logo(logo_path, width=150, height=100, caption = "", in_sidebar=False):
    #base_path = os.path.dirname(_file_)  # Basispfad für relative Pfade
    #logo_path = os.path.join(base_path, "Logo.png")  # Pfad zur Logo-Datei
    logo = Image.open(logo_path)
    resized_logo = logo.resize((width, height))
    if in_sidebar:
        # Anzeigen des Logos in der Sidebar
        st.sidebar.image(logo_path, width=100)  # Anpassung der Breite nach Bedarf
    else:
        # Anzeigen des Logos im Hauptbereich
        col1, col2, col3 = st.columns([120,2,1])
        with col3:
            st.image(logo_path, width=150, caption=caption)

# Main function
def main():
    # Initialisierung des Session States für Github
    init_github()

    # Initialisierung des Session States für DataFrame
    # init_dataframe_local()
    # Initialisierung des Session States für DataFrame
    init_dataframe_git()

    # Initialize session state if it doesn't exist
    if 'show_new_recipe_form' not in st.session_state:
        st.session_state['show_new_recipe_form'] = False

    display_logo("ShaRecipe_Logo.png", 150, 100, '', in_sidebar=False)

    sidebar()

    if st.session_state['show_new_recipe_form']:
        new_recipe_form()
    else:
        show_filtered_recipes()


if __name__ == "__main__":
    main()
