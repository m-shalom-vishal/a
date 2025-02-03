import streamlit as st
import nltk
from googleapiclient.discovery import build
from nltk.chat.util import Chat, reflections

# Download NLTK data (if not already installed)
nltk.download('punkt')

# Google Custom Search API setup
API_KEY = 'YOUR_GOOGLE_API_KEY'  # Replace with your Google API key
CX = 'YOUR_CX'  # Replace with your Custom Search Engine ID

def google_search(query):
    service = build("customsearch", "v1", developerKey=API_KEY)
    res = service.cse().list(q=query, cx=CX).execute()
    if 'items' in res:
        return res['items'][0]['snippet']
    else:
        return "Sorry, I couldn't find any relevant information."

# Define a simple NLP-based chatbot using NLTK
chat_pairs = [
    (r"Hi|Hello|Hey", ["Hello! How can I assist you today?"]),
    (r"(.*) weather (.*)", ["Please check the weather on your local website."]),
    (r"(.*) farming (.*)", ["I can help with farming tips. What would you like to know?"]),
    (r"(.*)", ["Sorry, I didn't understand that. Can you ask me something else?"]),
]

chatbot = Chat(chat_pairs, reflections)

# Streamlit app UI setup
st.title("Farmer Chatbot")
st.markdown("<marquee>Welcome to the Farmer Chatbot!</marquee>", unsafe_allow_html=True)

# Input from user
user_input = st.text_input("Ask me anything related to farming:")

if user_input:
    # Use NLTK chatbot if query is basic
    if "farming" in user_input.lower():
        response = chatbot.respond(user_input)
    else:
        # Use Google Custom Search API for advanced queries
        response = google_search(user_input)
    
    # Display the response
    st.write(response)
