\section{Ollama-Based Core Metrics}
The Ollama-like API reports the following metrics in raw form:

\subsection{Total Duration}
\begin{equation}
T_{\text{total}}^{(\mathrm{ns})} \quad \text{(nanoseconds)}
\end{equation}
Optionally expressed in seconds: 
\[
T_{\text{total}}^{(\mathrm{s})} = \frac{T_{\text{total}}^{(\mathrm{ns})}}{10^9}.
\]

\subsection{Load Duration}
\begin{equation}
T_{\text{load}}^{(\mathrm{ns})} \quad\text{(nanoseconds)}
\end{equation}

\subsection{Prompt Evaluation Duration}
\begin{equation}
T_{\text{prompt}}^{(\mathrm{ns})} \quad\text{(nanoseconds)}
\end{equation}

\subsection{Model Evaluation Duration}
\begin{equation}
T_{\text{eval}}^{(\mathrm{ns})} \quad\text{(nanoseconds)}
\end{equation}

\subsection{Token Counts}
\begin{align}
N_{\text{eval}} &= \text{Total tokens processed/generated in eval phase},\\
N_{\text{prompt}} &= \text{Number of prompt tokens}.
\end{align}

\subsection{Tokens per Second (Ollama Throughput)}
\begin{equation}
\text{TPS} 
= 
\frac{N_{\text{eval}}}{T_{\text{eval}}^{(\mathrm{ns})}/10^9}
= 
\frac{N_{\text{eval}} \times 10^9}{T_{\text{eval}}^{(\mathrm{ns})}}.
\end{equation}
\noindent
This is often reported as ``\texttt{tokens\_per\_second}''.

\vspace{1em}

\section{Local Resource Usage Metrics}
These metrics are measured on the local machine during inference. Typically, repeated samples $\{ x_i \}$ are collected over the time interval $[0, T_{\text{local}}]$.

\subsection{Average and Peak CPU Usage}
\begin{align}
\bar{C} &= \frac{1}{n} \sum_{i=1}^n C_i, \\
C_{\max} &= \max_{1 \leq i \leq n} C_i.
\end{align}

\subsection{Average and Peak Memory Usage}
\begin{align}
\bar{M} &= \frac{1}{n} \sum_{i=1}^n M_i, \\
M_{\max} &= \max_{1 \leq i \leq n} M_i.
\end{align}

\subsection{Average, Peak, and Minimum Power Usage}
\begin{align}
\bar{P} &= \frac{1}{n} \sum_{i=1}^n P_i, \\
P_{\max} &= \max_{1 \leq i \leq n} P_i, \quad
P_{\min} = \min_{1 \leq i \leq n} P_i.
\end{align}

\subsection{Standard Deviations (Memory, Power, CPU)}
If $\mu$ is the mean of the samples $x_i \in \{C_i, M_i, P_i\}$, the sample variance is:
\[
\sigma_x^2 = \frac{1}{n-1} \sum_{i=1}^n (x_i - \mu)^2.
\]
Hence the standard deviation is
\[
\sigma_x = \sqrt{\sigma_x^2}.
\]
In code, we have (for memory, e.g.) $\sigma_M = \text{mem\_std\_dev}$, etc.

\subsection{Total Energy Approximation}
\begin{equation}
E_{\text{total}} = \bar{P} \times T_{\text{local}}, 
\end{equation}
assuming constant average power $\bar{P}$ over the local inference time $T_{\text{local}}$.

\vspace{1em}

\section{Derived and Novel Metrics (Combining Ollama and Resource Data)}
We define below several derived metrics that combine the raw Ollama outputs and the local resource measurements:

\subsection{Time per Token}
\begin{equation}
\text{TimePerToken} = \frac{T_{\text{total}}^{(\mathrm{s})}}{N_{\text{eval}}}.
\end{equation}
In practice, $T_{\text{total}}^{(\mathrm{s})} = T_{\text{total}}^{(\mathrm{ns})}/10^9$.

\subsection{Load-to-Inference Ratio}
\begin{equation}
\text{LoadToInference} = \frac{T_{\text{load}}^{(\mathrm{ns})}}{T_{\text{eval}}^{(\mathrm{ns})}}.
\end{equation}

\subsection{Memory Usage per Token}
\begin{equation}
\text{MemPerTokenMB} = \frac{\bar{M}}{N_{\text{eval}}}.
\end{equation}

\subsection{Energy per Token}
\begin{equation}
\text{EnergyPerToken} = \frac{E_{\text{total}}}{N_{\text{eval}}}
= \frac{\bar{P} \times T_{\text{local}}}{N_{\text{eval}}}.
\end{equation}

\subsection{Power Spike}
\begin{equation}
\text{PowerSpike} = P_{\max} - P_{\min}.
\end{equation}

\subsection{Prompt Evaluation Ratio (Fraction of Total Time)}
\begin{equation}
\text{PromptEvalRatio} = 
\frac{T_{\text{prompt}}^{(\mathrm{ns})}}{T_{\text{total}}^{(\mathrm{ns})}}.
\end{equation}

\subsection{Prompt-to-Generation Overhead Ratio}
\begin{equation}
\text{PromptToGenerationOverhead} 
= 
\frac{T_{\text{prompt}}^{(\mathrm{ns})}}{T_{\text{eval}}^{(\mathrm{ns})}}.
\end{equation}

