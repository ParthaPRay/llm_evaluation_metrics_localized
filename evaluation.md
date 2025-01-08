# LLM Evaluation Metrics: A Mathematical Classification

## Introduction
This document classifies and provides mathematical formulations for a wide range of Large Language Model (LLM) evaluation metrics. We reference:

- **Ollama-based metrics** reported by an Ollama-like API (e.g. total duration, load duration, etc.).  
- **Local resource usage metrics** measured on the system (e.g. CPU usage, memory usage, power).  
- **Derived or novel metrics** that combine the above to produce advanced insights (e.g. tokens per second per Watt).

In places, we use integrals and sums to illustrate the concept of continuous vs. sampled measurements. Whenever a true continuous measurement is impractical, a discrete sum (e.g. from `psutil` sampling) is used.

## Notation
- \( N_{\text{eval}} \): Total number of tokens used or generated during model evaluation (`eval_count`).  
- \( N_{\text{prompt}} \): Number of prompt tokens (`prompt_eval_count`).  
- \( T_{\text{total}}^{(\mathrm{ns})} \): Total duration in nanoseconds (`total_duration_ns`).  
- \( T_{\text{load}}^{(\mathrm{ns})} \): Model load duration in nanoseconds (`load_duration_ns`).  
- \( T_{\text{prompt}}^{(\mathrm{ns})} \): Prompt evaluation duration in nanoseconds (`prompt_eval_duration_ns`).  
- \( T_{\text{eval}}^{(\mathrm{ns})} \): Model inference/evaluation duration in nanoseconds (`eval_duration_ns`).  
- \(\bar{P}\): Average power usage (W), derived from sampling (`avg_power_w`).  
- \(P_{\max}\), \(P_{\min}\): Peak and minimum power usage (W) (`peak_power_w`, `min_power_w`).  
- \(\bar{C}\): Average CPU usage (%), from sampling (`avg_cpu_usage_percent`).  
- \(C_{\max}\): Peak CPU usage (%) (`peak_cpu_usage_percent`).  
- \(\bar{M}\): Average RAM usage (MB) (`avg_ram_usage_mb`).  
- \(M_{\max}\): Peak RAM usage (MB) (`peak_ram_usage_mb`).  
- \(T_{\text{local}}\): Total local inference time in seconds, measured from the Python side.

---

## Ollama-Based Core Metrics

### Total Duration
$$
T_{\text{total}}^{(\mathrm{ns})} \quad (\text{nanoseconds})
$$

Optionally expressed in seconds:  
$$
T_{\text{total}}^{(\mathrm{s})} \;=\; \frac{T_{\text{total}}^{(\mathrm{ns})}}{10^9}.
$$

### Load Duration
$$
T_{\text{load}}^{(\mathrm{ns})} \quad (\text{nanoseconds})
$$

### Prompt Evaluation Duration
$$
T_{\text{prompt}}^{(\mathrm{ns})} \quad (\text{nanoseconds})
$$

### Model Evaluation Duration
$$
T_{\text{eval}}^{(\mathrm{ns})} \quad (\text{nanoseconds})
$$

### Token Counts
\[
N_{\text{eval}} = \text{Total tokens processed/generated in eval phase}, \quad
N_{\text{prompt}} = \text{Number of prompt tokens}.
\]

### Tokens per Second (Ollama Throughput)
$$
\text{TPS} 
\;=\; 
\frac{N_{\text{eval}}}{\frac{T_{\text{eval}}^{(\mathrm{ns})}}{10^9}}
\;=\;
\frac{N_{\text{eval}} \times 10^9}{T_{\text{eval}}^{(\mathrm{ns})}}.
$$

---

## Local Resource Usage Metrics

These metrics are measured on the local machine during inference. Typically, repeated samples \(\{ x_i \}\) are collected over the time interval \([0, T_{\text{local}}]\).

### Average and Peak CPU Usage
$$
\bar{C} \;=\; \frac{1}{n} \sum_{i=1}^n C_i,
\quad
C_{\max} \;=\; \max_{1 \leq i \leq n} C_i.
$$

