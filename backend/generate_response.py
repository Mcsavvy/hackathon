import cohere
import os

def interpret(phone):
    """The interpret function akes a dictionary and then calls on cohere AI
the cohere Ai now interprets this dictionary in a user friendly for
"""
    info = str(phone)
    prompt = f"This is an informative, persuasive salesman marketing for an electronics company trying to sell a\
    product, information is {info}, the salesman tells our customer:"
    co = cohere.Client(os.getenv("COHERE_API_KEY"))
    response = co.generate(  
        model='command-xlarge-nightly',  
        prompt = prompt,  
        max_tokens=400,
        temperature=1.5,
        k=2)
    res = response.generations[0].text
    print(res)
    return res;
