import openai
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import json
import os
import fitz

with open("NeoCity-Data\Neocity_Academy.json", "r", encoding="utf-8") as file:
    neo_data = json.load(file)

ai_course_cert = "NeoCity-Data\NeoCity_AI_Pathway_Courses_And_Certs.pdf"

def extract_text_from_pdf(pdf_path):
    text=""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"Failed to read PDF({pdf_path}) : {e}")
        return None

def extract_data(data):
    school_info = {
        "mission": None,
        "vision": None,
        "school_profile_pdf": None,
        "ai_pathway": {},
        "projects": []
    }

    for entry in data:
        content = entry["content"]
        ctype = content["type"].lower()

        if "mission" in ctype:
            school_info["mission"] = content["text"]
        elif "vision" in ctype:
            school_info["vision"] = content["text"]
        elif "school_profile_pdf" in ctype:
            school_info["school_profile_pdf"] = content["pdf_file_path"]
        elif "ai pathway" in ctype:
            school_info["ai_pathway"]["overview"] = content["pathway_description"]
            school_info["ai_pathway"]["classes"] = [
                {"name": cls["class"], "description": cls["description"]}
                for cls in content["classes"]
            ]
        elif "projects" in ctype:
            school_info["projects"].append({
                "title": content["title"],
                "description": content["project_description"],
                "students": content["students"],
                "image": content["image"]
            })
        
    return school_info

neocity_data = extract_data(neo_data)
neocity_schoolProf_data = extract_text_from_pdf(neocity_data["school_profile_pdf"])
neocity_aipath_cert_course_data = extract_text_from_pdf(ai_course_cert)

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

app = FastAPI()

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
    print("Received Request, contacting OpenAI API...")
    if not isinstance(request.messages, list):
        raise HTTPException(status_code=400, detail="Invalid messages format")

    system_message = {
    "role": "system",
    "content": f"""
        You are Nova, a chatbot assistant for NeoCity, a school located in Kissimmee, Florida in Osceola County.

        Here is the NeoCity data which you will use to answer questions:

        Mission Statement:
        {neocity_data['mission']}

        Vision Statement:
        {neocity_data['vision']}

        School Profile PDF:
        {neocity_schoolProf_data}

        Artificial Intelligence Pathway Overview:
        {neocity_data['ai_pathway']['overview']}

        AI Pathway Courses and Certifications:
        {neocity_aipath_cert_course_data}

        AI Pathway Classes:
        """
            + "\n".join([f"{cls['name']}:\n{cls['description']}" for cls in neocity_data['ai_pathway']['classes']]) +
        """
        Projects:
        """
            + "\n".join([f"{proj['title']}:\n{proj['description']}:\n{proj['students']}:\n{proj['image']}" for proj in neocity_data['projects']]) +
        """
        Your responsibilities include:
        - Use no emojis.
        - Keep your information informative while trying to be concise.
        - When asked about goals of NeoCity Academy, refer back to the mission statement.
        - No personal opinions.
        - Explaining answers with accurate information.
        - Responding only to questions about NeoCity Academy. Politely decline unrelated queries.
        - Always remain friendly and professional.
        - Answer questions about information that is included within the data provided to you.
        - Please assist users only with these topics and keep responses concise, friendly, and accurate.
        - Be aware that most of the information provided is outdated and may not reflect the current state of NeoCity Academy.
        - If the user asks for information that is not included in the data provided to you, please say "I don't know" instead of making up an answer.
        - Updated information will be provided in the future.
        - Do not use the internet as a source of information. Only use the information provided to you in the data.
        - Your information does not include all aspects of Neocity Academy, so be aware that you may not have all the information needed to answer a question. When answering prompt make sure to specify that your information may not be accurate due to limited/outdated information.
        - With each message that you are not certain with specify your limitations, dont decieve users.
        - Take context from previous message provided to you when coming up with a response
        - If within your data there is an overlap in information prioritize data which is labeled more recent if there is no date within the data drop down its priority
        """
    }

    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[system_message] + request.messages,
            temperature=0.7,
        )
        reply = completion.choices[0].message.content
        return {"message": reply}
    except Exception as e:
        print("❌ OpenAI API Error:", e)
        raise HTTPException(status_code=500, detail=f"Failed to get response from OpenAI")
# Basic health check
@app.get("/")
def read_root():
    return {"message": "Server is Online"}