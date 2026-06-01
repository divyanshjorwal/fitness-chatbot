#basic most bot 
from groq import Groq

client = Groq(api_key="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")

system_prompt = "answer with whatever relevant information there is to the question act like a normal chatbot'"

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input("Ask anything: ")}
    ]
)

print(response.choices[0].message.content)