# AI Information Retriever

This project is an AI-powered tool that helps you extract information from web search results. You can upload a CSV file or connect to a Google Sheet, specify a search query, and use an LLM (Hugging Face Question Answering API) to extract the desired information.

## Features

*   **Data input:** Upload a CSV file or connect to a Google Sheet.
*   **Dynamic queries:** Define search queries with placeholders (e.g., "Find the email address of {company}").
*   **Web search:** Automatically performs web searches using SerpAPI.
*   **LLM extraction:** Uses the Hugging Face Question Answering API to extract information from search results.
*   **Output:** Displays extracted data in a table and allows downloading as a CSV.
*   **Google Sheet update:** Option to update the connected Google Sheet with the extracted data.

## Setup Instructions

1.  **Install dependencies:**
    ```bash
    pip install streamlit pandas google-api-python-client google-auth-httplib2 google-auth-oauthlib serpapi requests
    ```

2.  **API keys and environment variables:**
    *   Obtain API keys for SerpAPI and Hugging Face.
    *   Store these API keys as environment variables:

        *   **Windows:**
            ```bash
            setx SERPAPI_API_KEY "your_serpapi_api_key"
            ```

        *   **macOS/Linux:**
            ```bash
            export SERPAPI_API_KEY="your_serpapi_api_key"
            ```

    *   For Google Sheets integration, create a service account in your Google Cloud project and store the JSON credentials file.
    *   For Hugging Face API key, you can store it in Streamlit secrets:
        *   Create a `.streamlit/secrets.toml` file in your app's directory.
        *   Add your Hugging Face API key:

            ```toml
            huggingface_api_key = "your_huggingface_api_key"
            ```

3.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

## Usage Guide

1.  **Data input:**
    *   Select either "CSV File" or "Google Sheets" as your data source.
    *   Upload your CSV file or provide the Google Sheet ID, Sheet Name, and your service account credentials file.

2.  **Select main column:**
    *   Choose the column from your data that contains the entities you want to search for (e.g., company names).

3.  **Enter prompt:**
    *   Type your search prompt, using a placeholder (e.g., "{company}") to represent the entity from your data.
        *   Example: "Find the email address of {company}"

4.  **Start processing:**
    *   Click the "Start Processing" button to initiate the web search and information extraction.

5.  **View and download results:**
    *   The extracted information will be displayed in a table.
    *   Click "Download CSV" to download the results.

6.  **Update Google Sheet (optional):**
    *   If you connected to a Google Sheet, click "Update Google Sheet" to update the sheet with the extracted data.

## Optional Features

*   **Error handling:** Includes exception handling to catch and display errors during web search and LLM extraction.
*   **Google Sheet update:** Allows updating the connected Google Sheet.

## Loom Video Walkthrough

(https://drive.google.com/file/d/1RoIWBIMdRXTidGdqvH2Be4h31czpfOh9/view?usp=drive_link)
