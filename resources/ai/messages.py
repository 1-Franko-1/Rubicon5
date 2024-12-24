#####################################################################################################################################################
##                                                                                                                                                 ##
##                                                        Rubicon 5 Source File: messages.py                                                       ##
##                                           The AI message handler. Also handles some other Groq stuff.                                           ##
##                                                                                                                                                 ##
#####################################################################################################################################################

#---------------------------------------------------------------------------------------------------------------------------------------------------#
###                                                           Hard-coded Python Modules                                                           ###
#---------------------------------------------------------------------------------------------------------------------------------------------------#

import random                                                             # Random        | Generate random numbers.

#---------------------------------------------------------------------------------------------------------------------------------------------------#
###                                                             Internal Source Files                                                             ###
#---------------------------------------------------------------------------------------------------------------------------------------------------#

from resources.deps.dephandler import *
from resources.deps.dependencydefs import *

#---------------------------------------------------------------------------------------------------------------------------------------------------#
###                                                                External Modules                                                               ###
#---------------------------------------------------------------------------------------------------------------------------------------------------#

### Soft Dependencies ###

groq_available = False
ollama_available = False
requests_available = False

with soft_dependency("Rubicon", soft_dependencies): import groq; groq_available = True
with soft_dependency("Rubicon", soft_dependencies): import ollama; ollama_available = True
with soft_dependency("Rubicon", soft_dependencies): import requests; requests_available = True

#---------------------------------------------------------------------------------------------------------------------------------------------------#
###                                                                    Globals                                                                    ###
#---------------------------------------------------------------------------------------------------------------------------------------------------#

random_messages = [
    "...What is that thing behind you?",
    "AUGUST 12TH, 2036, THE HEAT DEATH OF THE UNIVERSE. AUGUST 12TH, 2036, THE HEAT DEATH OF THE UNIVERSE. AUGUST 12TH, 2036, THE HEAT DEATH OF THE UNIVERSE.",
    "...Is that an omnious... Weirdly humming... Obsidian orb?",
    "The sun is shining. The sun is shining. The sun is shining. The sun is shining. The sun is shining. The sun is shining. The sun is shining. The sun is shining. The sun is shining.",
    "The sun is leaking. It's dissolving. It's coming apart. It's... Melting. It's raining down on us.",
    "Are those.. Bells? Bells ringing?"
]

#---------------------------------------------------------------------------------------------------------------------------------------------------#
###                                                                   Functions                                                                   ###
#---------------------------------------------------------------------------------------------------------------------------------------------------#

def groq_message(gclient: groq.Groq, conversation: dict[str, str], restricted_phrases: list[str] | None = None, random_message_chance: int = 150, tools = None,
                 model: str = "llama-3.3-70b-versatile", temperature: float = 0.25, top_p: float = 1.00, top_k: int = 40, frequency_penalty: float = 0.00,
                 presence_penalty: float = 0.00, max_tokens: int = 32768) -> str:
    
    """Takes the given conversation and returns a response from Groq.
    If restricted_phrases is not None, any matching string in the response will be removed.
    If random_message_chance is non-zero (and non-negative), there will be a 1/random_message_chance chance that a random message will be returned along with the message.

    If the Groq client is None, the function will return default values.
    
    Tools are functions the AI can use to do things.
    It is expected to be in a valid Groq format.
    
    This function does *not* handle errors, such as the model being nonexistent.
    You will have to handle those errors yourself."""

    if not gclient: return "", None, None

    raw_response = gclient.chat.completions.create(
        model=model,
        messages=conversation,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        max_tokens=max_tokens,
        tools=tools
    )

    raw_response = raw_response.choices[0].message
    message_content = raw_response.content
    used_tools = raw_response.tool_calls

    for phrase in restricted_phrases:
        message_content = message_content.replace(phrase, "")

    if random_message_chance < 0:
        random_message_chance = 0

    if random_message_chance > 0:
        if random.randint(1, random_message_chance) == 1:
            message_content = random.choice(random_messages)

    return message_content, raw_response, used_tools

# TODO ollama support

def get_valid_groq_model(model: str = "llama3-70b-8192", groq_client: groq.Groq = None) -> str:
    """Check if the provided model name is a valid Groq model. If it is, return it. Otherwise, return None."""

    if groq_available and requests_available and groq_client:
        _url = "https://api.groq.com/openai/v1/models"
        _headers = {
            "Authorization": f"Bearer {groq_client.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(_url, headers=_headers).json()

        for model_dict in response["data"]:
            if model_dict["id"] == model:
                model_response = model_dict["id"]
                return model_response
            else:
                continue

        return None # Invalid.

    return None # We can't verify...