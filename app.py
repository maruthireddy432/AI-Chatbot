from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_connection
from groq_rag_model import GroqRAGModel
import os
from dotenv import load_dotenv
import re
import json
from flask import Flask, request, jsonify

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# -----------------------------
# ✅ Initialize model globally
# -----------------------------
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("❌ GROQ_API_KEY not found in .env file.")

app.logger.info("🚀 Loading GroqRAG model...")
groq_model = GroqRAGModel(groq_api_key=groq_api_key)
app.logger.info("✅ GroqRAG model loaded successfully.")


# ------------------------------------------------------------------
# ✨ NEW: Function to parse the model's string output into JSON
# ------------------------------------------------------------------
def parse_bot_reply_to_json(raw_text: str):
    """
    Parses a markdown-like text string from the model into a structured
    JSON format for the frontend.
    """
    # If the response is simple (no special formatting), return it as a single paragraph.
    if '**' not in raw_text and '•' not in raw_text:
        return [{"type": "paragraph", "content": raw_text}]

    # Clean up text and split into processable lines
    lines = raw_text.replace('<br>', '\n').split('\n')
    
    structured_reply = []
    current_section = None
    
    # Heuristic to find the main header (usually the first bolded line)
    first_bold_line = next((line for line in lines if line.strip().startswith('**')), None)
    if first_bold_line:
        header_content = first_bold_line.strip().strip('* ')
        # Remove separators if they are in the header
        header_content = re.split(r' \|\|-+', header_content)[0].strip()
        structured_reply.append({"type": "header", "content": header_content})
        # Remove the header line so it's not processed again
        lines.pop(lines.index(first_bold_line))

    for line in lines:
        line = line.strip()
        if not line or '-----' in line:
            continue

        # Check for a section title (e.g., **Credit & Financing**)
        is_section_title = line.startswith('**') and line.endswith('**') and '•' not in line
        if is_section_title:
            if current_section:
                structured_reply.append(current_section)
            
            title = line.strip('* ')
            current_section = {"type": "section", "title": title, "items": []}
            continue

        # Check for a list item (e.g., • **Scheme Name** | Description)
        if line.startswith('•'):
            if not current_section:
                # Create a default section if an item appears without a title
                current_section = {"type": "section", "title": "Details", "items": []}

            # Clean the line and split into scheme and description
            item_content = line.lstrip('• ').strip()
            parts = item_content.split('|', 1)
            scheme_part = parts[0].strip().replace('**', '')
            description = parts[1].strip() if len(parts) > 1 else ""
            
            current_section["items"].append({
                "scheme": scheme_part,
                "description": description
            })

    # Add the last processed section
    if current_section:
        structured_reply.append(current_section)
        
    return structured_reply


@app.route('/')
def home():
    """Basic health check"""
    return jsonify({"message": "Chatbot backend is running!"})


@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        conn = get_connection()
        if not conn:
            app.logger.error("❌ Database connection failed.")
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (sender, message) VALUES (%s, %s)",
            ("user", user_message)
        )
        conn.commit()

        app.logger.info(f"🤖 User: {user_message}")
        
        # --- THIS IS THE FIX ---
        
        # 1. Get the response from the model (which might be a string)
        bot_reply_from_model = groq_model.ask(user_message)
        app.logger.info(f"✅ Bot Raw Output from Model: {bot_reply_from_model}")

        # 2. Parse the string into a Python object (list/dict)
        parsed_json_reply = bot_reply_from_model
        if isinstance(bot_reply_from_model, str):
            try:
                # This line converts the JSON string into a proper Python list
                parsed_json_reply = json.loads(bot_reply_from_model)
            except json.JSONDecodeError:
                app.logger.error(f"Failed to parse model output as JSON: {bot_reply_from_model}")
                parsed_json_reply = [{"type": "paragraph", "content": "Sorry, I received an invalid response."}]

        # --- END OF FIX ---

        bot_message_for_db = json.dumps(parsed_json_reply)
        cursor.execute(
            "INSERT INTO chat_history (sender, message) VALUES (%s, %s)",
            ("bot", bot_message_for_db)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # 3. Return the fully parsed JSON object to the frontend
        return jsonify({"reply": parsed_json_reply})

    except Exception as e:
        app.logger.exception("🔥 Error in /chat endpoint:")
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)