from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
import requests
import json

app = FastAPI()

# Allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp = spacy.load("en_core_web_sm")

class PromptRequest(BaseModel):
    prompt: str

@app.post("/process/")
async def process_prompt(data: PromptRequest):
    prompt = data.prompt
    doc = nlp(prompt)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # Call Ollama (streamed response)
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt},
        stream=True
    )

    output = ""
    for line in response.iter_lines():
        if line:
            try:
                # chunk = json.loads(line)
                # output += chunk.get("response", "")
                json_data = json.loads(line.decode("utf-8"))
                output += json_data.get("response", "")
            except Exception as e:
                continue  # Ignore malformed chunks

    return {
        "entities": entities,
        "llm_response": output.strip()
    }
