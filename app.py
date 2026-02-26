from flask import Flask, render_template, request, jsonify
from database import get_prompt_by_id, get_all_prompts
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
print("App is starting...")

app = Flask(__name__)

# Initialize Groq/OpenAI client with API key and base URL
client = OpenAI(
api_key=os.getenv("GROQ_API_KEY"),
base_url="https://api.groq.com/openai/v1"
)


# Home route: display all prompts
@app.route("/")
def index():
    prompts = get_all_prompts()  # Fetch prompts from the database
    return render_template("index.html", prompts=prompts)

# Generate route: send selected prompt to the model
@app.route("/generate", methods=["POST"])
def generate():
    # Get the prompt ID sent from frontend
    prompt_id = request.json.get("id")
    
    # Fetch the prompt text from database using ID
    prompt_text = get_prompt_by_id(prompt_id)

    # Return error if ID is invalid
    if not prompt_text:
        return jsonify({"error": "Invalid ID"}), 400

    # Send prompt to Groq API model
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt_text}]
    )

    # Return the generated response to frontend
    return jsonify({"result": response.choices[0].message.content})

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)