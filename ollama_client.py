import requests

class OllamaClient:
    def __init__(self, host="localhost", port=11434, model="llama2"):
        self.base_url = f"http://{host}:{port}/api/generate"
        self.model = model

    def generate(self, prompt, timeout=300):
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.base_url, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.Timeout:
            return f"Error: Request timed out after {timeout} seconds. The story generation may take longer; try reducing the story length or waiting."
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {str(e)}"