### Average and Peak Memory Usage
$$
\bar{M} \;=\; \frac{1}{n} \sum_{i=1}^n M_i,
\quad
M_{\max} \;=\; \max_{1 \leq i \leq n} M_i.
$$

### Average, Peak, and Minimum Power Usage
$$
\bar{P} \;=\; \frac{1}{n} \sum_{i=1}^n P_i,
\quad
P_{\max} \;=\; \max_{1 \leq i \leq n} P_i,
\quad
P_{\min} \;=\; \min_{1 \leq i \leq n} P_i.
$$

### Standard Deviations (Memory, Power, CPU)
If \(\mu\) is the mean of the samples \(x_i \in \{C_i, M_i, P_i\}\), the sample variance is  
$$
\sigma_x^2 = \frac{1}{n-1} \sum_{i=1}^n (x_i - \mu)^2.
$$  
Hence the standard deviation is  
$$
\sigma_x = \sqrt{\sigma_x^2}.
$$  
In code, we have (for memory, e.g.) \(\sigma_M = \text{mem_std_dev}\), etc.

### Total Energy Approximation
$$
E_{\text{total}} \;=\; \bar{P} \times T_{\text{local}},
$$
assuming constant average power \(\bar{P}\) over the local inference time \(T_{\text{local}}\).

---

## Derived and Novel Metrics (Combining Ollama and Resource Data)

We define below several derived metrics that combine the raw Ollama outputs and the local resource measurements.

### Time per Token
$$
\text{TimePerToken}
\;=\;
\frac{T_{\text{total}}^{(\mathrm{s})}}{N_{\text{eval}}}.
$$
*(In practice, \( T_{\text{total}}^{(\mathrm{s})} = T_{\text{total}}^{(\mathrm{ns})} / 10^9\)).*

### Load-to-Inference Ratio
$$
\text{LoadToInference}
\;=\;
\frac{T_{\text{load}}^{(\mathrm{ns})}}{T_{\text{eval}}^{(\mathrm{ns})}}.
$$

### Memory Usage per Token
$$
\text{MemPerTokenMB}
\;=\;
\frac{\bar{M}}{N_{\text{eval}}}.
$$

### Energy per Token
$$
\text{EnergyPerToken}
\;=\;
\frac{E_{\text{total}}}{N_{\text{eval}}}
\;=\;
\frac{\bar{P} \times T_{\text{local}}}{N_{\text{eval}}}.
$$

### Power Spike
$$
\text{PowerSpike}
\;=\;
P_{\max} - P_{\min}.
$$

### Prompt Evaluation Ratio (Fraction of Total Time)
$$
\text{PromptEvalRatio}
\;=\;
\frac{T_{\text{prompt}}^{(\mathrm{ns})}}{T_{\text{total}}^{(\mathrm{ns})}}.
$$

### Prompt-to-Generation Overhead Ratio
$$
\text{PromptToGenerationOverhead}
\;=\;
\frac{T_{\text{prompt}}^{(\mathrm{ns})}}{T_{\text{eval}}^{(\mathrm{ns})}}.
$$

### Power Efficiency Index (TPS per Watt)
$$
\text{PowerEfficiencyIndex}
\;=\;
\frac{\text{TPS}}{\bar{P}}
\;=\;
\frac{
   \frac{N_{\text{eval}}}{\bigl(T_{\text{eval}}^{(\mathrm{ns})}/10^9\bigr)}
}{
   \bar{P}
}.
$$

### CPU Stability Index
Define \(\sigma_C\) as the standard deviation of CPU usage samples and  
$$
\denom_{\text{CPU}} = \max(100, \bar{C}),
$$
then
$$
\text{CPUStabilityIndex}
\;=\;
1 - \frac{\sigma_C}{\denom_{\text{CPU}}}.
$$
Values below \(0\) are clamped to \(0\).

