# TECHIN-510-FinalProject
This is the repo for TECHIN-510 final Project.
Thanks to Jackie, Wanling & Qianna.

## Project Name
OttyMool🦦 

## Description
OttyMool🦦  is a comprehensive web application tailored to manage group expenses, especially for travel seamlessly. 

## Web app link:
## Youtube link: 

# Problem Statement
The main problem GroupSpend AI addresses is the complexity of managing group expenses, especially during travel. Traditional methods of tracking shared expenses are often cumbersome and prone to errors, leading to potential conflicts among group members. GroupSpend AI aims to simplify this process by providing a platform where expenses can be entered in human language, visualized dynamically, and summarized in detailed reports.

## Technologies Used 
Streamlit for web app interface
Flask Backend with OpenAI Integration
Data Visualization
PostgreSQL

## How to Run
1. Ensure Python and pip are installed on your system.
2. Clone the repository to your local machine.
3. Navigate to the project directory
4. Run the commands below in the terminal if you want to run in a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```
5. Finish the initial settings:
```bash
pip install -r requirements.txt
cp .env.sample .env
Change the .env file to match your environment
```
6. Run the commond in the terminal below to start the Streamlit app locally.
```bash
streamlit run app.py
```

## Reflections
### General Experience & Challenges
Learning Experience
Natural Language Processing (NLP): Implementing OpenAI's API to process and structure expense entries in conversational language.
Web Development: Using Streamlit and Flask to create a user-friendly interface and a robust backend.
Data Visualization: Designing dynamic visualizations to represent the fund flow situation among group members.
Database Management: Utilizing PostgreSQL to store and manage data related to team memberships, trip details, and financial transactions.

Challenges Faced
Accuracy of NLP: Ensuring that the natural language processing accurately interprets and structures the expense entries.
Data Security: Safeguarding sensitive financial information and user data.
User Interface Design: Creating an intuitive and responsive interface that accommodates various user interactions.
Scalability: Designing the system to handle a growing number of users and transactions efficiently.
In order to define richer and free visual effects, we use CSS, but CSS is not so formal and stable compared to the basic components in stremlit, and it requires multiple debugging to achieve the ideal effect.

### Detailed New Takeaways
1. ```st.experimental_rerun```  
2. ```from st_clickable_images import clickable_images```  
3. ```import streamlit.components.v1 as components```  
4. ```from streamlit_float import *```  
