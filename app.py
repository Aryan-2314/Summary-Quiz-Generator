import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow frontend communication
CORS(app)

# Configure the Gemini API key from the .env file
try:
    genai.configure(api_key="AIzaSyDisN_-LtP7mhryoV8D2uz6BcIQfU-pNe8")
except AttributeError as e:
    print("ERROR: The GOOGLE_API_KEY is missing. Please ensure it is set in your .env file.")
    exit()

# This is a basic route to confirm the server is running
@app.route('/')
def home():
    """Provides a simple confirmation that the server is online."""
    return "Hello! The Gemini Quiz Generator server is running."

# This is the main endpoint that generates the summary and quiz
@app.route('/api/generate', methods=['POST'])
def generate_content():
    """
    Receives text via a POST request, sends it to the Gemini API,
    cleans the response, and returns a JSON object with a summary and quiz.
    """
    # 1. Validate that the request contains JSON with a 'text' key
    if not request.json or 'text' not in request.json:
        return jsonify({"error": "Request must be JSON with a 'text' key."}), 400
    
    lecture_text = request.json['text']

    try:
        # 2. Initialize the desired Gemini Model
        model = genai.GenerativeModel('gemini-2.5-flash')

        # 3. Create the detailed prompt for the AI
        prompt = f"""
        Based on the following lecture text, please perform two tasks:
        First, provide a concise summary of the key points in 3-5 bullet points.
        Second, generate a 5-question multiple-choice quiz based on the text. For each question, provide 4 options (A, B, C, D) and indicate the correct answer.

        Format your entire response as a single, valid JSON object with two keys: "summary" and "quiz".
        The "summary" key's value should be an array of strings (the bullet points).
        The "quiz" key's value should be an array of objects, where each object has the keys: "question", "options", and "answer". The "options" value should be an object with keys "A", "B", "C", "D". The "answer" value should be the letter of the correct option.

        IMPORTANT: Do not include any text, introductory phrases, or markdown formatting like ```json before or after the JSON object itself. The entire response text should be only the JSON object.

        Lecture Text:
        ---
        {lecture_text}
        ---
        """
        
        # 4. Call the Gemini API to get the response
        response = model.generate_content(prompt)
        # ADD THESE THREE LINES TO DEBUG
        print("----------- RAW AI RESPONSE -----------")
        print(response.text)
        print("----------- END RAW AI RESPONSE -----------")
        
        # 5. Clean the AI's response to ensure it's valid JSON
        # The model can sometimes wrap the JSON in markdown fences (```json ... ```)
        # This code extracts the clean JSON from the raw text response.
        
        text_response = response.text
        match = re.search(r"```json\s*(\{.*?\})\s*```", text_response, re.DOTALL)
        if match:
            clean_json = match.group(1)
        else:
            # If markdown is not found, find the first '{' and last '}'
            start_index = text_response.find('{')
            end_index = text_response.rfind('}')
            if start_index != -1 and end_index != -1 and end_index > start_index:
                clean_json = text_response[start_index:end_index+1]
            else:
                # If no JSON object can be found at all, raise an error
                raise ValueError("No valid JSON object found in the AI response.")
        
        # 6. Return the cleaned JSON string to the frontend
        return clean_json, 200, {'Content-Type': 'application/json'}

    except Exception as e:
        # Handle potential errors from the API or code
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

# This block allows you to run the app directly from the command line
if __name__ == '__main__':
    app.run(debug=True)