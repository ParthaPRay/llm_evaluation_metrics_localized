# Localized LLM evaluation Metrics
# Partha Pratim Ray
# 8/1/2025
# parthapratimray1986@gmail.com

##### Modify base_power and max_power of your device ######
# base_power = 2.7
# max_power = 6.7
###########################################################

# curl -X POST http://localhost:5000/process_prompt \
#      -H "Content-Type: application/json" \
#      -d '{ "prompt": "What is capital of India?" }'

import psutil
import threading
import time
import requests
import logging
from math import sqrt
from flask import Flask, request, jsonify

import csv
import os
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

###############################################################################
# MODEL SETTINGS
###############################################################################
MODEL_NAME = "qwen2.5:0.5b-instruct-q8_0"

CSV_FILENAME = "metrics_log.csv"

###############################################################################
# ResourceMonitor
###############################################################################
class ResourceMonitor:
    """
    Monitors system-wide CPU usage, memory usage, and approximates power consumption.
    Gathers arrays so we can compute standard deviations, peaks, etc.
    """
    def __init__(self, interval=1.0):
        self.interval = interval
        self.running = False

        self.cpu_usage_readings = []
        self.mem_usage_readings = []
        self.power_readings = []

        self.monitor_thread = None

    def start(self):
        self.running = True
        psutil.cpu_percent(interval=None)  # warm-up
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def _monitor(self):
        while self.running:
            try:
                cpu_percent = psutil.cpu_percent(interval=None)
                self.cpu_usage_readings.append(cpu_percent)

                mem_info = psutil.virtual_memory()
                used_mb = (mem_info.total - mem_info.available) / (1024**2)
                self.mem_usage_readings.append(used_mb)

                # approximate power based on CPU usage
                power_w = self._estimate_power(cpu_percent)
                self.power_readings.append(power_w)

                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")

    @staticmethod
    def _estimate_power(cpu_percent):
        """
        Approximate system power (Watts) from CPU usage on a Pi-like device.
        Adjust base_power and max_power if you have real measurements.
        """
        base_power = 2.7
        max_power = 6.7
        return base_power + (max_power - base_power)*(cpu_percent/100)

    # ----------- Accessors -----------
    def get_cpu_usage_array(self):
        return self.cpu_usage_readings

    def get_avg_cpu(self):
        if not self.cpu_usage_readings:
            return 0
        return sum(self.cpu_usage_readings) / len(self.cpu_usage_readings)

    def get_peak_cpu(self):
        return max(self.cpu_usage_readings) if self.cpu_usage_readings else 0

    def get_avg_mem_mb(self):
        if not self.mem_usage_readings:
            return 0
        return sum(self.mem_usage_readings) / len(self.mem_usage_readings)

    def get_peak_mem_mb(self):
        return max(self.mem_usage_readings) if self.mem_usage_readings else 0

    def get_avg_power(self):
        if not self.power_readings:
            return 0
        return sum(self.power_readings) / len(self.power_readings)

    def get_peak_power(self):
        return max(self.power_readings) if self.power_readings else 0

    def get_min_power(self):
        return min(self.power_readings) if self.power_readings else 0

    def get_std_dev_memory(self):
        if len(self.mem_usage_readings) < 2:
            return 0
        avg_m = self.get_avg_mem_mb()
        var_m = sum((m - avg_m)**2 for m in self.mem_usage_readings)/(len(self.mem_usage_readings)-1)
        return sqrt(var_m)

    def get_std_dev_power(self):
        if len(self.power_readings) < 2:
            return 0
        avg_p = self.get_avg_power()
        var_p = sum((p - avg_p)**2 for p in self.power_readings)/(len(self.power_readings)-1)
        return sqrt(var_p)

###############################################################################
# CSV Logging Utilities
###############################################################################
def log_metrics_to_csv(
    timestamp_str,
    model_name,
    prompt,
    response_text,
    ollama_metrics,
    resource_usage,
    all_novel_metrics
):
    """
    Appends a single row to a CSV file with all relevant metrics.
    The columns (fieldnames) are defined in a fixed order.
    """

    # Combine all metrics into one dict for easy CSV writing
    row_data = {}
    row_data["timestamp"] = timestamp_str
    row_data["model"] = model_name
    row_data["prompt"] = prompt
    row_data["response"] = response_text

    # Ollama-based metrics
    for k, v in ollama_metrics.items():
        row_data[k] = v

    # Resource usage metrics
    for k, v in resource_usage.items():
        row_data[k] = v

    # Novel derived metrics
    for k, v in all_novel_metrics.items():
        row_data[k] = v

    # Define a consistent column order
    fieldnames = list(row_data.keys())

    # Write or append to CSV
    file_exists = os.path.isfile(CSV_FILENAME)
    with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # If file is new, write header
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_data)

