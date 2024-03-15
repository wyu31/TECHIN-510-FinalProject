from openai import OpenAI
import openai
from dotenv import load_dotenv
import os

import streamlit as st
import base64
from st_clickable_images import clickable_images
import streamlit.components.v1 as components
from streamlit_float import *

import re
import pandas as pd
import builtins
import random
import sqlite3
import psycopg2
import json
from dotenv import load_dotenv
from collections import defaultdict
from decimal import Decimal




load_dotenv()
openai_api_key=os.getenv("OPENAI_API_KEY")

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
    st.markdown("<div class='custom-heading'>Choose a Group to Manage Group Expenses</div>", unsafe_allow_html=True)
    if st.button("Create a new group"):
        st.session_state.page = 'create_group'
        st.rerun()

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

    ChangeButtonColour('View existing groups', 'white', '#b4aedf') 
    if st.button("View existing groups", key ='b3'):
        st.session_state.page = 'show_group'
        st.rerun()

    ChangeButtonColour('Chat with AI accountant', '#c89dc6', 'white', '2px solid #c89dc6') # Now includes border style
    if st.button("Chat with AI accountant", key ='b2'):
        st.session_state.page = 'chat_and_process_expenses'
        st.rerun()

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
def save_data_to_individual_json(group_name, participants):
    # Create the directory if it doesn't exist
    directory = "individual_group_info"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Generate unique ID for the group and prepare the filename for individual group file
    filename = os.path.join(directory, f"{group_name}_expense_data.json")
    central_filename = 'expense_data.json'  # This file maintains a list of all groups

    # Load or initialize the central data list
    if os.path.exists(central_filename):
        with open(central_filename, 'r') as file:
            central_data = json.load(file)
    else:
        central_data = []

    # Generate a unique ID for the new group
    existing_ids = {item['Group ID'] for item in central_data}
    group_id = '{:04d}'.format(random.randint(0, 9999))
    while group_id in existing_ids:
        group_id = '{:04d}'.format(random.randint(0, 9999))

    # Check if the group already exists in the central file
    if any(item['Group Name'] == group_name for item in central_data):
        st.error(f"Group '{group_name}' already exists.")
        return None

    # Prepare data for individual group file
    group_data = {
        'Group ID': group_id,
        'Group Name': group_name,
        'Participants': participants,
    }

    # Save individual group data
    with open(filename, 'w') as file:
        json.dump(group_data, file, indent=4)

    # Update the central data list
    central_data.append({'Group ID': group_id, 'Group Name': group_name, 'File': filename})

    # Save the updated central data list
    with open(central_filename, 'w') as file:
        json.dump(central_data, file, indent=4)

    st.success(f"Group '{group_name}' created with ID {group_id}.")
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

    st.markdown("<div class='custom-subheading'>New Additions</div>", unsafe_allow_html=True)
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
        st.rerun()
    
    if clicked2 == 0:
        st.session_state.page = 'show_group'
        st.rerun()

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

    # Placeholder
    for _ in range(2):  # Adjust the range for more or fewer spaces
        st.text("")

    if st.button("Add a group"):
        if handle_add_group():
            # Insert new group data into the SQL database
            add_group_to_db(group_name, st.session_state['participants'])

    # Use a custom HTML block with inline styling for larger space
    st.markdown("""
        <div style='margin-bottom: 60px;'><!-- Space Block --></div>
    """, unsafe_allow_html=True)

    # Add Participant Name
    new_participant = st.text_input("Add Participant's Name", key='new_participant')
    
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

    ChangeButtonColour('Add a participant', 'white', '#b4aedf') 
    if st.button("Add a participant", key='add_participant') and new_participant:
        if new_participant not in st.session_state['participants']:
            st.session_state['participants'].append(new_participant)
            st.success(f"Participant '{new_participant}' added.")            
        else:
            st.error("Name already exists. Please enter another name.")

    # Display current participants with an option to delete
    if 'participants' in st.session_state:
        for idx, participant in enumerate(st.session_state['participants']):
            st.markdown("---")  # Separation line for clarity
            col1, col2 = st.columns([1,1])
            with col1:
                st.write(participant)

            with col2:
                if st.button('Delete', key=f'delete_{idx}'):
                    st.session_state['participants'].remove(participant)
    

    # Placeholder
    for _ in range(3):  # Adjust the range for more or fewer spaces
        st.text("")

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

    ChangeButtonColour('Make sure', '#c89dc6', 'white', '2px solid #c89dc6') # Now includes border style
    
    # Use a custom HTML block with inline styling for larger space
    st.markdown("""
        <div style='margin-bottom: 10px;'><!-- Space Block --></div>
    """, unsafe_allow_html=True)

