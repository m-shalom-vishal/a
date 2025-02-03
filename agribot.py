import streamlit as st
import requests
import pandas as pd
import os
import nltk
from nltk.tokenize import word_tokenize

nltk.data.path.append(os.path.abspath("nltk_data"))
nltk.download('punkt')

# Google Custom Search API Config
API_KEY = "AIzaSyBGKiSPD8Aj1TWm1OqE9Cpn0laxzE1n0O0"  # Replace with your API key
SEARCH_ENGINE_ID = "57e4625115f494176"  # Replace with your CSE ID
CSV_FILE = "search_history.csv"  # File to store search history

# Apply Web Designing with Custom CSS
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg,rgb(180, 250, 16),rgb(119, 235, 108));
            color: #333;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(135deg, #a1c4fd, #c2e9fb);
        }
        h1 {
            color: darkblue;
            text-align: center;
            font-size: 32px;
        }
        .stTextInput>div>div>input {
            background-color: white;
            color:darkblue;
            border: 2px solid #ff9a9e;
            border-radius: 8px;
        }
        .stButton>button {
            background-color: #ff758c;
            color: white;
            border-radius: 8px;
            padding: 10px;
        }
        @keyframes scrollText {
            from { transform: translateX(100%); }
            to { transform: translateX(-100%); }
        }
        .scrolling-title {
            font-size: 40px;
            font-weight: bold;
            color: green;
            white-space: nowrap;
            overflow: hidden;
            display: inline-block;
            animation: scrollText 10s linear infinite;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
st.sidebar.title("🌾 AgriBot Menu")
page = st.sidebar.radio("Go to", ["Chatbot", "Search History"])

# NLP Functions
def search_google(query):
    """Fetches results from Google Custom Search API"""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url).json()
    
    results = []
    for item in response.get("items", []):
        results.append({"title": item["title"], "link": item["link"], "snippet": item["snippet"]})
    
    return results

def preprocess_query(query):
    """Preprocesses user query using NLP (tokenization)"""
    tokens = word_tokenize(query.lower())
    return " ".join(tokens)

def save_to_csv(query, results):
    """Saves search query and results to a CSV file"""
    data = []
    for result in results:
        summarized_snippet = result["snippet"]  # Since we're not summarizing, just use the original snippet
        data.append([query, result["title"], result["link"], summarized_snippet])
    
    df = pd.DataFrame(data, columns=["Query", "Title", "Link", "Summary"])
    
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, mode='w', header=True, index=False)

# Page Selection
if page == "Chatbot":
    st.markdown("<div class='scrolling-title'>🌾 AgriBot - Your Smart Agricultural Assistant 🚜</div>", unsafe_allow_html=True)
    
    query = st.text_input("Enter your question:")
    
    if query:
        processed_query = preprocess_query(query)
        search_results = search_google(processed_query)
        
        if not search_results:
            st.warning("No relevant results found. Try rephrasing your query.")
        else:
            st.subheader("Top Results:")
            for result in search_results[:5]:
                st.markdown(f"**[{result['title']}]({result['link']})**")
                st.write(result["snippet"])
                st.write("---")
            
            save_to_csv(query, search_results)
            st.success("Your search history has been saved! ✅")

elif page == "Search History":
    st.title("📂 Search History")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.dataframe(df)
    else:
        st.warning("No search history found.")
