# llm_evaluation_metrics_localized
This repo contains codes localized llm evaluation metrics

This sentence uses `$` delimiters to show math inline: $\sqrt{3x-1}+(1+x)^2$

# Classification and Mathematical Representation of Metrics

## **1. Performance Metrics**
These metrics measure how efficiently the model performs in terms of time and throughput.

### **1.1. Latency Metrics**
- **Total Duration (Seconds)**:
  \[
  T_{\text{total}} = \frac{\text{total\_duration\_ns}}{10^9}
  \]

- **Time Per Token (Seconds)**:
  \[
  T_{\text{token}} = \frac{T_{\text{total}}}{\text{eval\_count}} \quad \text{if } \text{eval\_count} > 0
  \]

- **Prompt Evaluation Duration (Nanoseconds)**:
  \[
  T_{\text{prompt\_eval}} = \text{prompt\_eval\_duration\_ns}
  \]

- **Evaluation Latency Per Token (Nanoseconds)**:
  \[
  T_{\text{eval\_latency\_per\_token}} = \frac{\text{model\_eval\_duration\_ns}}{\text{eval\_count}} \quad \text{if } \text{eval\_count} > 0
  \]

### **1.2. Throughput Metrics**
- **Tokens Per Second**:
  \[
  \text{TPS} = \frac{\text{eval\_count}}{\text{model\_eval\_duration\_ns}/10^9} \quad \text{if } \text{model\_eval\_duration\_ns} > 0
  \]

- **Prompt Evaluation Tokens Per Second**:
  \[
  \text{TPS}_{\text{prompt}} = \frac{\text{prompt\_eval\_count}}{T_{\text{prompt\_eval}} / 10^9} \quad \text{if } T_{\text{prompt\_eval}} > 0
  \]

---

## **2. Resource Utilization Metrics**
These metrics focus on the utilization of system resources during inference.

### **2.1. CPU Metrics**
- **Average CPU Usage (%)**:
  \[
  \text{CPU}_{\text{avg}} = \text{mean}(\text{cpu\_usage\_readings})
  \]

- **Peak CPU Usage (%)**:
  \[
  \text{CPU}_{\text{peak}} = \max(\text{cpu\_usage\_readings})
  \]

- **CPU Stability Index**:
  \[
  \text{CSI} = 1 - \frac{\sigma_{\text{CPU}}}{\max(100, \text{CPU}_{\text{avg}})}
  \]
  where:
  \[
  \sigma_{\text{CPU}} = \sqrt{\frac{\sum (\text{cpu\_usage\_readings} - \mu_{\text{CPU}})^2}{n - 1}}
  \]

### **2.2. Memory Metrics**
- **Average RAM Usage (MB)**:
  \[
  \text{RAM}_{\text{avg}} = \text{mean}(\text{mem\_usage\_readings})
  \]

- **Peak RAM Usage (MB)**:
  \[
  \text{RAM}_{\text{peak}} = \max(\text{mem\_usage\_readings})
  \]

- **Memory Variation Index**:
  \[
  \text{MVI} = \frac{\sigma_{\text{RAM}}}{\text{RAM}_{\text{avg}}}
  \]
  where:
  \[
  \sigma_{\text{RAM}} = \sqrt{\frac{\sum (\text{mem\_usage\_readings} - \mu_{\text{RAM}})^2}{n - 1}}
  \]

### **2.3. Power Metrics**
- **Average Power Consumption (Watts)**:
  \[
  P_{\text{avg}} = \text{mean}(\text{power\_readings})
  \]

- **Peak Power Consumption (Watts)**:
  \[
  P_{\text{peak}} = \max(\text{power\_readings})
  \]

- **Power Spike (Watts)**:
  \[
  P_{\text{spike}} = P_{\text{peak}} - P_{\text{min}}
  \]

- **Power Usage Variation Index**:
  \[
  \text{PVI} = \frac{\sigma_{\text{Power}}}{P_{\text{avg}}}
  \]
  where:
  \[
  \sigma_{\text{Power}} = \sqrt{\frac{\sum (\text{power\_readings} - \mu_{\text{Power}})^2}{n - 1}}
  \]

---

## **3. Efficiency Metrics**
These metrics capture the relationship between resource usage and model output.

### **3.1. Energy Efficiency**
- **Energy Per Token (Joules)**:
  \[
  E_{\text{token}} = \frac{E_{\text{total}}}{\text{eval\_count}} \quad \text{where } E_{\text{total}} = P_{\text{avg}} \cdot T_{\text{local\_inference}}
  \]

### **3.2. Computational Efficiency**
- **Memory Usage Per Token (MB)**:
  \[
  \text{MEM}_{\text{token}} = \frac{\text{RAM}_{\text{avg}}}{\text{eval\_count}}
  \]

- **Evaluation Memory Efficiency**:
  \[
  \text{EME} = \frac{\text{TPS}}{\text{RAM}_{\text{avg}}}
  \]

### **3.3. Power Efficiency**
- **Power Efficiency Index (TPS/Watt)**:
  \[
  \text{PEI} = \frac{\text{TPS}}{P_{\text{avg}}}
  \]

### **3.4. Model Efficiency**
- **Model Efficiency Index**:
  \[
  \text{MEI} = \frac{\text{TPS}}{\text{RAM}_{\text{peak}}}
  \]

---

## **4. Evaluation Dynamics Metrics**
These metrics explore interactions between different stages of inference.

### **4.1. Temporal Ratios**
- **Load to Inference Ratio**:
  \[
  \text{LIR} = \frac{\text{load\_duration\_ns}}{\text{model\_eval\_duration\_ns}}
  \]

