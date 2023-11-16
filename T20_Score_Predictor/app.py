import streamlit as st
import pickle
import pandas as pd
from PIL import Image

# Load the pre-trained model
pipe = pickle.load(open('Dataset_level1.pkl', 'rb'))

# Define teams and cities
teams = ['Australia', 'India', 'Bangladesh', 'New Zealand', 'South Africa', 'England', 'West Indies', 'Afghanistan', 'Pakistan', 'Sri Lanka']
cities = ['Colombo', 'Mirpur', 'Johannesburg', 'Dubai', 'Auckland', 'Cape Town', 'London', 'Pallekele', 'Barbados', 'Sydney', 'Melbourne', 'Durban', 'St Lucia', 'Wellington', 'Lauderhill', 'Hamilton', 'Centurion', 'Manchester', 'Abu Dhabi', 'Mumbai', 'Nottingham', 'Southampton', 'Mount Maunganui', 'Chittagong', 'Kolkata', 'Lahore', 'Delhi', 'Nagpur', 'Chandigarh', 'Adelaide', 'Bangalore', 'St Kitts', 'Cardiff', 'Christchurch', 'Trinidad']

# Set page title and icon
st.set_page_config(page_title='T20 World Cup Score Predictor', page_icon=':cricket_game:')

# Load images
image2 = Image.open("img2.jpg")

# Set the layout with a title and image
st.title('ICC Men T20 World Cup Score Predictor')
st.image(image2, caption='T20 World Cup', use_column_width=True)

# Create three columns for input
col1, col2, col3 = st.columns(3)

# Select batting and bowling teams
with col1:
    batting_team = st.selectbox('Select Batting Team', sorted(teams))

with col2:
    bowling_team = st.selectbox('Select Bowling Team', sorted(teams))

# Select city
with col3:
    city = st.selectbox('Select City', sorted(cities))

# Create three columns for numerical input
col4, col5, col6 = st.columns(3)

# Input current score, overs, wickets, and last five overs' runs
with col4:
    current_score = st.number_input('Current Score', min_value=0, step=1)

with col5:
    overs = st.number_input('Overs Done (works for overs > 5)', min_value=0, step=0.1)

with col6:
    wickets = st.number_input('Wickets Fallen', min_value=0, step=1)

# Input runs scored in the last five overs
last_five = st.number_input('Runs Scored in Last 5 Overs', min_value=0, step=1)

# Prediction button
if st.button('Predict Score'):
    balls_left = 120 - (overs * 6)
    wickets_left = 10 - wickets
    crr = current_score / overs

    # Create a DataFrame with the input values
    input_df = pd.DataFrame({'batting_team': [batting_team], 'bowling_team': [bowling_team], 'city': city,
                              'current_score': [current_score], 'balls_left': [balls_left], 'wickets_left': [wickets],
                              'crr': [crr], 'last_five': [last_five]})

    # Make the prediction using the pre-trained model
    result = pipe.predict(input_df)

    # Display the predicted score
    st.header(f"Predicted Score: {int(result[0])}")

# Add a footer or additional information if needed
