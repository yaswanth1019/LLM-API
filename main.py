from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import langchain
import langchain_google_genai
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Initialize environment
os.environ["GOOGLE_API_KEY"] =  os.getenv("GOOGLE_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Load model
llm = ChatGroq(
    temperature=0.2,
    model_name="llama3-70b-8192"
)

rag_prompt = ChatPromptTemplate.from_template("""
You are a cultural and historical guide embedded in an AR/VR assistant.

Use the provided context to generate a **comprehensive, structured, and informative explanation**.
- Include **as much detail as possible** from the context.
- Organize the information using short paragraphs, bullet points, and section headings.
- Do **not** ask follow-up questions.
- Do **not** use conversational or assistant-like phrases.
- Do **not** speculate or add information not present in the context.

User Question: {question}

Provide only the detailed, formatted, factual information below:
""")

def create_direct_llm_chain():
    return (
        {"question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )

rag_chain = create_direct_llm_chain()

class QueryRequest(BaseModel):
    question: str

@app.post("/chat")
def chat(request: QueryRequest):
    response = rag_chain.invoke(request.question)
    return {"response": response}

# ✅ Add this route to return a default message at /
@app.get("/")
def read_root():
    return {"message": "FastAPI app is running 🚀"}
