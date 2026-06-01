#2 memory in this bot 
from groq import Groq

client= Groq(api_key="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")

system_prompt = "You are a fitness coach. Only answer questions related to gym, diet and fitness." \
" If asked anything else, say 'I only help with fitness related questions and answer precisely"

messages = [
    {"role":"system", "content":system_prompt}

]

messages = [
    {"role": "system", "content": system_prompt}
]

while True:
    user_input = input("ask me anything fitness related :")
    
    messages.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    
    reply = response.choices[0].message.content
    
    messages.append({"role": "assistant", "content": reply})
    
    print(f"Bot: {reply}\n")