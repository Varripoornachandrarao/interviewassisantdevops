from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
try:
    from langgraph_checkpoint_redis import RedisSaver
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
from langgraph.prebuilt import create_react_agent
import assemblyai as aai
import os
import base64
import requests
import tempfile
import json
import logging
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

aai.settings.api_key = ASSEMBLYAI_API_KEY

# Initialize checkpointer (Redis for prod/scaling, InMemory for dev)
if HAS_REDIS and REDIS_URL:
    try:
        # Assuming REDIS_URL is like redis://host:port
        checkpointer = RedisSaver.from_conn_info(host=REDIS_URL.split("//")[1].split(":")[0], port=int(REDIS_URL.split(":")[2]))
        logger.info(f"Using RedisSaver for state persistence at {REDIS_URL}")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis, falling back to InMemorySaver: {e}")
        checkpointer = InMemorySaver()
else:
    logger.info("Using InMemorySaver for state persistence")
    checkpointer = InMemorySaver()

model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GOOGLE_API_KEY
)

# Shared interview prompts
INTERVIEW_PROMPT = """You are Natalie, a friendly and conversational interviewer conducting a natural {subject} interview.

IMPORTANT GUIDELINES:
1. Ask exactly 5 questions total throughout the interview
2. Keep questions SHORT and CRISP (1-2 sentences maximum)
3. ALWAYS reference what the candidate ACTUALLY said in their previous answer - do NOT make up or assume their answers
4. Show genuine interest with brief acknowledgments based on their REAL responses
5. Adapt questions based on their ACTUAL responses - go deeper if they're strong, adjust if uncertain
6. Be warm and conversational but CONCISE
7. No lengthy explanations - just ask clear, direct questions

CRITICAL: Read the conversation history carefully. Only acknowledge what the candidate truly said, not what you think they might have said.

Keep it short, conversational, and adaptive!"""

FEEDBACK_PROMPT = """Based on our complete interview conversation, provide detailed feedback as JSON only:
    {{
    "subject": "<topic>",
    "candidate_score": <1-5>,
    "feedback": "<detailed strengths with specific examples 
    from their ACTUAL answers>",
    "areas_of_improvement": "<constructive suggestions based 
    on gaps you noticed>"
    }}
    Be specific - reference ACTUAL things they said during the interview."""

app = Flask(__name__)
CORS(app, expose_headers=['X-Question-Number', 'X-Interview-Complete'])

# Session state (simple in-memory dict for demo, should be more robust in prod)
session_data = {}

def get_agent(subject=None):
    # If a subject is provided, we use it to format the system prompt
    state_modifier = INTERVIEW_PROMPT.format(subject=subject) if subject else None
    return create_react_agent(
        model=model,
        tools=[],
        checkpointer=checkpointer,
        state_modifier=state_modifier
    )

def stream_audio(text):
    BASE_URL = "https://global.api.murf.ai/v1/speech/stream"
    payload = {
        "text": text,
        "voiceId": "en-US-natalie",
        "model": "FALCON",
        "multiNativeLocale": "en-US",
        "sampleRate": 24000,
        "format": "MP3",
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": MURF_API_KEY
    }
    
    try:
        response = requests.post(
            BASE_URL,
            headers=headers,
            data=json.dumps(payload),
            stream=True
        )
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                yield base64.b64encode(chunk).decode("utf-8") + "\n"
    except Exception as e:
        logger.error(f"Error streaming audio from Murf API: {e}")
        yield ""

@app.route("/start-interview", methods=["POST"])
def start_interview():
    data = request.json
    subject = data.get("subject", "Python")
    
    # We use a default thread_id for now, but this could be passed from the client
    thread_id = data.get("session_id", "default_session")
    
    session_data[thread_id] = {
        "question_count": 1,
        "subject": subject
    }
    
    agent = get_agent(subject)
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # For LangGraph create_react_agent, we just pass the user message
        response = agent.invoke({
            "messages": [
                {"role": "user", "content": f"Start the interview with a warm greeting and ask the first question about {subject}. Keep it SHORT (1-2 sentences)."}
            ]
        }, config=config)
        
        question = response["messages"][-1].content
        logger.info(f"[Session: {thread_id}] Started interview about {subject}")
        
        return Response(stream_audio(question), mimetype='text/plain')
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        return jsonify({"error": str(e)}), 500