\subsection{Power Efficiency Index (TPS per Watt)}
\begin{equation}
\text{PowerEfficiencyIndex} 
= 
\frac{\text{TPS}}{\bar{P}}
= 
\frac{N_{\text{eval}} / (T_{\text{eval}}^{(\mathrm{ns})}/10^9)}{\bar{P}}.
\end{equation}

\subsection{CPU Stability Index}
Define $\sigma_C$ as the standard deviation of CPU usage samples and 
\[
\denom_{\text{CPU}} = \max(100, \bar{C}),
\]
then
\begin{equation}
\text{CPUStabilityIndex} 
= 
1 - \frac{\sigma_C}{\denom_{\text{CPU}}}.
\end{equation}
Values $< 0$ are clamped to 0.

\subsection{Model Efficiency Index}
\begin{equation}
\text{ModelEfficiencyIndex} = \frac{\text{TPS}}{M_{\max}}.
\end{equation}
That is, tokens per second divided by peak memory usage (MB).

\subsection{Peak CPU to Average Ratio}
\begin{equation}
\text{PeakCPUtoAvgRatio} = \frac{C_{\max}}{\bar{C}}.
\end{equation}

\subsection{Memory Variation Index}
\begin{equation}
\text{MemVariationIndex} = \frac{\sigma_M}{\bar{M}}.
\end{equation}

\subsection{Peak Power to Average Power Ratio}
\begin{equation}
\text{PeakPowerToAvgPowerRatio} 
= 
\frac{P_{\max}}{\bar{P}}.
\end{equation}

\subsection{Prompt Evaluation Tokens per Second}
\begin{equation}
\text{PromptEvalTPS} 
= 
\frac{N_{\text{prompt}}}{T_{\text{prompt}}^{(\mathrm{ns})}/10^9}.
\end{equation}

\subsection{Evaluation Latency per Token}
\begin{equation}
\text{EvalLatencyPerToken} 
= 
\frac{T_{\text{eval}}^{(\mathrm{ns})}}{N_{\text{eval}}}.
\end{equation}

\subsection{Evaluation Memory Efficiency}
\begin{equation}
\text{EvalMemoryEfficiency} 
= 
\frac{\text{TPS}}{\bar{M}}.
\end{equation}

\subsection{Token Production Energy Efficiency}
\begin{equation}
\text{TokenProductionEnergyEff} 
= 
\frac{N_{\text{eval}}}{\bar{P} \times T_{\text{local}}}.
\end{equation}
The inverse of \texttt{EnergyPerToken}.

\subsection{Average CPU to Power Ratio}
\begin{equation}
\text{AvgCPUtoPowerRatio} 
= 
\frac{\bar{C}}{\bar{P}}.
\end{equation}

\subsection{Peak RAM to Peak CPU Ratio}
\begin{equation}
\text{PeakRAMtoPeakCPU} 
= 
\frac{M_{\max}}{C_{\max}}.
\end{equation}

\subsection{Time-Weighted Power Factor}
\begin{equation}
\text{TimeWeightedPowerFactor} 
= 
\frac{\bar{P}}{T_{\text{local}}}.
\end{equation}

\subsection{Load to Prompt Ratio}
\begin{equation}
\text{LoadToPromptRatio} 
= 
\frac{T_{\text{load}}^{(\mathrm{ns})}}{T_{\text{prompt}}^{(\mathrm{ns})}}.
\end{equation}

\subsection{Prompt to Total Token Ratio}
\begin{equation}
\text{PromptToTotalTokenRatio} 
= 
\frac{N_{\text{prompt}}}{N_{\text{eval}}}.
\end{equation}

\subsection{Memory to CPU Ratio (Peak Values)}
\begin{equation}
\text{MemoryToCPUratio} 
= 
\frac{M_{\max}}{C_{\max}}.
\end{equation}

\subsection{Memory to Power Ratio}
\begin{equation}
\text{MemoryToPowerRatio} 
= 
\frac{\bar{M}}{\bar{P}}.
\end{equation}

\subsection{RAM Usage Variation Index}
\begin{equation}
\text{RAMUsageVariationIndex} 
= 
\frac{\sigma_M}{\bar{M}}.
\end{equation}
(Synonym of Memory Variation Index in some contexts.)

\subsection{Power Usage Variation Index}
\begin{equation}
\text{PowerUsageVariationIndex} 
= 
\frac{\sigma_P}{\bar{P}}.
\end{equation}
Where $\sigma_P$ is the std.\ dev.\ of power measurements.

\subsection{Sustained Inference Factor}
\begin{align}
\text{SustainedInferenceFactor} 
&= 
\left(\frac{N_{\text{eval}}}{N_{\text{prompt}} + N_{\text{eval}}}\right)
\times
\left(\frac{\text{TPS}}{\bar{P}}\right).
\end{align}
It measures the fraction of newly generated tokens multiplied by tokens/Watt.

\subsection{Thermal Load Factor}
\begin{equation}
\text{ThermalLoadFactor} 
= 
\frac{\frac{\bar{C} + C_{\max}}{2}}{\bar{P}}.
\end{equation}