# Ensuring Button
    if st.button("Make sure", key='finish_adding'):
        if group_name and 'participants' in st.session_state and st.session_state['participants']:
            # This block remains unchanged, save the data to JSON
            if group_name in st.session_state.groups:
                group_id = save_data_to_individual_json(group_name, st.session_state['participants'])
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
    st.markdown("<div class='custom-subheading'>Existing Groups</div>", unsafe_allow_html=True)
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
            st.rerun()

    # Placeholder
    for _ in range(4):  # Adjust the range for more or fewer spaces
        st.text("")

    # Get all groups
    directory = "individual_group_info"
    if not os.path.exists(directory):
        os.makedirs(directory)
    group_files = os.listdir(directory)

    if not group_files:
        st.error("No groups found. Please create a group first.")
        return

    # Dropdown to select a group
    group_names = [file_name.split('_')[0] for file_name in group_files if file_name.endswith("_expense_data.json")]
    selected_group = st.selectbox('Select a group to view or edit', group_names)

    # Once a group is selected, show the participants and options
    if selected_group:
        file_path = os.path.join(directory, f"{selected_group}_expense_data.json")
        with open(file_path, 'r') as file:
            group_data = json.load(file)

        # Adjusted section: Handling group_data as a list or dictionary
        if isinstance(group_data, list):
            if group_data:  # Check if the list is not empty
                group_data = group_data[0]  # Use the first item
            else:
                st.error("No group data found in the selected file.")
                return
        
        participants = group_data.get('Participants', [])
        group_id = group_data.get('Group ID', 'Unknown ID')

        st.subheader(f"Group ID: {group_id} - {selected_group}")
        st.write("Participants:")

        # List the participants
        if participants:
            for participant in participants:
                st.markdown(f"- {participant}")
        else:
            st.write("No participants found.")

        # Dropdown for selecting a participant to delete
        selected_participant = st.selectbox("Select a participant to delete", options=[None] + participants)

        # Delete button
        if st.button("Delete selected participant") and selected_participant:
            # Remove the selected participant from the list
            participants.remove(selected_participant)
            # Update the group_data with the modified participants list
            group_data['Participants'] = participants
            # Write the updated data back to the file
            with open(file_path, 'w') as file:
                json.dump(group_data, file, indent=4)
            st.success(f"Participant {selected_participant} deleted successfully.")
            st.rerun()

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

        ChangeButtonColour(f"Delete group {selected_group}", 'white', '#b4aedf')         
        # Button to delete the group
        if st.button(f"Delete group {selected_group}", key=f"delete_group_{group_id}"):
            os.remove(file_path)  # Delete the group file
            st.success(f"Group {selected_group} deleted successfully.")
            st.rerun()  # Refresh the page to show the update
        
        ChangeButtonColour("Data visualization", '#c89dc6', 'white', '2px solid #c89dc6') # Now includes border style
        if st.button("Data visualization", key ='b6'):
            st.session_state.page = 'data_visualization'
            st.rerun()

# Page 4 - Chat with AI Account
def get_group_names():
    directory = "individual_group_info"
    if not os.path.exists(directory):
        os.makedirs(directory)
    group_files = os.listdir(directory)
    return [file.replace('_expense_data.json', '') for file in group_files]

def save_expense_to_group_file(group_name, expense_data):
    directory = "individual_group_info"
    filename = os.path.join(directory, f"{group_name}_expense_data.json")
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    try:
        data = []
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                data = json.load(file)
                if not isinstance(data, list):
                    raise ValueError(f"Data in {filename} is not a list")

        data.append(expense_data)
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
            
        st.success(f"Expense data saved to {filename} successfully.")
        
    except Exception as e:
        st.error(f"An error occurred: {e}")