###############################################################################
# /process_prompt ENDPOINT
###############################################################################
@app.route('/process_prompt', methods=['POST'])
def process_prompt():
    data = request.get_json() or {}
    prompt = data.get("prompt")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    api_url = "http://localhost:11434/api/generate"
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    # Start monitoring
    monitor = ResourceMonitor(interval=1.0)
    monitor.start()

    start_time = time.time()
    response = requests.post(api_url, json=payload)
    end_time = time.time()

    # Stop monitoring
    monitor.stop()

    if response.status_code != 200:
        return jsonify({
            "error": f"LLM API Error: {response.status_code}",
            "details": response.text
        }), response.status_code

    # -------------------------------------------------------------------------
    # 1) Parse Ollama-Based Metrics
    # -------------------------------------------------------------------------
    result_data = response.json()

    # Attempt to capture the text or "response" from the JSON
    # (Modify this key if your local API uses a different one, e.g. "output")
    llm_response_text = result_data.get("response", "")  # or "result_data.get('output', '')"

    total_duration_ns = result_data.get("total_duration", 0)
    load_duration_ns = result_data.get("load_duration", 0)
    prompt_eval_duration_ns = result_data.get("prompt_eval_duration", 0)
    model_eval_duration_ns = result_data.get("eval_duration", 0)
    eval_count = result_data.get("eval_count", 0)
    prompt_eval_count = result_data.get("prompt_eval_count", 0)  # if available

    total_duration_s = total_duration_ns / 1e9
    tokens_per_second = 0
    if model_eval_duration_ns > 0:
        tokens_per_second = (eval_count / model_eval_duration_ns) * 1e9

    ollama_metrics = {
        "total_duration_ns": total_duration_ns,
        "total_duration_s": total_duration_s,
        "load_duration_ns": load_duration_ns,
        "prompt_eval_duration_ns": prompt_eval_duration_ns,
        "eval_duration_ns": model_eval_duration_ns,
        "eval_count": eval_count,
        "tokens_per_second": tokens_per_second
    }

    # -------------------------------------------------------------------------
    # 2) Local Resource Usage Dictionary
    # -------------------------------------------------------------------------
    resource_usage = {
        "avg_cpu_usage_percent": monitor.get_avg_cpu(),
        "peak_cpu_usage_percent": monitor.get_peak_cpu(),
        "avg_ram_usage_mb": monitor.get_avg_mem_mb(),
        "peak_ram_usage_mb": monitor.get_peak_mem_mb(),
        "avg_power_w": monitor.get_avg_power(),
        "peak_power_w": monitor.get_peak_power(),
        "min_power_w": monitor.get_min_power(),
        "mem_std_dev": monitor.get_std_dev_memory(),
        "power_std_dev": monitor.get_std_dev_power(),
    }

    local_inference_time_s = end_time - start_time
    total_energy_j = resource_usage["avg_power_w"] * local_inference_time_s

    # -------------------------------------------------------------------------
    # B) Derived "Novel" Metrics
    # -------------------------------------------------------------------------
    time_per_token_s = 0
    if eval_count > 0:
        time_per_token_s = total_duration_s / eval_count

    load_to_inference_ratio = 0
    if model_eval_duration_ns > 0:
        load_to_inference_ratio = load_duration_ns / model_eval_duration_ns

    memory_usage_per_token_mb = 0
    if eval_count > 0:
        memory_usage_per_token_mb = resource_usage["avg_ram_usage_mb"] / eval_count

    energy_per_token_j = 0
    if eval_count > 0:
        energy_per_token_j = total_energy_j / eval_count

    power_spike_w = resource_usage["peak_power_w"] - resource_usage["min_power_w"]

    prompt_eval_ratio = 0
    if total_duration_ns > 0:
        prompt_eval_ratio = prompt_eval_duration_ns / total_duration_ns

    prompt_to_generation_overhead_ratio = 0
    if model_eval_duration_ns > 0:
        prompt_to_generation_overhead_ratio = prompt_eval_duration_ns / model_eval_duration_ns

    power_efficiency_index = 0
    if resource_usage["avg_power_w"] > 0:
        power_efficiency_index = tokens_per_second / resource_usage["avg_power_w"]

    cpu_usage_array = monitor.get_cpu_usage_array()
    cpu_stddev = 0
    if len(cpu_usage_array) > 1:
        mu_cpu = sum(cpu_usage_array)/len(cpu_usage_array)
        var_cpu = sum((x - mu_cpu)**2 for x in cpu_usage_array) / (len(cpu_usage_array)-1)
        cpu_stddev = sqrt(var_cpu)

    denom_for_stability = max(100, resource_usage["avg_cpu_usage_percent"])
    cpu_stability_index = 1 - (cpu_stddev / denom_for_stability)
    if cpu_stability_index < 0:
        cpu_stability_index = 0

    model_efficiency_index = 0
    if resource_usage["peak_ram_usage_mb"] > 0:
        model_efficiency_index = tokens_per_second / resource_usage["peak_ram_usage_mb"]

    peak_cpu_to_average_ratio = 0
    if resource_usage["avg_cpu_usage_percent"] > 0:
        peak_cpu_to_average_ratio = (
            resource_usage["peak_cpu_usage_percent"] /
            resource_usage["avg_cpu_usage_percent"]
        )

    memory_variation_index = 0
    if (
        resource_usage["avg_ram_usage_mb"] > 0 and
        resource_usage["mem_std_dev"] > 0
    ):
        memory_variation_index = (
            resource_usage["mem_std_dev"] /
            resource_usage["avg_ram_usage_mb"]
        )

    peak_power_to_average_power_ratio = 0
    if resource_usage["avg_power_w"] > 0:
        peak_power_to_average_power_ratio = (
            resource_usage["peak_power_w"] /
            resource_usage["avg_power_w"]
        )

    prompt_eval_tokens_per_s = 0
    if prompt_eval_duration_ns > 0 and prompt_eval_count > 0:
        prompt_eval_tokens_per_s = prompt_eval_count / (prompt_eval_duration_ns / 1e9)

    eval_latency_per_token_ns = 0
    if eval_count > 0:
        eval_latency_per_token_ns = model_eval_duration_ns / eval_count

    eval_memory_efficiency = 0
    if resource_usage["avg_ram_usage_mb"] > 0:
        eval_memory_efficiency = tokens_per_second / resource_usage["avg_ram_usage_mb"]

    token_production_energy_efficiency = 0
    if total_energy_j > 1e-9:
        token_production_energy_efficiency = eval_count / total_energy_j

    avg_cpu_to_power_ratio = 0
    if resource_usage["avg_power_w"] > 0:
        avg_cpu_to_power_ratio = (
            resource_usage["avg_cpu_usage_percent"] /
            resource_usage["avg_power_w"]
        )

    peak_ram_to_peak_cpu_ratio = 0
    if resource_usage["peak_cpu_usage_percent"] > 0:
        peak_ram_to_peak_cpu_ratio = (
            resource_usage["peak_ram_usage_mb"] /
            resource_usage["peak_cpu_usage_percent"]
        )

    time_weighted_power_factor = 0
    if local_inference_time_s > 0:
        time_weighted_power_factor = (
            resource_usage["avg_power_w"] /
            local_inference_time_s
        )

    load_to_prompt_ratio = 0
    if prompt_eval_duration_ns > 0:
        load_to_prompt_ratio = load_duration_ns / prompt_eval_duration_ns

    prompt_to_total_token_ratio = 0
    if eval_count > 0:
        prompt_to_total_token_ratio = prompt_eval_count / eval_count

    memory_to_cpu_ratio = 0
    if resource_usage["peak_cpu_usage_percent"] > 0:
        memory_to_cpu_ratio = (
            resource_usage["peak_ram_usage_mb"] /
            resource_usage["peak_cpu_usage_percent"]
        )

    memory_to_power_ratio = 0
    if resource_usage["avg_power_w"] > 0:
        memory_to_power_ratio = (
            resource_usage["avg_ram_usage_mb"] /
            resource_usage["avg_power_w"]
        )

    ram_usage_variation_index = 0
    if (
        resource_usage["avg_ram_usage_mb"] > 0 and
        resource_usage["mem_std_dev"] > 0
    ):
        ram_usage_variation_index = (
            resource_usage["mem_std_dev"] /
            resource_usage["avg_ram_usage_mb"]
        )

    power_usage_variation_index = 0
    if (
        resource_usage["avg_power_w"] > 0 and
        resource_usage["power_std_dev"] > 0
    ):
        power_usage_variation_index = (
            resource_usage["power_std_dev"] /
            resource_usage["avg_power_w"]
        )

    denom_nt = prompt_eval_count + eval_count
    if denom_nt <= 0:
        denom_nt = 1
    ratio_new_tokens = eval_count / denom_nt
    power_eff = 0
    if resource_usage["avg_power_w"] > 0:
        power_eff = tokens_per_second / resource_usage["avg_power_w"]
    sustained_inference_factor = ratio_new_tokens * power_eff

    thermal_load_factor = 0
    if resource_usage["avg_power_w"] > 0:
        combined_cpu = (
            resource_usage["avg_cpu_usage_percent"] +
            resource_usage["peak_cpu_usage_percent"]
        ) / 2.0
        thermal_load_factor = combined_cpu / resource_usage["avg_power_w"]

    all_novel_metrics = {
        "time_per_token_s": time_per_token_s,
        "load_to_inference_ratio": load_to_inference_ratio,
        "memory_usage_per_token_mb": memory_usage_per_token_mb,
        "energy_per_token_j": energy_per_token_j,
        "power_spike_w": power_spike_w,
        "prompt_eval_ratio": prompt_eval_ratio,
        "time_per_prompt_eval_ns": prompt_eval_duration_ns,

        "prompt_to_generation_overhead_ratio": prompt_to_generation_overhead_ratio,
        "power_efficiency_index_tps_per_w": power_efficiency_index,
        "cpu_stability_index": cpu_stability_index,

        "model_efficiency_index": model_efficiency_index,
        "peak_cpu_to_average_ratio": peak_cpu_to_average_ratio,
        "memory_variation_index": memory_variation_index,
        "peak_power_to_average_power_ratio": peak_power_to_average_power_ratio,
        "prompt_eval_tokens_per_s": prompt_eval_tokens_per_s,
        "eval_latency_per_token_ns": eval_latency_per_token_ns,
        "eval_memory_efficiency": eval_memory_efficiency,
        "token_production_energy_efficiency": token_production_energy_efficiency,
        "avg_cpu_to_power_ratio": avg_cpu_to_power_ratio,
        "peak_ram_to_peak_cpu_ratio": peak_ram_to_peak_cpu_ratio,

        "time_weighted_power_factor": time_weighted_power_factor,
        "load_to_prompt_ratio": load_to_prompt_ratio,
        "prompt_to_total_token_ratio": prompt_to_total_token_ratio,
        "memory_to_cpu_ratio": memory_to_cpu_ratio,
        "memory_to_power_ratio": memory_to_power_ratio,
        "ram_usage_variation_index": ram_usage_variation_index,
        "power_usage_variation_index": power_usage_variation_index,
        "sustained_inference_factor": sustained_inference_factor,
        "thermal_load_factor": thermal_load_factor
    }

    # -------------------------------------------------------------------------
    # Log everything to CSV
    # -------------------------------------------------------------------------
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log to CSV
    log_metrics_to_csv(
        timestamp_str=timestamp_str,
        model_name=MODEL_NAME,
        prompt=prompt,
        response_text=llm_response_text,
        ollama_metrics=ollama_metrics,
        resource_usage=resource_usage,
        all_novel_metrics=all_novel_metrics
    )

    # -------------------------------------------------------------------------
    # Final JSON response
    # -------------------------------------------------------------------------
    response_data = {
        "ollama_metrics": ollama_metrics,
        "resource_usage": resource_usage,
        "all_novel_metrics": all_novel_metrics,
        "model_response": llm_response_text
    }

    return jsonify(response_data)


###############################################################################
# MAIN
###############################################################################
if __name__ == '__main__':
    logger.info(f"Starting Flask server with model: {MODEL_NAME}")
    app.run(host='0.0.0.0', port=5000)
