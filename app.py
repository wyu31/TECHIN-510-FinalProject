import streamlit as st
import base64
from st_clickable_images import clickable_images
import streamlit.components.v1 as components
from streamlit_float import *
from db import get_group_ids, get_group_member_ids, add_expense


import os
import pandas as pd
import random
import openai
import sqlite3
import json
import psycopg2
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from openai import OpenAI

# Page Format Setting
st.set_page_config(page_title="OttyMool", page_icon="🦦", layout="centered")

def encode_image(image_path):
    with open(image_path, "rb") as file:
        bg_image = file.read()
    return base64.b64encode(bg_image).decode()

def add_custom_css():
    with open("style.css", "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def add_bg_from_file(image_path):
    bg_image_base64 = encode_image(image_path)
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bg_image_base64}");
            background-size: cover;
        }}
        </style>
        """, unsafe_allow_html=True)

# Page 1 - Home Page
def select_or_create_group():
    st.markdown("<div class='custom-heading'>Choose a Group to Manage Recording Expenses</div>", unsafe_allow_html=True)
    if st.button("Create a new group"):
        st.session_state.page = 'create_group'
        st.experimental_rerun()

    # Buttons that look different from the default button in css
    def ChangeButtonColour(widget_label, font_color, background_color='transparent', border_style=None):
        # Use 'let' for block scope in modern JavaScript
        # Check for elements' existence before attempting to style them
        # Use 'textContent' for better compatibility across browsers
        border_style_js = f"elements[i].style.border = '{border_style}';" if border_style else ""
        htmlstr = f"""
            <script>
                document.addEventListener('DOMContentLoaded', (event) => {{
                    let elements = window.parent.document.querySelectorAll('button');
                    for (let i = 0; i < elements.length; ++i) {{
                        if (elements[i].textContent.trim() == '{widget_label}') {{
                            elements[i].style.color ='{font_color}';
                            elements[i].style.background = '{background_color}';
                            {border_style_js}
                        }}
                    }}
                }});
            </script>
        """
        components.html(htmlstr, height=0, width=0)

    ChangeButtonColour('Join a new group', 'white', '#b4aedf')
    
    if st.button("Join a new group", key ='b2'):
        st.session_state.page = 'join_group'
        st.experimental_rerun()

    ChangeButtonColour('View existing groups', '#c89dc6', 'white', '2px solid #c89dc6') # Now includes border style

    if st.button("View existing groups", key ='b3'):
        st.session_state.page = 'show_group'
        st.experimental_rerun()

# Page 2 - Create Group & Participants in Json
def create_group(group_name=""):
    # Check if group_name is not empty and not already in the list of groups
    if group_name:
        if 'groups' not in st.session_state:
            st.session_state.groups = []
        if group_name not in st.session_state.groups:
            st.session_state.groups.append(group_name)
            st.success(f"Group '{group_name}' created!")
            # Optionally, reset the group name input field here if desired
            st.session_state.new_group_name = ""
            return True  # Indicate successful creation
        else:
            st.error(f"Group '{group_name}' already exists.")
            return False  # Indicate failure due to existing name
    else:
        # If no group name is provided, do not attempt to create a group.
        st.warning("Please enter a group name.")
        return False  # Indicate failure due to no name provided


# Function to save group name and participants to JSON, and generate a random 4-digit group ID
def save_data_to_json(group_name, participants):
    filename = 'expense_data.json'
    data = []

    # Check if the JSON file exists and read its content
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        existing_ids = {item['Group ID'] for item in data}
    else:
        existing_ids = set()

    # Generate a new unique group_id
    group_id = None
    while group_id is None or group_id in existing_ids:
        group_id = '{:04d}'.format(random.randint(0, 9999))

    # Now we are sure group_id is set, proceed to use it
    new_data = {
        'Group ID': group_id,
        'Group Name': group_name,
        'Participants': participants,
    }
    data.append(new_data)

    # Write updated data to JSON file
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    
    return group_id

def create_group_page():
# Insert custom CSS to reduce black space at the top
    st.markdown(
        """
            <style>
                .appview-container .main .block-container {{
                    padding-top: {padding_top}rem;
                    padding-bottom: {padding_bottom}rem;
                    }}

            </style>""".format(
            padding_top=1, padding_bottom=1
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<div class='custom-subheading'>Add Group and Member</div>", unsafe_allow_html=True)
    st.markdown('<div class="white-block"></div>', unsafe_allow_html=True)

    # Define the back button icon
    back_icon_path = "icon/Back.png"
    finish_icon_path = "icon/Finish.png"

    back_icon = encode_image(back_icon_path)
    finish_icon = encode_image(finish_icon_path)

    # Prepare the images for display
    back_image = f"data:image/png;base64,{back_icon}"
    finish_image = f"data:image/png;base64,{finish_icon}"

    col1, col2 = st.columns([1,1])
    
    with col1:
        clicked = clickable_images(
            [back_image],
            titles=["Back"],
            div_style={
                "display": "flex",
                "justify-content": "left",
                "flex-wrap": "wrap",
                "max-width": "100%",  # Prevents the flex container from taking full width, adjust as necessary
                "margin-top": "0px",  # Negative value to move up
            },
            img_style={
                "cursor": "pointer",
                "width": "30px",
                "height": "30px",
                "margin": "0px",  # Adjusted for compactness
            }
        )
    
    float_init()
    # Column 2: Finish button, adjusted to not cover subtitle or other content
    with col2:
        col2.float(css="position: fixed; right: -50px; top: 12px; z-index: 1")
        # Adjust the 'top' value as needed to ensure it does not overlap with your subtitle
        clicked2 = clickable_images(
            [finish_image],  # Assuming finish_image is defined elsewhere
            titles=["Finish"],
            div_style={
                "display": "flex",
                "justify-content": "right",  # Aligns the items to the left within the container
                "flex-wrap": "wrap",
                "max-width": "100%",  # Limits the container's max width to reduce blank space
                "height": "25px",  # Limits the container's max width to reduce blank space

            },
            img_style={
                "margin": "70px",  # Reduces margin around the image to minimize blank space
                "width": "50px",  # Image width
                "height": "20px",  # Image height
            },
        )

    if clicked == 0:
        st.session_state.page = 'home'
        st.experimental_rerun()
    
    if clicked2 == 0:
        st.session_state.page = 'show_group'
        st.experimental_rerun()

    st.text("")
    
    group_name = st.text_input("Add a Group Name", value="", key='new_group_name')
    def handle_add_group():
        if 'groups' not in st.session_state:
            st.session_state.groups = []
        if group_name and group_name not in st.session_state.groups:
            st.session_state.groups.append(group_name)
            st.success(f"Group '{group_name}' created!")
            if 'participants' not in st.session_state:
                st.session_state.participants = []
            else:
                st.session_state.participants.clear()
        elif group_name in st.session_state.groups:
            st.error(f"Group '{group_name}' already exists.")
        else:
            st.warning("Please enter a group name.")

    if st.button("Add a Group"):
        handle_add_group()

    # Use a custom HTML block with inline styling for larger space
    st.markdown("""
        <div style='margin-bottom: 60px;'><!-- Space Block --></div>
    """, unsafe_allow_html=True)

    # Add Participant Name
    new_participant = st.text_input("Add Participant's Name", key='new_participant')

    if st.button("Add Participant", key='add_participant') and new_participant:
        if new_participant not in st.session_state['participants']:
            st.session_state['participants'].append(new_participant)
            st.success(f"Participant '{new_participant}' added.")            
        else:
            st.error("Name already exists. Please enter another name.")

    # Display current participants with an option to delete
    if 'participants' in st.session_state:
        for idx, participant in enumerate(st.session_state['participants']):
            st.markdown("---")  # Separation line for clarity
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(participant)
            with col2:
                if st.button('Delete', key=f'delete_{idx}'):
                    st.session_state['participants'].remove(participant)
    
    # Use a custom HTML block with inline styling for larger space
    st.markdown("""
        <div style='margin-bottom: 10px;'><!-- Space Block --></div>
    """, unsafe_allow_html=True)

    # Buttons that look different from the default button in css
    def ChangeButtonColour(widget_label, font_color, background_color='transparent', border_style=None):
        # Use 'let' for block scope in modern JavaScript
        # Check for elements' existence before attempting to style them
        # Use 'textContent' for better compatibility across browsers
        border_style_js = f"elements[i].style.border = '{border_style}';" if border_style else ""
        htmlstr = f"""
            <script>
                document.addEventListener('DOMContentLoaded', (event) => {{
                    let elements = window.parent.document.querySelectorAll('button');
                    for (let i = 0; i < elements.length; ++i) {{
                        if (elements[i].textContent.trim() == '{widget_label}') {{
                            elements[i].style.color ='{font_color}';
                            elements[i].style.background = '{background_color}';
                            {border_style_js}
                        }}
                    }}
                }});
            </script>
        """
        components.html(htmlstr, height=0, width=0)

    ChangeButtonColour('Make Sure', '#c89dc6', 'white', '2px solid #c89dc6') # Now includes border style
    
    # Use a custom HTML block with inline styling for larger space
    st.markdown("""
        <div style='margin-bottom: 10px;'><!-- Space Block --></div>
    """, unsafe_allow_html=True)

# Ensuring Button
    if st.button("Make Sure", key='finish_adding'):
        if group_name and 'participants' in st.session_state and st.session_state['participants']:
            # This block remains unchanged, save the data to JSON
            if group_name in st.session_state.groups:
                group_id = save_data_to_json(group_name, st.session_state['participants'])
                # After saving, display group info instead of navigating away
                st.success(f"Group '{group_name}' saved with ID {group_id}.")
                # Display the saved group information
                st.markdown(f"**Group ID:** {group_id}")
                st.markdown(f"**Group Name:** {group_name}")
                st.markdown("**Participants:**")
                for participant in st.session_state['participants']:
                    st.markdown(f"- {participant}")
                # Optionally clear session state here if you don't plan to use it further
                st.session_state['groups'].remove(group_name)  # Remove the group if not needed further
                del st.session_state['participants']  # Clear participants
        else:
            st.error("Please add at least one participant and ensure the group has a name.")

# Page 3 - Show Groups
def show_group_page():

# Insert custom CSS to reduce black space at the top
    st.markdown(
        """
            <style>
                .appview-container .main .block-container {{
                    padding-top: {padding_top}rem;
                    padding-bottom: {padding_bottom}rem;
                    }}

            </style>""".format(
            padding_top=1, padding_bottom=1
        ),
        unsafe_allow_html=True,
    )
    st.markdown("<div class='custom-subheading'>View Existing Groups</div>", unsafe_allow_html=True)
    st.markdown('<div class="white-block"></div>', unsafe_allow_html=True)

    back_icon_path = "icon/Back.png"  # Make sure the path is correct
    back_icon = encode_image(back_icon_path)
    back_image = f"data:image/png;base64,{back_icon}"

    # Back icon column
    col1, col2 = st.columns([1, 1])  # Adjust the ratio to your layout
    with col1:
        if clickable_images(
            [back_image],
            titles=["Back"],
            div_style={
                "display": "flex",
                "justify-content": "flex-start",
                "flex-wrap": "wrap",
                "max-width": "100%",
            },
            img_style={
                "cursor": "pointer",
                "width": "30px",
                "height": "30px",
                "margin": "0px",  # Adjusted for compactness
            },
        ) == 0:
            st.session_state.page = 'home'
            st.experimental_rerun()
    

    # Path to the JSON file with the groups data
    filename = 'expense_data.json'

    # Check if the JSON file exists and read its content
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            groups_data = json.load(file)

        # Prepare a container for deletion requests
        participant_to_delete = None
        group_to_delete = None

        # Placeholder
        for _ in range(4):  # Adjust the range for more or fewer spaces
            st.text("")

        # Iterate over each group and display its content
        for group in groups_data:
            group_id = group['Group ID']
            group_name = group['Group Name']
            participants = group['Participants']

            with st.expander(f"Group ID: {group_id} - {group_name}"):
                st.write("Participants:")
                for idx, participant in enumerate(participants):
                    # Create a unique key for each participant button using both group ID and index
                    unique_key = f"delete_participant_{group_id}_{idx}"
                    if st.button(f"Delete {participant}", key=unique_key):
                        participant_to_delete = (group_id, participant)
                
                # Add a delete group button
                delete_group_key = f"delete_group_{group_id}"
                if st.button(f"Delete Group: {group_name}", key=delete_group_key):
                    group_to_delete = group_id

        # Handle participant deletion
        if participant_to_delete:
            for group in groups_data:
                if group['Group ID'] == participant_to_delete[0]:
                    group['Participants'].remove(participant_to_delete[1])
                    break
            with open(filename, 'w') as file:
                json.dump(groups_data, file, indent=4)
            st.experimental_rerun()
        
        # Handle group deletion
        if group_to_delete:
            groups_data = [group for group in groups_data if group['Group ID'] != group_to_delete]
            with open(filename, 'w') as file:
                json.dump(groups_data, file, indent=4)
            st.experimental_rerun()

    else:
        st.error("No groups found. Please create a group first.")

    # Iterate over each group and display its content
    for group in groups_data:
        group_id = group['Group ID']
        group_name = group['Group Name']
        # Existing code for displaying group...

        # Add a button for navigating to manage expenses for the group
        if st.button(f"Manage Expenses for {group_name}", key=f"manage_{group_id}"):
            st.session_state.selected_group_id = group_id  # Set selected group ID in session state
            st.session_state.page = 'manage_expenses'  # Change page state to trigger navigation
            st.experimental_rerun()

# Page 4 - Manage Data with SQL DataBase
def manage_expenses_page():
    st.title("Manage Expenses")
    # Fetch group options from the database
    group_options = get_group_ids()
    if not group_options:
        st.warning("No groups available. Please create a group first.")
        return
    
    group_ids, group_names = zip(*group_options) if group_options else ([], [])
    selected_group_id = st.selectbox("Select Group", options=group_names, index=0 if group_options else -1)
    
    if not group_options:
        return  # Exit if there are no groups to manage expenses for

    item = st.text_input("Item")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    member_options = get_group_member_ids(selected_group_id)

    if member_options:
        member_ids, member_names = zip(*member_options)
        paid_by = st.selectbox("Who Paid?", options=member_names)
        if st.button("Add Expense"):
            add_expense(selected_group_id, item, amount, paid_by)
            st.success("Expense added successfully")
    else:
        st.warning("No members found in this group.")

# Main function
def main():
    add_custom_css()
    add_bg_from_file("gradient/home-bg.png")
    
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'groups' not in st.session_state:
        st.session_state.groups = []
    if 'participants' not in st.session_state:
        st.session_state.participants = []

    if st.session_state.page == 'home':
        select_or_create_group()
    elif st.session_state.page == 'create_group':
        create_group_page()
    elif st.session_state.page == 'show_group':
        show_group_page() 
    elif st.session_state.page == 'manage_expenses':
        manage_expenses_page()

if __name__ == "__main__":
    main()