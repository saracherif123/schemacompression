'''
Created on Sep 8, 2023

@author: immanueltrummer
'''
import openai
import tiktoken
import time
import os


def nr_tokens(model, text):
    """ Counts the number of tokens in text.
    
    Args:
        model: use tokenizer of this model.
        text: count tokens for this text.
    
    Returns:
        number of tokens in input text.
    """
    tokenizer = tiktoken.encoding_for_model(model)
    tokens = tokenizer.encode(text)
    return len(tokens)


class LLM():
    """ Represents large language model. """
    
    def __init__(self, name, api_key=None):
        """ Initializes for OpenAI model.
        
        Args:
            name: name of OpenAI model.
            api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.name = name
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=api_key)

    def __call__(self, prompt):
        """ Retrieves answer from LLM. 
        
        Args:
            prompt: input prompt.
        
        Returns:
            model output.
        """
        for retry_nr in range(1, 4):
            try:
                response = self.client.chat.completions.create(
                    model=self.name,
                    messages=[
                        {'role':'user', 'content':prompt}
                        ]
                    )
                return response.choices[0].message.content
            except Exception as e:
                print("OpenAI API error:", e)
                time.sleep(2 * retry_nr)
        raise Exception('Cannot reach OpenAI model!')