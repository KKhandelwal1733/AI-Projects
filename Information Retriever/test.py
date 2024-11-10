import os
import groq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableLambda

# Set up the Groq API key
os.environ['GROQ_API_KEY'] = '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'

# Initialize the Groq client with the API key
client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define the prompt template
template = """Extract the {information} of {company} from the following web results:
{web_results}"""
prompt_template = PromptTemplate(
    input_variables=["information", "company", "web_results"],
    template=template
)

# Function to interact with the Groq API
def groq_completion(inputs):
    prompt = inputs
    # Making the API call to Groq and getting the response
    response = client.chat.completions.create(
        model="gemma2-9b-it",  # You can specify other Groq models if needed
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

# Function to extract information from search results using LangChain
def extract_information(prompt, search_results):
    # Prepare the prompt with search results
    formatted_results = "\n".join(
        [
            f"**{result['title']}**\n{result['snippet']}\n{result['link']}\n"
            for result in search_results
        ]
    )

    # Creating the full prompt by using prompt_template
    full_prompt = prompt_template.format(
        information="email address",  # Modify to extract different types of info
        company="Breakout Consultancy Private Limited",
        web_results=formatted_results
    )

    # Wrap the groq_completion function as a RunnableLambda
    groq_runnable = RunnableLambda(groq_completion)

    # Wrap the prompt_template as a RunnableLambda
    prompt_runnable = RunnableLambda(lambda inputs: prompt_template.format(**inputs))

    # Define the final sequence to chain the prompt and completion function
    sequence = RunnableSequence(prompt_runnable,groq_runnable)  # Step 2: Calling Groq API for completion

    # Run the sequence with the full prompt
    response = sequence.invoke(
        {
            'information': 'email address',  # info to extract
            'company': 'Breakout Consultancy Private Limited', 
            'web_results': formatted_results
        }
    )

    return response.strip()

# Example usage
if __name__ == "__main__":
    # Example search results (replace with actual search results from a web search)
    search_results = [
        {"title": "Breakout Consultancy - Contact Us", "snippet": "Contact us at email@example.com", "link": "https://example.com/contact"},
        {"title": "Breakout Consultancy Pvt Ltd", "snippet": "Our email is info@breakout.com", "link": "https://breakout.com"}
    ]

    # Define the prompt (customizable)
    prompt = "Extract the email address of {company} from the following web results:"

    # Call the function to extract information
    extracted_info = extract_information(prompt, search_results)

    # Print the extracted information
    print("Extracted Information:", extracted_info)
