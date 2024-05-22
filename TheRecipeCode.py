import pandas as pd
import streamlit as st
from PIL import Image
import numpy as np
import os
import io
import re
import random
from github_contents import GithubContents  # Stellen Sie sicher, dass die Klasse definiert ist

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

# Function to highlight search text in a string
def highlight_text(text, search_text):
    # Use re.sub to replace the search string with the highlighted version
    highlighted_text = re.sub(f'({search_text})', r'<span style="color:red">\\1</span>', text, flags=re.IGNORECASE)
    return highlighted_text

def delete_recipe(row):
    init_dataframe_git()  # make sure the DataFrame is up to date

    recipes = st.session_state.recipes
    recipes = recipes[recipes['id'] != row['id']]

    save_recipes_to_git(recipes, f"Rezept {row['rezeptname']} wurde gelöscht.")

def save_recipes_to_git(recipes, message):
    init_dataframe_git()  # make sure the DataFrame is up to date

    # Save the updated dataframe to the CSV file
    st.session_state.recipes = recipes

    # Save the updated DataFrame to GitHub
    st.session_state.github.write_df(csv_file_name, recipes, message)

def init_dataframe_local():
    # Load the CSV file
    recipes = pd.read_csv('recipes.csv')
    recipes['zutaten'] = recipes['zutaten'].str.replace('<br>', '\n')
    recipes['anleitung'] = recipes['anleitung'].str.replace('<br>', '\n')
    st.session_state.recipes = recipes

def init_dataframe_git():
    """Initialize or load the dataframe."""
    if 'recipes' not in st.session_state:
        if st.session_state.github.file_exists(csv_file_name):
            recipes = st.session_state.github.read_df(csv_file_name)

            # Replace <br> with \n in the 'ingredients' column
            recipes['zutaten'] = recipes['zutaten'].str.replace('<br>', '\n')
            recipes['anleitung'] = recipes['anleitung'].str.replace('<br>', '\n')
            st.session_state.recipes = recipes
        else:
            st.session_state.recipes = pd.DataFrame(columns=COLUMNS)

def image_to_byte_array(image: Image) -> bytes:
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

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
    st.sidebar.title("Suchen")
    st.session_state.search_term = st.sidebar.text_input(" ")

    st.sidebar.text(" ")
    st.sidebar.title("Filtern nach Kategorien")
    st.sidebar.text(" ")
    selected_categories = []

    for category_key in categories_keys:
        selected_categories.append(st.sidebar.checkbox(categories_dict[category_key], key=category_key))

    st.session_state.selected_categories = selected_categories

    st.sidebar.title("Neues Rezept")

    if st.sidebar.button('Rezept hochladen'):
        st.session_state['showNewRecipeForm'] = True

    if st.sidebar.button('Alle Rezepte anzeigen'):
        st.session_state['showNewRecipeForm'] = False

def categories_for_recipe(row):
    categories_string = ''

    for category_key in categories_keys:
        if row[category_key]:
            if categories_string:
                categories_string += f', {categories_dict[category_key]}'
            else:
                categories_string += f'{categories_dict[category_key]}'

    return categories_string

def show_filtered_recipes():
    recipes = st.session_state.recipes
    search_term = st.session_state.search_term
    selected_categories = st.session_state.selected_categories
    filtered_recipes_filtered = recipes[
        recipes['rezeptname'].str.contains(search_term, case=False) |
        recipes['zutaten'].str.contains(search_term, case=False) |
        recipes['anleitung'].str.contains(search_term, case=False)
    ]

    for index, value in enumerate(selected_categories):
        if value:
            category_key = categories_keys[index]
            filtered_recipes_filtered = filtered_recipes_filtered[filtered_recipes_filtered[category_key]]

    filtered_recipes = filtered_recipes_filtered

    if not filtered_recipes.empty:
        items_per_page = 3
        num_pages = len(filtered_recipes) // items_per_page
        if len(filtered_recipes) % items_per_page:
            num_pages += 1
        page_num = st.number_input('Page number', min_value=1, max_value=num_pages, value=1, step=1)

        start = (page_num - 1) * items_per_page
        end = start + items_per_page
        for index, row in filtered_recipes.iloc[start:end].iterrows():
            title = row['rezeptname']
            ingredient = row['zutaten']
            instructions = row['anleitung']

            if search_term:
                title = highlight_text(title, search_term)
                ingredient = highlight_text(ingredient, search_term)
                instructions = highlight_text(instructions, search_term)

            title = re.sub(f'({title})', r'<span style="font-weight:600">\\1</span>', title, flags=re.IGNORECASE)

        # Display the highlighted text in Streamlit
            st.markdown(title, unsafe_allow_html=True)

            st.write("Kategorien: ", categories_for_recipe(row))

            st.markdown(f"Zutaten: {ingredient}", unsafe_allow_html=True)
            st.markdown(f"Anleitung: {instructions}", unsafe_allow_html=True)

            st.write("Link ", row['link'])
            if pd.isna(row['imageurl']):
                st.write(f"Rezept '{row['rezeptname']}' hat kein Bild.")
            else:
                if os.path.isfile(row['imageurl']):
                    st.image(row['imageurl'])
                else:
                    if st.session_state.github.file_exists(row['imageurl']):
                        image_bytes, _ = st.session_state.github.read(row['imageurl'])
                        st.image(image_bytes)
                    else:
                        st.write(f"Rezept '{row['rezeptname']}' hat kein Bild.")
            if st.button(f"Rezept '{row['rezeptname']}' löschen"):
                delete_recipe(row)
                st.success(f"Rezept '{row['rezeptname']}' wurde gelöscht.")
    else:
        st.write('Rezept nicht gefunden.')

def new_recipe_form():
    st.title("Neues Rezept erstellen")
    with st.form(key='recipe_form'):
        title = st.text_input('Rezeptname')

        # Upload image
        uploaded_file = st.file_uploader("Bild hochladen", type=["jpg", "jpeg", "png"])

        # Check if the file is uploaded
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            image_bytes = image_to_byte_array(image)

            # Generate a unique filename for the uploaded image
            image_filename = f"images/{random.randint(1000, 9999)}_{uploaded_file.name}"

        ingredients = st.text_area('Zutaten', height=100)
        instructions = st.text_area('Anleitung', height=200)
        link = st.text_input('Link', '')
        categories = st.multiselect('Kategorien', list(categories_dict.values()))

        categories_dict_reverse = {v: k for k, v in categories_dict.items()}
        categories_selected = {k: (categories_dict_reverse[k] in categories) for k in categories_dict.keys()}

        if st.form_submit_button('Rezept speichern'):
            new_recipe = {
                'id': random.randint(1000, 9999),
                'rezeptname': title,
                'zutaten': ingredients.replace('\n', '<br>'),
                'anleitung': instructions.replace('\n', '<br>'),
                'link': link,
                'imageurl': image_filename if uploaded_file else None,
                **categories_selected
            }

            # Save the new recipe to the GitHub
            update_mycontacts_table(new_recipe)

            # Save the image to the GitHub repository if uploaded
            if uploaded_file is not None:
                st.session_state.github.write(image_filename, image_bytes, f"Upload image for recipe '{title}'")

            st.success('Rezept wurde gespeichert!')

def main():
    init_github()
    init_dataframe_git()
    sidebar()

    if st.session_state.get('showNewRecipeForm', False):
        new_recipe_form()
    else:
        show_filtered_recipes()

if __name__ == "__main__":
    main()
