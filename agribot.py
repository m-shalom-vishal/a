import streamlit as st
import requests
import pandas as pd
import os
import nltk
from nltk.tokenize import word_tokenize
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from langdetect import detect
from googletrans import Translator  # Google Translate API

nltk.download('punkt_tab')

# Google Custom Search API Config
API_KEY = "AIzaSyBGKiSPD8Aj1TWm1OqE9Cpn0laxzE1n0O0"  # Replace with your API key
SEARCH_ENGINE_ID = "57e4625115f494176"  # Replace with your CSE ID
CSV_FILE = "search_history.csv"  # File to store search history

# Initialize translator
translator = Translator()

# Detect language of user input
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"

# Translate text between languages
def translate_text(text, src_lang, dest_lang="en"):
    if src_lang != dest_lang:
        return translator.translate(text, src=src_lang, dest=dest_lang).text
    return text

# Google Search API function
def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url).json()

    results = []
    for item in response.get("items", []):
        results.append({"title": item["title"], "link": item["link"], "snippet": item["snippet"]})

    return results

# Preprocess query
def preprocess_query(query):
    tokens = word_tokenize(query.lower())
    return " ".join(tokens)

# Summarize text
def summarize_text(text, sentences=2):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences)
    return " ".join([str(sentence) for sentence in summary])

# Save search history
def save_to_csv(query, results, lang):
    data = []
    for result in results:
        summarized_snippet = summarize_text(result["snippet"])
        translated_summary = translate_text(summarized_snippet, "en", lang)
        translated_title = translate_text(result["title"], "en", lang)
        
        data.append([query, translated_title, result["link"], translated_summary])

    df = pd.DataFrame(data, columns=["Query", "Title", "Link", "Summary"])
    
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, mode='w', header=True, index=False)

# Detect greetings
def detect_greeting(query):
    greetings_keywords = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening', 'hey', 'hi there', 'bye', 'goodbye', 'take care']
    return any(greeting in query.lower() for greeting in greetings_keywords)

# Streamlit UI
st.title("🌾 AgriBot - Multilingual Chatbot 🚜")

st.sidebar.title("🌾 AgriBot Menu")
page = st.sidebar.radio("Go to", ["Chatbot", "Search History"])

if page == "Chatbot":
    query = st.text_input("Enter your question:")

    if query:
        user_lang = detect_language(query)  # Detect user's language
        query_in_english = translate_text(query, user_lang, "en")  # Translate query to English

        if detect_greeting(query_in_english):
            response = "Hello, Welcome to Agribot! How can I assist you today?"
        else:
            processed_query = preprocess_query(query_in_english)
            search_results = search_google(processed_query)

            if not search_results:
                response = "No relevant results found. Try rephrasing your query."
            else:
                response = ""
                for result in search_results[:5]:
                    translated_title = translate_text(result["title"], "en", user_lang)
                    translated_snippet = translate_text(result["snippet"], "en", user_lang)
                    response += f"**[{translated_title}]({result['link']})**\n\n{translated_snippet}\n\n---\n"

                save_to_csv(query, search_results, user_lang)

        # Translate response back to the user's language
        translated_response = translate_text(response, "en", user_lang)
        st.markdown(translated_response)

elif page == "Search History":
    st.title("📂 Search History")
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.dataframe(df)
    else:
        st.warning("No search history found.")