### Model Efficiency Index
$$
\text{ModelEfficiencyIndex}
\;=\;
\frac{\text{TPS}}{M_{\max}}.
$$
That is, tokens per second divided by peak memory usage (MB).

### Peak CPU to Average Ratio
$$
\text{PeakCPUtoAvgRatio}
\;=\;
\frac{C_{\max}}{\bar{C}}.
$$

### Memory Variation Index
$$
\text{MemVariationIndex}
\;=\;
\frac{\sigma_M}{\bar{M}}.
$$

### Peak Power to Average Power Ratio
$$
\text{PeakPowerToAvgPowerRatio}
\;=\;
\frac{P_{\max}}{\bar{P}}.
$$

### Prompt Evaluation Tokens per Second
$$
\text{PromptEvalTPS}
\;=\;
\frac{N_{\text{prompt}}}{\bigl(T_{\text{prompt}}^{(\mathrm{ns})}/10^9\bigr)}.
$$

### Evaluation Latency per Token
$$
\text{EvalLatencyPerToken}
\;=\;
\frac{T_{\text{eval}}^{(\mathrm{ns})}}{N_{\text{eval}}}.
$$

### Evaluation Memory Efficiency
$$
\text{EvalMemoryEfficiency}
\;=\;
\frac{\text{TPS}}{\bar{M}}.
$$

### Token Production Energy Efficiency
$$
\text{TokenProductionEnergyEff}
\;=\;
\frac{N_{\text{eval}}}{\bar{P} \times T_{\text{local}}}.
$$
*(The inverse of \(\text{EnergyPerToken}\).)*

### Average CPU to Power Ratio
$$
\text{AvgCPUtoPowerRatio}
\;=\;
\frac{\bar{C}}{\bar{P}}.
$$

### Peak RAM to Peak CPU Ratio
$$
\text{PeakRAMtoPeakCPU}
\;=\;
\frac{M_{\max}}{C_{\max}}.
$$

### Time-Weighted Power Factor
$$
\text{TimeWeightedPowerFactor}
\;=\;
\frac{\bar{P}}{T_{\text{local}}}.
$$

### Load to Prompt Ratio
$$
\text{LoadToPromptRatio}
\;=\;
\frac{T_{\text{load}}^{(\mathrm{ns})}}{T_{\text{prompt}}^{(\mathrm{ns})}}.
$$

### Prompt to Total Token Ratio
$$
\text{PromptToTotalTokenRatio}
\;=\;
\frac{N_{\text{prompt}}}{N_{\text{eval}}}.
$$

### Memory to CPU Ratio (Peak Values)
$$
\text{MemoryToCPUratio}
\;=\;
\frac{M_{\max}}{C_{\max}}.
$$

### Memory to Power Ratio
$$
\text{MemoryToPowerRatio}
\;=\;
\frac{\bar{M}}{\bar{P}}.
$$

### RAM Usage Variation Index
$$
\text{RAMUsageVariationIndex}
\;=\;
\frac{\sigma_M}{\bar{M}}.
$$
*(Synonym of Memory Variation Index in some contexts.)*

### Power Usage Variation Index
$$
\text{PowerUsageVariationIndex}
\;=\;
\frac{\sigma_P}{\bar{P}}.
$$

### Sustained Inference Factor
$$
\text{SustainedInferenceFactor}
\;=\;
\left(\frac{N_{\text{eval}}}{N_{\text{prompt}} + N_{\text{eval}}}\right)
\times
\left(\frac{\text{TPS}}{\bar{P}}\right).
$$

### Thermal Load Factor
$$
\text{ThermalLoadFactor}
\;=\;
\frac{\frac{\bar{C} + C_{\max}}{2}}{\bar{P}}.
$$

---

## Conclusion
These metrics provide a multi-faceted view of LLM performance, combining Ollama-based timing/token metrics with locally measured CPU, memory, and power usage. By applying fundamental mathematical operations (ratios, integrals, standard deviations), users can derive in-depth performance profiles for any given model or hardware configuration.
