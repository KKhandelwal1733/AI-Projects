import streamlit as st
import pandas as pd
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from typing import List, Dict
from serpapi import GoogleSearch 
import groq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableLambda


# Set your SerpAPI API key
serpapi_api_key = os.environ.get("SERPAPI_API_KEY")

# --- Google Sheets Integration ---
# Create a connection to Google Sheets
def connect_to_google_sheets(credentials):
    try:
        creds = service_account.Credentials.from_service_account_info(
            credentials, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds)
        return service
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

# --- Data Loading ---
def load_data():
   try: 
    data_source = st.radio("Select Data Source:", ("CSV File", "Google Sheets"))
    df = None
    sheet_id = None
    sheet_name = None
    service = None
    if data_source == "CSV File":
        uploaded_file = st.file_uploader("Upload CSV File", type="csv")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
    elif data_source == "Google Sheets":
        st.write("Please upload your Google Service Account JSON file:")
        credentials_file = st.file_uploader(
            "Upload Credentials", type="json"
        )
        if credentials_file:
            try:
                credentials = json.load(credentials_file)
                service = connect_to_google_sheets(credentials)
                if service:
                    sheet_id = st.text_input("Enter Google Sheet ID:")
                    sheet_name = st.text_input("Enter Sheet Name:")
                    if sheet_id and sheet_name:
                        range_name = f"{sheet_name}!A:Z"  # Adjust range as needed
                        result = (
                            service.spreadsheets()
                            .values()
                            .get(spreadsheetId=sheet_id, range=range_name)
                            .execute()
                        )
                        df = pd.DataFrame(result.get("values", []))
            except Exception as e:
                st.error(f"Error loading data from Google Sheets: {e}")
    if df is not None:
        st.write("Data Preview:")
        st.dataframe(df.head())
        return df, sheet_id, sheet_name, service
    else:
        return None,None ,None,None
   except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

# --- Prompt Input ---
def get_user_prompt():
    prompt = st.text_input(
        "Enter your prompt (use {company} as a placeholder):",
        "Get me the email address of {company}",
    )
    return prompt

# --- Web Search ---
def search_web(query):
    params = {
        "api_key": serpapi_api_key,
        "engine": "google",
        "q": query,
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results["organic_results"]  # Adjust based on SerpAPI response structure

# --- LLM Extraction ---
def query(payload):
    """
    Send a POST request to the Hugging Face Inference API with the question and context.
    Args:
        payload (dict): A dictionary containing "question" and "context".
    Returns:
        dict: The API response containing the answer or error details.
    """
    API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    headers = {"Authorization": "Bearer hugging_face_token"}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx or 5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def extract_information(prompt, search_results):
    """
    Extract information using the Hugging Face Question Answering API.
    Args:
        prompt (str): The question to be answered.
        search_results (list[dict]): A list of dictionaries containing "title", "snippet", and "link".
    Returns:
        str: The extracted answer or an error message.
    """
    # Combine search results into a single context string
    context = "\n".join(
        [
            f"{result['title']}: {result['snippet']} ({result['link']})"
            for result in search_results
        ]
    )

    # Prepare the payload for the Hugging Face API
    payload = {
        "question": prompt,
        "context": context
    }

    # Query the API and process the response
    response = query(payload)
    if "error" in response:
        return f"Error: {response['error']}"
    return response.get("answer", "No relevant information found.")



# --- Main App ---
def main():
    st.title("AI Information Extractor")

    # Load data
    df, sheet_id, sheet_name, service = load_data()
    if df is None:
        return

    # Select main column
    main_column = st.selectbox("Select the main column", df.columns)

    # Get user prompt
    user_prompt = get_user_prompt()

    # Process data
    if st.button("Start Processing"):
        extracted_data = []
        for entity in df[main_column]:
            # Construct search query
            query = user_prompt.replace("{company}", entity)

            # Perform web search
            search_results = search_web(query)

            # Extract information using LLM
            try:
                extracted_info = extract_information(query, search_results)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.error("Error extracting information:")
            
                

            extracted_data.append({"Company": entity, "Extracted Info": extracted_info})

        # Display results
        st.write("Extracted Information:")
        ouput_df=pd.DataFrame(extracted_data)
        st.dataframe(ouput_df)

        # Download CSV
        st.download_button(
            "Download CSV",
            ouput_df.to_csv(index=False).encode("utf-8"),
            "extracted_data.csv",
            "text/csv",
        )
        
        if service and sheet_id and sheet_name:
            if st.button("Update Google Sheet"):
                try:
                    range_name = f"{sheet_name}!A:Z"  # Adjust range as needed
                    service.spreadsheets().values().update(
                        spreadsheetId=sheet_id,
                        range=range_name,
                        valueInputOption="USER_ENTERED",
                        body={"values": output_df.values.tolist()},
                    ).execute()
                    st.success("Google Sheet updated successfully!")
                except Exception as e:
                    st.error(f"Error updating Google Sheet: {e}")

if __name__ == "__main__":
    main()