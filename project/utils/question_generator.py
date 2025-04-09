# utils/question_generator.py
import json
import os
import time
from typing import List, Dict

import requests
from dotenv import load_dotenv

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")  # set DEEPSEEK_API_KEY in the.env file


class QuestionGenerator:
    def __init__(self, model: str = "deepseek-chat", max_retries: int = 3):
        self.model = model
        self.max_retries = max_retries
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

    def generate_questions(
            self,
            text: str,
            keywords: List[str],
            question_types: List[str] = ["MCQ", "True/False","Fill-in-the-Blank"],
            num_questions: int = 5
    ) -> List[Dict]:
        """Generate a variety of questions"""
        prompt = self._build_prompt(text, keywords, question_types, num_questions)
        print("prompt:{}".format(prompt))
        response = self._call_api_with_retry(prompt)
        return self._parse_response(response)

    def _build_prompt(
            self,
            text: str,
            keywords: List[str],
            question_types: List[str],
            num_questions: int
    ) -> str:
        """Build prompt that meets depth requirements"""
        return f"""
Generate {num_questions} questions based on the following text, requiring:
1. Must include these keywords: {', '.join(keywords[:5])}
2. Question types include: {', '.join(question_types)}
3. Multiple Choice Question (MCQ) requirements:
- 4 options available
- There's only one right answer
- Contains answer parsing
4. The True/False question requires:
- Clearly mark true/false
- Contains answer parsing
5. The output format must be in strict JSON format:
    {{
    "questions": [
    {{
    "type": "MCQ",
    "question": "Question content ",
    "options": ["A. Option 1", "B. Option 2",...] ,
    "answer": "A",
    "explanation": "Contents explained"
    }},
    {{
    "type": "True/False",
    "question": "Question content ",
    "answer": "True",
    "explanation": "Contents explained"
    }}
    ]
    }}
    Text content:
    {text[:3000]}
Answer questions strictly according to Question types include {', '.join(question_types)}, and only generate questions of the corresponding type. 
Before answering, think deeply for more than 10 rounds, and improve the rigor of the answer by thinking about how your own point of view will be refuted. Optimize argumentation logic to ensure comprehensiveness.
 """

    def _call_api_with_retry(self, prompt: str) -> dict:
        """API calls with retry mechanism"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a professional test question writer"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        for _ in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"API Error: {e}. Retrying...")
                time.sleep(2)
        raise Exception("API request failed after retries")

    def _parse_response(self, response: dict) -> List[Dict]:
        """The response of the analytic depth search"""
        try:
            # Extract the generated text content
            generated_text = response['choices'][0]['message']['content']

            # Handle possible markdown blocks of code
            if '```json' in generated_text:
                generated_text = generated_text.split('```json')[1].split('```')[0]

            data = json.loads(generated_text.strip())
            return data.get("questions", [])
        except (KeyError, json.JSONDecodeError) as e:
            print(f"Parsing failure: {e}")
            return []



if __name__ == "__main__":
    generator = QuestionGenerator()
    sample_text = "The OSI model consists of a seven-layer structure..."
    keywords = ["OSI Model ", "Transport Layer ", "TCP Protocol"]
    questions = generator.generate_questions(sample_text, keywords)
    print(json.dumps(questions, indent=2, ensure_ascii=False))