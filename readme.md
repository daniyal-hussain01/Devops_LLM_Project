DevOps LLM Web Application

This project is a lightweight DevOps based LLM web application built using Flask and SQLite. It retrieves prompts from a database, sends them to a Groq hosted LLaMA model through an API, and returns AI generated responses to the user via a web interface.

Tech Stack

Backend: Python with Flask
Database: SQLite
LLM Provider: Groq API using LLaMA model
Frontend: HTML and JavaScript
Environment Management: Python virtual environment
Version Control: Git and GitHub

Project Flow

User selects an option in the browser
Frontend sends the selected ID to the backend
Backend fetches the prompt from SQLite
Prompt is sent to the Groq API
Model response is received
Backend returns the result to frontend
User sees the generated output

How to Run Locally

Clone the repository

Navigate to the project folder

Create a virtual environment
python -m venv venv

Activate the virtual environment
Windows CMD: venv\Scripts\activate
PowerShell: .\venv\Scripts\Activate.ps1

Install dependencies
pip install -r requirements.txt

Create a .env file in the root directory and add
GROQ_API_KEY=your_api_key_here

Run the application
python app.py

Open your browser and visit
http://127.0.0.1:5000