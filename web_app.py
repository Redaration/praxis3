#!/usr/bin/env python3
"""
Web application for the AI Course Generator.
"""

from flask import Flask, request, jsonify, render_template_string
from config import config
from llm_client import call_llm
from exceptions import LLMError, ValidationError
from validation import validate_prompt

app = Flask(__name__)

# --- HTML Templates ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Course Generator</title>
    <style>
        body {
            font-family: sans-serif;
            margin: 2em;
            background-color: #f4f4f9;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2em;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        textarea {
            width: 100%;
            height: 100px;
            margin-bottom: 1em;
            padding: 0.5em;
            border-radius: 4px;
            border: 1px solid #ccc;
        }
        button {
            padding: 0.5em 1em;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .outline {
            margin-top: 2em;
            padding: 1em;
            border: 1px solid #ddd;
            background-color: #fafafa;
        }
        .error {
            color: #d8000c;
            background-color: #ffbaba;
            padding: 1em;
            border-radius: 4px;
        }
        .loading {
            text-align: center;
            padding: 2em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Course Generator</h1>
        <form id="course-form">
            <textarea id="prompt" name="prompt" placeholder="Enter a topic for your course..."></textarea>
            <button type="submit">Generate Outline</button>
        </form>
        <div id="result"></div>
    </div>

    <script>
        document.getElementById('course-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const prompt = document.getElementById('prompt').value;
            const resultDiv = document.getElementById('result');

            resultDiv.innerHTML = '<div class="loading">Generating...</div>';

            fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt: prompt })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultDiv.innerHTML = `<div class="error">${data.error}</div>`;
                } else {
                    resultDiv.innerHTML = `<div class="outline"><pre>${data.outline}</pre></div>`;
                }
            })
            .catch(error => {
                resultDiv.innerHTML = `<div class="error">An unexpected error occurred.</div>`;
            });
        });
    </script>
</body>
</html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/generate', methods=['POST'])
def generate_course():
    data = request.get_json()
    prompt = data.get('prompt')

    try:
        validated_prompt = validate_prompt(prompt)
        
        system_prompt = "You are an expert instructional designer. Create a detailed course outline based on the user's prompt. The outline should include modules, lessons, and key topics."
        
        outline = call_llm(
            prompt=validated_prompt,
            system_prompt=system_prompt,
            model=config.DEFAULT_MODEL,
            max_tokens=2000
        )
        
        return jsonify({'outline': outline})

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except LLMError as e:
        return jsonify({'error': f"LLM Error: {e}"}), 500
    except Exception as e:
        return jsonify({'error': f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True)