def chat_and_process_expenses_page():
    st.title("🤖 Accounting Robot")
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Add a dropdown for users to choose the group
    group_names = get_group_names()  # Ensure this function is defined and returns a list of group names
    selected_group = st.selectbox("Choose your group", group_names)

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hello! Try ask me questions like: We had dinner for $90 paid by Jackie split among Jackie, Wanling, Qianna"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("e.g., We had dinner for $90 paid by Jackie split among Jackie, Wanling, Qianna):"):
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()

        client = OpenAI(api_key=openai_api_key, base_url=os.getenv("OPENAI_API_BASE"))

        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Define an accounting-specific system prompt
        accounting_prompt = {
            "role": "system",
            "content":'''
            You are an advanced accounting assistant. 
            Provide accurate, detailed, and professional financial advice.
            Also print the json format like the example:
            We had dinner for $90 paid by Jackie split among Jackie, Wanling, Qiana, 
            calculate the money owed, and analyze the money spliting for users.
            <text> Wanling, Jackie, and I went to lunch and spent 100 dollars, we want to split it equally. Jackie paid first. 
            </text> <example> { "activity": "lunch", "activity_amount": 90, "lender": "Jackie", 
            "borrower": "Wanling","Qianna", "amount": 30 } </example>'
            and output in JSON format for the dinner activity
            json_string = """
            {
                "activity": "dinner",
                "activity_amount": 90,
                "lender": "Jackie",
                "borrower": ["Wanling", "Qianna"],
                "amount": 30
            }
            """
            '''
        }
        
        # Include the accounting prompt along with user messages
        messages_with_context = [accounting_prompt] + st.session_state.messages
        
        # Call the OpenAI API with the updated session state as the prompt
        response = client.chat.completions.create(model="gpt-3.5-turbo-0125", messages=messages_with_context)
        
        # Extract the response message and append it to the session state
        msg = response.choices[0].message.content

        # Parse the response to extract JSON output
        try:
            json_output = json.loads(msg)
            if isinstance(json_output, dict):
                st.session_state.messages.append({"role": "assistant", "content": json.dumps(json_output, indent=4)})
                st.chat_message("assistant").write(json.dumps(json_output, indent=4))
                # Add box for copying JSON info
                st.text_area("Copy JSON info:", value=json.dumps(json_output, indent=4), height=200)
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Unable to generate JSON output for this request."})
                st.chat_message("assistant").write("Unable to generate JSON output for this request.")
        except json.JSONDecodeError:
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)

    # Add a text area for users to paste the JSON data
    json_input = st.text_area("Paste and check the generated JSON data here:", height=120)
    
    
    # Save button to save the pasted JSON data
    if st.button("Save JSON"):
        if not json_input.strip():  # Check if the json_input is empty or only whitespace
            st.error("No JSON data to save. Please paste the JSON data into the text area.")
            return  # Exit the function to avoid further processing

        try:
            expense_data = json.loads(json_input)  # Parse the JSON input from the text area
            save_expense_to_group_file(selected_group, expense_data)  # Call save function with parsed JSON
            st.success("Expense saved successfully.")
        except json.JSONDecodeError as e:
            st.error(f"An error occurred while parsing the JSON input: {e}")
        except Exception as e:
            st.error(f"An error occurred while saving the JSON data: {e}")

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

    ChangeButtonColour('Data visualization', 'white', '#b4aedf') 
    if st.button("Data visualization", key ='b4'):
        st.session_state.page = 'data_visualization'
        st.rerun()

    ChangeButtonColour('Go back home', '#c89dc6', 'white', '2px solid #c89dc6') # Now includes border style
    if st.button("Go back home", key ='b5'):
        st.session_state.page = 'home'
        st.rerun()

# Ensure to define save_expense_to_group_file to accept the new parsed_json parameter
def save_expense_to_group_file(group_name, expense_data):
    directory = "individual_group_info"
    filename = os.path.join(directory, f"{group_name}_expense_data.json")

    if not os.path.exists(directory):
        os.makedirs(directory)

    try:
        # Initialize data as an empty list or load existing data
        data = []

        if os.path.exists(filename):
            with open(filename, 'r') as file:
                # Load the existing data, expecting it to be a list
                file_data = json.load(file)
                if isinstance(file_data, list):
                    data = file_data  # Use existing data if it's a list
                # If the data is a dictionary, start a new list with this dictionary
                elif isinstance(file_data, dict):
                    data = [file_data]
                else:
                    raise ValueError(f"Data in {filename} is neither a list nor a dictionary")

        # Append the new expense data and save back to the file
        data.append(expense_data)
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)

        st.success(f"Expense data saved to {filename} successfully.")

    except Exception as e:
        st.error(f"An error occurred: {e}")


# Page 5 - Data Visualization Page
# Function to get group names based on the available JSON files
def get_group_names(directory="individual_group_info"):
    if not os.path.exists(directory):
        os.makedirs(directory)
        return []
    return [f for f in os.listdir(directory) if f.endswith('_expense_data.json')]

# Function to load JSON data
def load_json_data(group_name, directory="individual_group_info"):
    filename = os.path.join(directory, f"{group_name}_expense_data.json")
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        return []

