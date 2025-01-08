# Localized LLM evaluation Metrics TEST CODE
# Partha Pratim Ray
# 8/1/2025
# parthapratimray1986@gmail.com

# First run python llm_metrics_11.py in oner terminal

# Then run this code from other terminal in same directory


###########################################################

import requests
import time
import random

def hit_endpoint(base_url, prompts):
    """
    Hit the API endpoint with a variety of prompts.
    """
    results = []

    for prompt in prompts:
        payload = {"prompt": prompt}

        try:
            print(f"Sending prompt: {prompt}")
            start_time = time.time()
            response = requests.post(f"{base_url}/process_prompt", json=payload)
            end_time = time.time()

            if response.status_code == 200:
                result = response.json()
                result["elapsed_time"] = end_time - start_time
                results.append(result)
                print(f"Response received in {result['elapsed_time']:.2f}s: {result['model_response'][:100]}...")
            else:
                print(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"Error during request: {e}")

        time.sleep(1)  # Pause between requests to avoid overwhelming the server

    return results

def generate_prompts():
    """
    Generate a list of diverse NLP tasks for testing.
    """
    prompts = [
        # General Knowledge
        "What is the capital of France?",

        # Summarization
        "Summarize the following text: The industrial revolution was a period of major industrialization...",

        # Creative Writing
        "Write a short poem about the beauty of nature.",

        # Sentiment Analysis
        "Classify the sentiment: 'I absolutely loved the new restaurant!'",

        # Text Completion
        "Complete this sentence: The quick brown fox jumps over...",

        # Translation
        "Translate to French: 'Good morning, how are you?'",

        # Coding Assistance
        "Write a Python function to calculate the factorial of a number.",

        # Edge Device Suitability
        "Explain the benefits of Raspberry Pi in IoT applications.",

        # Mathematical Queries
        "What is the square root of 256?",

        # Conversational
        "Pretend to be a travel assistant. Suggest some attractions in Paris for a family vacation.",
    ]
    return prompts

def main():
    base_url = "http://localhost:5000"
    prompts = generate_prompts()
    results = hit_endpoint(base_url, prompts)

    # Save results to a file (optional)
    with open("llm_test_results.json", "w", encoding="utf-8") as f:
        import json
        json.dump(results, f, ensure_ascii=False, indent=4)

    print("\nTest completed. Results saved to 'llm_test_results.json'.")

if __name__ == "__main__":
    main()
