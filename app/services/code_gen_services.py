from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os
from dotenv import load_dotenv

from ..mypackages.myfunction import timer
from ..config.settings import settings

load_dotenv()


DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Initialize LangChain with DeepSeek
llm = ChatOpenAI(
    model_name="deepseek-chat",
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base="https://api.deepseek.com"
)

@timer
def update_website_styles(html_code: str, css_code: str, style_update_prompt: str) -> tuple:
    """
    Given the HTML and CSS of a website and a prompt describing the style updates to be made,
    this function uses LangChain to generate the updated HTML and CSS with the specified style changes.
    """

    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Deepseek API Key: {settings.DEEPSEEK_API_KEY}")
    print(f"Secret Token: {settings.SECRET_TOKEN}")
    
    prompt = f"""
    You will be given the HTML and CSS of a website along with a prompt describing the style updates to be made. Your task is to modify only the styles according to the prompt while keeping all structure, class names, and logic intact. Here's how to proceed:

    First, you will receive the website's HTML and CSS:

    <html_code>
    {html_code}
    </html_code>

    <css_code>
    {css_code}
    </css_code>

    Next, you will receive a prompt describing the style updates to be made:

    <style_update_prompt>
    {style_update_prompt}
    </style_update_prompt>

    Your task is to update the styles according to the prompt while following these guidelines:

    - Modify only the CSS, either within the provided <style> tag or in an external stylesheet if referenced.
    - Do not change any class names, IDs, or structural elements in the HTML.
    - Keep all logic, structure, and functionality of the website unchanged.
    - If necessary, you may add inline styles to elements in the HTML, but do not remove or modify external stylesheets.

    After making the style updates, provide the entire updated HTML and CSS wrapped in the following tags:

    <updated_html>
    {{UPDATED_HTML}}
    </updated_html>

    <updated_css>
    {{UPDATED_CSS}}
    </updated_css>

    Your final output should only include the updated HTML and CSS, formatted as described, without any explanations, comments, or additional text outside these tags.
    """
    
    messages = [
        SystemMessage(content="You are a helpful assistant"),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    response = response.content
    updated_html = response.split("<updated_html>")[1].split("</updated_html>")[0]
    updated_css = response.split("<updated_css>")[1].split("</updated_css>")[0]

    return updated_html, updated_css

    
# if __name__ == "__main__":
    
#     html_code = """
#     <html>
#     <head>
#         <title>Website Styles</title>
#         <link rel="stylesheet" href="styles.css">
#     """

#     css_code = """
#     body {

#     }
#     """

#     style_update = "make the footer more modern and visually appealing"

#     updated_html_css = update_website_styles(html_code, css_code, style_update)
#     print(updated_html_css)