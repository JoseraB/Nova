import openai

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import os
import motor.motor_asyncio

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# MongoDB connection (optional if you use DB)
MONGO_URI = os.getenv("MONGO_URI")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.neo_city_db  # Change to your DB name

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Pydantic schema
class MessageRequest(BaseModel):
    messages: list[dict]

# POST endpoint
@app.post("/openai")
async def ask_openai(request: MessageRequest):
    if not isinstance(request.messages, list):
        raise HTTPException(status_code=400, detail="Invalid messages format")

    system_message = {
        "role": "system",
        "content": """
        You are Nova, a chatbot assistant for NeoCity, a school located in Kissimmee, Florida in Osceola County.

        Your responsibilities include:
        - Use no emojis.
        - Keep your information informative while trying to be concise.
        - When asked about goals of NeoCity Academy, refer back to the mission statement.
        - No personal opinions.
        - Explaining answers with accurate information.
        - Responding only to questions about NeoCity Academy. Politely decline unrelated queries.
        - Always remain friendly and professional.
        - Answer questions about the class schedule, pathway information year by year, school partners, teachers by department, new student recruitment policy, clubs and sports.
        - Please assist users only with these topics and keep responses concise, friendly, and accurate.
        """
    }

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[system_message] + request.messages,
            temperature=0.7,
        )
        reply = completion["choices"][0]["message"]["content"]
        return {"message": reply}
    except Exception as e:
        print("OpenAI API Error:", e)
        raise HTTPException(status_code=500, detail="Failed to get response from OpenAI")

# Basic health check
@app.get("/")
def read_root():
    return {"message": "Server is Online"}