import os
from dotenv import load_dotenv,find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY',None)

# model_client = OpenAIChatCompletionClient(model="gpt-3.5-turbo",api_key=os.getenv('openai'))
# model_client = AnthropicChatCompletionClient(model='claude-3-5-sonnet-20241022',api_key=os.getenv('ANTHROPIC_API_KEY'))

# Initialize the Gemini model client
model_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=GEMINI_API_KEY,  # Ensure this environment variable is set
    model_info={
        "family": ModelFamily.GEMINI_2_0_FLASH,
        "function_calling": True,
        "vision": False,
        "json_output": False,
        "structured_output": True,
    },
)