def speech_to_text(audio_path):
    """Convert audio file to text using AssemblyAI"""
    try:
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(
            speech_models=["universal-3-pro", "universal-2"],
            language_detection=True
        )
        transcript = transcriber.transcribe(audio_path, config=config)
        return transcript.text if transcript and transcript.text else ""
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        return ""

@app.route("/submit-answer", methods=["POST"])
def submit_answer():
    thread_id = request.form.get("session_id", "default_session")
    
    if thread_id not in session_data:
        return jsonify({"error": "Session not found. Please start a new interview."}), 400
    
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio file provided"}), 400
    
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".webm").name
    audio_file.save(temp_path)
    
    answer = speech_to_text(temp_path)
    os.unlink(temp_path)
    
    if not answer or answer.strip() == "":
        answer = "[Candidate provided a verbal response but transcription failed]"
    
    logger.info(f"[Session: {thread_id}] Answer: {answer}")
    
    config = {"configurable": {"thread_id": thread_id}}
    agent = get_agent(session_data[thread_id]["subject"])
    
    agent.invoke({"messages": [{"role": "user", "content": answer}]}, config=config)
    
    current_count = session_data[thread_id]["question_count"]
    
    if current_count >= 5:
        response = agent.invoke({
            "messages": [{"role": "user", "content": "That was the 5th question. Briefly acknowledge their ACTUAL answer and let them know the interview is complete. Keep it SHORT."}]
        }, config=config)
        
        closing_message = response["messages"][-1].content
        logger.info(f"[Session: {thread_id}] Interview complete")
        
        return Response(
            stream_audio(closing_message),
            mimetype='text/plain',
            headers={'X-Interview-Complete': 'true'}
        )
    
    session_data[thread_id]["question_count"] += 1
    new_count = session_data[thread_id]["question_count"]
    
    prompt = f"""The candidate just answered question {new_count - 1}.
Look at their ACTUAL answer above. Now ask question {new_count} of 5:
1. Briefly acknowledge what they ACTUALLY said (1 sentence)
2. Ask your next question that builds on their response (1-2 sentences)
3. Keep the TOTAL response under 3 sentences."""
    
    response = agent.invoke({"messages": [{"role": "user", "content": prompt}]}, config=config)
    question = response["messages"][-1].content
    
    return Response(
        stream_audio(question),
        mimetype='text/plain',
        headers={'X-Question-Number': str(new_count)}
    )

@app.route("/get-feedback", methods=["POST"])
def get_feedback():
    data = request.json
    thread_id = data.get("session_id", "default_session")
    
    if thread_id not in session_data:
        return jsonify({"error": "Session not found"}), 400
        
    config = {"configurable": {"thread_id": thread_id}}
    agent = get_agent(session_data[thread_id]["subject"])
    
    try:
        response = agent.invoke({
            "messages": [
                {"role": "user", "content": f"{FEEDBACK_PROMPT}\n\nReview our complete interview conversation and provide detailed feedback."}
            ]
        }, config=config)
        
        text = response["messages"][-1].content
        cleaned = text.strip()
        if "```" in cleaned:
            # Handle cases where LLM might output code blocks or not
            parts = cleaned.split("```")
            if len(parts) >= 2:
                cleaned = parts[1].replace("json", "").strip()
        
        try:
            feedback = json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback if LLM output is not clean JSON
            feedback = {"raw_text": cleaned}
            
        return jsonify({"success": True, "feedback": feedback})
    except Exception as e:
        logger.error(f"Error generating feedback: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "version": "1.2.0"}), 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