- **Load to Prompt Ratio**:
  \[
  \text{LPR} = \frac{\text{load\_duration\_ns}}{T_{\text{prompt\_eval}}}
  \]

- **Prompt Evaluation Ratio**:
  \[
  \text{PER} = \frac{T_{\text{prompt\_eval}}}{T_{\text{total}}}
  \]

- **Prompt to Total Token Ratio**:
  \[
  \text{PTR} = \frac{\text{prompt\_eval\_count}}{\text{eval\_count}}
  \]

### **4.2. Overhead Analysis**
- **Prompt-to-Generation Overhead Ratio**:
  \[
  \text{PGOR} = \frac{T_{\text{prompt\_eval}}}{\text{model\_eval\_duration\_ns}}
  \]

---

## **5. Stability and Variability Metrics**
These focus on system-level consistency.

- **Peak-to-Average CPU Ratio**:
  \[
  \text{CPU}_{\text{peak\_avg}} = \frac{\text{CPU}_{\text{peak}}}{\text{CPU}_{\text{avg}}}
  \]

- **Peak Power to Average Power Ratio**:
  \[
  P_{\text{peak\_avg}} = \frac{P_{\text{peak}}}{P_{\text{avg}}}
  \]

---

## **6. Advanced Meta-Metrics**
These combine multiple aspects of the evaluation.

- **Thermal Load Factor**:
  \[
  \text{TLF} = \frac{\frac{\text{CPU}_{\text{avg}} + \text{CPU}_{\text{peak}}}{2}}{P_{\text{avg}}}
  \]

- **Sustained Inference Factor**:
  \[
  \text{SIF} = \left(\frac{\text{eval\_count}}{\text{eval\_count} + \text{prompt\_eval\_count}}\right) \cdot \text{PEI}
  \]

---

## **7. Additional Metrics**
These metrics provide further insights into the behavior and efficiency of the system.

### **7.1. Ratios and Factors**
- **Time Weighted Power Factor**:
  \[
  \text{TWPF} = \frac{P_{\text{avg}}}{T_{\text{local\_inference}}}
  \]

- **Load to Prompt Ratio**:
  \[
  \text{LPR} = \frac{\text{load\_duration\_ns}}{T_{\text{prompt\_eval}}}
  \]

- **Prompt to Total Token Ratio**:
  \[
  \text{PTR} = \frac{\text{prompt\_eval\_count}}{\text{eval\_count}}
  \]

- **Memory to CPU Ratio**:
  \[
  \text{MCR} = \frac{\text{RAM}_{\text{peak}}}{\text{CPU}_{\text{peak}}}
  \]

- **Memory to Power Ratio**:
  \[
  \text{MPR} = \frac{\text{RAM}_{\text{avg}}}{P_{\text{avg}}}
  \]

- **RAM Usage Variation Index**:
  \[
  \text{RVI} = \frac{\sigma_{\text{RAM}}}{\text{RAM}_{\text{avg}}}
  \]

- **Power Usage Variation Index**:
  \[
  \text{PVI} = \frac{\sigma_{\text{Power}}}{P_{\text{avg}}}
  \]

- **Peak RAM to Peak CPU Ratio**:
  \[
  \text{PRCR} = \frac{\text{RAM}_{\text{peak}}}{\text{CPU}_{\text{peak}}}
  \]

---

### **7.2. Efficiency and Stability Metrics**
- **Token Production Energy Efficiency**:
  \[
  \text{TPEE} = \frac{\text{eval\_count}}{E_{\text{total}}} \quad \text{if } E_{\text{total}} > 0
  \]

- **Average CPU to Power Ratio**:
  \[
  \text{ACPR} = \frac{\text{CPU}_{\text{avg}}}{P_{\text{avg}}}
  \]

- **Sustained Inference Factor**:
  \[
  \text{SIF} = \left(\frac{\text{eval\_count}}{\text{eval\_count} + \text{prompt\_eval\_count}}\right) \cdot \text{PEI}
  \]

- **Thermal Load Factor**:
  \[
  \text{TLF} = \frac{\frac{\text{CPU}_{\text{avg}} + \text{CPU}_{\text{peak}}}{2}}{P_{\text{avg}}}
  \]

---

### **7.3. Dynamic Metrics**
These metrics reflect real-time interactions and variability during inference.

- **Prompt-to-Generation Overhead Ratio**:
  \[
  \text{PGOR} = \frac{T_{\text{prompt\_eval}}}{\text{model\_eval\_duration\_ns}}
  \]

- **Load to Inference Ratio**:
  \[
  \text{LIR} = \frac{\text{load\_duration\_ns}}{\text{model\_eval\_duration\_ns}}
  \]

- **Peak Power to Average Power Ratio**:
  \[
  P_{\text{peak\_avg}} = \frac{P_{\text{peak}}}{P_{\text{avg}}}
  \]

---

## **Summary of Classification**
The metrics have been systematically grouped into categories for clarity and analysis:
1. **Performance Metrics**: Measure latency and throughput.
2. **Resource Utilization Metrics**: Focus on CPU, memory, and power usage.
3. **Efficiency Metrics**: Explore energy, computational, and power efficiency.
4. **Evaluation Dynamics Metrics**: Analyze temporal and stage interactions.
5. **Stability and Variability Metrics**: Address system consistency.
6. **Advanced Meta-Metrics**: Combine multiple aspects for higher-order insights.
7. **Additional Metrics**: Provide further granularity on resource dynamics.

Each metric is defined mathematically, ensuring precision and technical depth for localized LLM evaluation in resource-constrained environments.


---
