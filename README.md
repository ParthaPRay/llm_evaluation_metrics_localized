# LLM Evaluation Metrics at Edge

This project provides a Flask-based API for evaluating and monitoring the performance of Large Language Models (LLMs) with detailed metrics including resource usage (CPU, memory, power), and operational efficiency.

---
## Modify base_power and max_power of your device

* base_power = The Value e.g., 240 ; for IDLE Mode
* max_power = The Value e.g. 600 ; for FULL MODE
---

## Installation

### Step 1: Install Ollama
Ensure that you have **Ollama** installed on your system. Refer to [Ollama's official installation guide](https://ollama.com) for instructions.

### Step 2: Set Up Python Environment
1. Clone this repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Requirements
Ensure the following Python libraries are installed:
- `flask`
- `psutil`
- `requests`

These are already listed in the `requirements.txt` file.

## Running the Application

llm_metrics_11.py has CSV and JSON logging

1. Start the Flask server:
   ```bash
   python llm_metrics_11.py
   ```

2. The server will start and listen on `http://0.0.0.0:5000`.

## API Usage

### POST `/process_prompt`
Send a prompt to the model and receive performance metrics.

#### Example `curl` Command
```bash
curl -X POST http://localhost:5000/process_prompt \
-H "Content-Type: application/json" \
-d '{
    "prompt": "What is the capital of France?"
}'
```

#### Response
The API will return a JSON object containing:
- **Ollama-based metrics**: Total duration, load duration, evaluation duration, etc.
- **Local resource usage**: CPU usage, memory usage, power consumption.
- **Derived metrics**: Tokens per second, energy per token, and more.

---

Feel free to customize the content for your specific repository and use case!