# Function to get group names based on the available JSON files
def get_group_names(directory="individual_group_info"):
    if not os.path.exists(directory):
        os.makedirs(directory)
        return []
    return [f.replace('_expense_data.json', '') for f in os.listdir(directory) if f.endswith('_expense_data.json')]

# Function to load JSON data
def load_json_data(group_name, directory="individual_group_info"):
    filename = os.path.join(directory, f"{group_name}_expense_data.json")
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        return []

# Function to calculate debts
def calculate_debts(data):
    debts = defaultdict(Decimal)  # Initialize a default dictionary for debts
    activity_info = {}  # Initialize a dictionary to store activity info
    for entry in data:
        if 'activity' in entry:
            # Directly use the specified amount each borrower owes
            amount_per_borrower = Decimal(entry['amount'])
            lender = entry['lender']
            activity = entry['activity']
            for borrower in entry['borrower']:
                if borrower != lender:  # Ignore if borrower is also the lender
                    key = (borrower, lender, activity)  # Include activity in key to distinguish different activities
                    debts[key] += amount_per_borrower
                    # Store activity name in activity_info dictionary
                    activity_info[key] = activity

    # Prepare data for DataFrame
    debts_list = [
        {'Lender': key[1], 'Borrower': key[0], 'Amount': amt, 'Activity': activity_info[key]}
        for key, amt in debts.items()
    ]
    return pd.DataFrame(debts_list)

def data_visualization_page():
    st.title("📝 Expense Visualization")

    # Dropdown to select the group
    group_names = get_group_names()
    selected_group = st.selectbox("Select a group", group_names)

    if selected_group:
        # Load the data for the selected group
        data = load_json_data(selected_group)
        
        # Check if data contains any dict entries with an "activity" key
        has_expense_data = any(isinstance(entry, dict) and "activity" in entry for entry in data)
        
        if data and has_expense_data:
            # Display raw JSON data
            st.text("Raw JSON Data")
            st.json(data)

            # Calculate overall debts
            all_debts_df = calculate_debts(data)

            # Before accessing 'Lender' and 'Borrower', check if the DataFrame is empty
            if not all_debts_df.empty:
                # Get unique list of all people involved in transactions
                all_names = list(set(all_debts_df['Lender'].tolist() + all_debts_df['Borrower'].tolist()))

                selected_name = st.selectbox("Select a name to filter", ["All"] + all_names)

                # Filter debts by selected name if not "All"
                if selected_name != "All":
                    debts_df = all_debts_df[(all_debts_df['Lender'] == selected_name) | (all_debts_df['Borrower'] == selected_name)]
                else:
                    debts_df = all_debts_df

                # Display the DataFrame
                st.markdown(
                    """
                    <style>
                    .stDataFrame {width: 100%;}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.dataframe(debts_df)

                # Additional feature: Summary of amounts owed by and to the selected name
                if selected_name != "All":
                    owed_by_selected = debts_df[debts_df['Borrower'] == selected_name]['Amount'].sum()
                    owed_to_selected = debts_df[debts_df['Lender'] == selected_name]['Amount'].sum()
                    st.write(f"Total amount owed by {selected_name}: {owed_by_selected}")
                    st.write(f"Total amount owed to {selected_name}: {owed_to_selected}")
            else:
                # Show message when there's no expense data to calculate debts from
                st.error("Go Back to Add Info! The group hasn't added group expense information.")
        else:
            # Show message when the selected group has no data or no expense entries
            st.error("Go Back to Add Info! The group hasn't added group expense information.")
    else:
        st.error("No groups found. Please create a group first.")

    # Placeholder
    for _ in range(1):  # Adjust the range for more or fewer spaces
        st.text("")

    # Save button to save the pasted JSON data
    if st.button("Go back view existing groups"):
        st.session_state.page = 'show_group'
        st.rerun()

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
    
    ChangeButtonColour('Go back AI accountant', 'white', '#b4aedf') 
    if st.button("Go back AI accountant", key ='b7'):
        st.session_state.page = 'chat_and_process_expenses'
        st.rerun()

    ChangeButtonColour('Go back home', '#c89dc6', 'white', '2px solid #c89dc6') # Now includes border style
    if st.button("Go back home", key ='b8'):
        st.session_state.page = 'home'
        st.rerun()

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
    elif st.session_state.page == 'chat_and_process_expenses':
        chat_and_process_expenses_page()
    elif st.session_state.page == 'data_visualization':
        data_visualization_page()

if __name__ == "__main__":
    main()