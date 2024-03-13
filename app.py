import streamlit as st
import base64
from st_clickable_images import clickable_images
import streamlit.components.v1 as components
from streamlit_float import *


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

if 'groups' not in st.session_state:
    st.session_state.groups = []

def create_group(group_name=""):
    if group_name:
        if group_name not in st.session_state.groups:
            st.session_state.groups.append(group_name)
            st.success(f"Group '{group_name}' created!")
            # No need to navigate or rerun here since we want the success message to display
        else:
            st.error(f"Group '{group_name}' already exists.")
    else:
        # If no group name is provided, do not attempt to create a group.
        st.warning("Please enter a group name.")

# Page 1
def select_or_create_group():
    st.markdown("<div class='custom-heading'>Select your group to begin recording expenses</div>", unsafe_allow_html=True)
    if st.session_state.groups:
        st.subheader("Recent Groups")
        for group in st.session_state.groups:
            if st.button(f"Select {group}", key=f"select_{group}"):
                # Perform action for selecting a group here
                st.session_state.current_group = group

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


    ChangeButtonColour('Join a group', '#c89dc6', 'white', '2px solid #c89dc6') # Now includes border style

    if st.button("Join a group", key ='b2'):
            st.session_state.page = 'join_group'
            st.experimental_rerun()

# Page 2
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
            },
            img_style={
                "cursor": "pointer",
                "width": "30px",
                "height": "30px",
                "margin": "20px",  # Adjusted for compactness
            }
        )
    
    float_init()
    # Column 2: Finish button, adjusted to not cover subtitle or other content
    with col2:
        col2.float(css="position: fixed; right: -50px; top: 0px; z-index: 1")
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
        st.session_state.page = 'join_group'
        st.experimental_rerun()
    
    st.markdown('<div class="white-block"></div>', unsafe_allow_html=True)
    st.markdown("<div class='custom-subheading'>Create Group Name</div>", unsafe_allow_html=True)

    group_name = st.text_input("Group Name", key='new_group_name')
    if st.button("Create Group"):
        create_group(group_name)

    if group_name in st.session_state.groups:
        # Go back to home page if the group was successfully created
        st.session_state.page = 'home'
        st.experimental_rerun()

# Page 3
def join_group_page():

    st.title('_My name is_ :blue[Wanling Yu] :fish:')

# Main function
def main():
    add_custom_css()
    add_bg_from_file("gradient/home-bg.png")
    
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'groups' not in st.session_state:
        st.session_state.groups = []

    if st.session_state.page == 'home':
        select_or_create_group()
    elif st.session_state.page == 'create_group':
        create_group_page()
    elif st.session_state.page == 'join_group':
        join_group_page() 

if __name__ == "__main__":
    main()