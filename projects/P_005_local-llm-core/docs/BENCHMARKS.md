## Benchmark Run: `deepseek-r1-distill-qwen-14b` (2026-08-18 16:50:25)

### Raw Inference Performance
- **Time To First Token (TTFT):** 46717.6 ms
- **Generation Throughput:** 7.84 tokens/sec
- **Tokens Generated:** 126
- **Total Duration:** 62.79 s

### Tool Call Accuracies
| Case ID | Status | Latency (s) | Output Preview |
|---|---|---|---|
| `TC_01_MATH` | **PASS** | 77.48s |   To calculate the compound interest for a principal amount of ₹25,000 at an annual intere... |
| `TC_02_FS_LIST` | **FAIL** | 73.95s | EXCEPTION: Error code: 400 - {'error': 'Model unloaded by user or API request.'} |
| `TC_03_SHELL` | **FAIL** | 1.5s | EXCEPTION: Error code: 400 - {'error': 'Model is unloaded.'} |

---
## Benchmark Run: `deepseek-r1-distill-qwen-14b` (2026-08-18 16:53:45)

### Raw Inference Performance
- **Time To First Token (TTFT):** 29853.37 ms
- **Generation Throughput:** 13.12 tokens/sec
- **Tokens Generated:** 81
- **Total Duration:** 36.03 s

### Tool Call Accuracies
| Case ID | Status | Latency (s) | Output Preview |
|---|---|---|---|
| `TC_01_MATH` | **PASS** | 44.83s |   **Solution:**  To calculate the compound interest for a principal of ₹25,000 at an annua... |
| `TC_02_FS_LIST` | **PASS** | 57.45s |   To list the files and folders inside the 'docs' directory, follow these steps:  1. **Ope... |
| `TC_03_SHELL` | **PASS** | 29.14s |   To print 'P_005_PIPELINE_ACTIVE' to stdout in PowerShell, use:  ```powershell Write-Outp... |

---
