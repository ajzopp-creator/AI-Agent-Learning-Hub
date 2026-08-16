# P_000_Model_Hardware_Spec

**Last verified:** August 15, 2026
**Regenerate with:** `Trader-CLI` PowerShell one-liner at the bottom of this doc — note which machine it was run on when updating.

---

## Machines

| Machine | Role | Local LLM tier | Notes |
|---|---|---|---|
| AJZ-TRADING-LAP (ASUS TUF F16) | Primary | Full — see below | RTX 5070 8GB VRAM, 96GB RAM |
| AJZSTRATEGIESLG (LG Gram 17Z990-R) | Secondary | None — cloud only | No usable GPU offload path; Cowork also unavailable (Windows 11 Home, no Hyper-V) |

---

## Machine: AJZ-TRADING-LAP (ASUS TUF Gaming F16 FX608LP)

| Component | Spec |
|---|---|
| Manufacturer / Model | ASUSTeK ASUS TUF Gaming F16 FX608LP |
| BIOS | AMI FX608LP.313 (2025-11-17) |
| OS | Windows 11 Pro, build 26200, installed 2025-12-04 |
| CPU | Intel Core Ultra 9 275HX (Arrow Lake-HX) |
| Cores / Threads | 24 / 24 (8 P-cores + 16 E-cores, no HT on this generation) |
| Base clock | 2.7 GHz (boost 5.4 GHz) |
| RAM | 96 GB total — 2 × 48 GB Micron DDR5-5600 SODIMM |
| Discrete GPU | NVIDIA GeForce RTX 5070 Laptop (Blackwell, compute cap 12.0) |
| VRAM | 8 GB GDDR7 (8151 MiB reported by nvidia-smi) |
| NVIDIA driver | 591.44 |
| Integrated GPU | Intel Arc Graphics (iGPU) |
| Storage C: | 1 TB NVMe SSD (Samsung MZVL21T0HDLU) — OS |
| Storage D: | 1 TB NVMe SSD (Micron MTFDKBA1T0QGN) — OneDrive root, backups |
| Storage F: | 4 TB USB HDD (Seagate Expansion) — static OneDrive snapshot, do not rely on for live work |
| Other display adapters | DisplayLink USB (dock) |

### Local LLM capacity (LM Studio + llama.cpp)

VRAM is the binding constraint for fully-on-GPU inference. With 8 GB usable VRAM and 96 GB system RAM, partial offload covers everything up to dense 70B at Q4.

#### Sizing rules of thumb

| Quant | Size formula | Example: 7B | 14B | 32B | 70B |
|---|---|---|---|---|---|
| Q4_K_M | ~0.55 × N GB | 4.4 GB | 8.5 GB | 19 GB | 42 GB |
| Q5_K_M | ~0.65 × N GB | 5.2 GB | 10 GB | 22 GB | 50 GB |
| Q8_0   | ~1.05 × N GB | 8.4 GB | 16 GB | 35 GB | 75 GB |

Add ~1 GB for KV cache at 8K context, ~2 GB at 32K. Reserve ~500 MB VRAM for the desktop.

#### What runs well on this machine

| Tier | Recommended model | Quant | Where it lives | Tokens/sec (typical) |
|---|---|---|---|---|
| **Fast** — fully on GPU | Qwen2.5-7B-Instruct | Q4_K_M | All in VRAM, 8K ctx | 50–80 |
| **Fast+** — tight on GPU | Qwen2.5-14B-Instruct | Q4_K_M | Mostly VRAM, 4K ctx | 25–40 |
| **Smart** — split | Qwen2.5-32B-Instruct or QwQ-32B | Q4_K_M | ~12 layers GPU, rest RAM | 8–15 |
| **Heavy** — mostly RAM | Llama-3.3-70B-Instruct | Q4_K_M | Few layers GPU | 2–4 |
| **Coder** — split | Qwen2.5-Coder-32B | Q4_K_M | Same as Smart tier | 8–15 |

For trading-specific reasoning (chart pattern logic, scenario analysis), QwQ-32B in the Smart tier is the strongest single choice — purpose-built for chain-of-thought work, runs at the same memory cost as Qwen2.5-32B.

#### LM Studio per-model settings

| Model size | n_gpu_layers | Context | Notes |
|---|---|---|---|
| 7B Q4    | -1 (all)   | 8192–32768 | Easy; cap context only if you need >50 tok/s |
| 14B Q4   | -1 (all)   | 4096–8192  | Watch VRAM usage in Task Manager; drop to 28 if OOM |
| 32B Q4   | 12–18      | 4096       | Tune up until VRAM is ~7.5 GB, no higher |
| 70B Q4   | 4–8        | 4096       | Slow but workable for offline analysis only |

LM Studio's "GPU Offload" slider equates to n_gpu_layers. Start conservative, watch nvidia-smi, push up until you see VRAM hit ~7.5 GB.

### Tooling decisions tied to this hardware

- **Local runtime:** LM Studio (GUI) is the chosen stack. Reasons: native Blackwell/CUDA 12.6 support, OpenAI-compatible server on `localhost:1234` already wired into hub_lib, per-layer GPU offload control, model browser. Anaconda AI Navigator was evaluated and rejected — smaller library, less control, no Blackwell tuning.
- **Headless alternative:** Ollama (`localhost:11434`) is a viable swap if you ever want LM Studio off the desktop. hub_lib's `call_lmstudio()` works against either by changing `base_url`.
- **Maximum-throughput alternative:** llama.cpp directly. ~15% faster than LM Studio on the same GGUF, no GUI. Only worth the tradeoff for batch jobs.

---

## Machine: AJZSTRATEGIESLG (LG Gram 17Z990-R)

**Role:** Secondary, cloud-inference-only.

| Component | Spec |
|---|---|
| CPU | Intel Core i7-8565U — 4 cores |
| GPU | Intel UHD 620 (integrated, no CUDA path) |
| RAM | 15.8 GB |
| Disk | 237 GB NVMe (single) |
| OS | Windows 11 Home — no Hyper-V, Cowork unavailable |

No usable GPU offload path on this hardware. DeepSeek R1 14B would run CPU-only at roughly 1–2 tok/s; Qwen 32B and Llama 4 Scout aren't runnable at all. A single 8B model as an offline fallback is technically possible post-rebuild (~150 GB free) at maybe 3–5 tok/s — Tony's call, not a recommendation; slow enough that the Claude API wins whenever a network is available.

This machine has no LM Studio tier. All `local_*` tasks route to their `cloud_*` equivalent here instead — see MODEL_MAP routing below.

---

## hub_lib MODEL_MAP — current routing

Defined in `C:\Users\Trader\AI-Agent-Learning-Hub\hub_lib\model_manager.py`.

| Task name | Provider (ASUS) | Provider (LG) | Model |
|---|---|---|---|
| `local_fast`    | lmstudio  | anthropic → routed to `cloud_fast` | qwen2.5-7b-instruct / claude-haiku-4-5-20251001 |
| `local_smart`   | lmstudio  | anthropic → routed to `cloud_smart` | qwen2.5-32b-instruct / claude-opus-4-7 |
| `cloud_fast`    | anthropic | anthropic | claude-haiku-4-5-20251001 |
| `cloud_smart`   | anthropic | anthropic | claude-opus-4-7 |
| `vp_pattern`    | google    | google    | gemini-2.5-flash |
| `vp_reasoning`  | google    | google    | gemini-2.5-pro |

**Open risk (resolved pending verification):** hostname-aware routing (WO-P000-E10.004) landed in code 2026-08-15 — `machine_capability.py` (new) plus a `model_manager.py` edit auto-route `local_*` to `cloud_*` on any machine without a local LLM tier. WO status stays PENDING until the two checks in its Verification Plan run: confirm the LG silently substitutes cloud with an INFO-level log, and confirm the ASUS still hits `localhost:1234` unchanged.

To swap a local task to a different model on the ASUS, either edit the row in MODEL_MAP or set an override in `.env`:

```
HUBLIB_TASK_LOCAL_SMART=lmstudio:qwq-32b
```

---

## Regenerate this spec

Open Anaconda Prompt or any PowerShell, paste:

```powershell
$cs   = Get-CimInstance Win32_ComputerSystem
$cpu  = Get-CimInstance Win32_Processor
$os   = Get-CimInstance Win32_OperatingSystem
$bios = Get-CimInstance Win32_BIOS
$ram  = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
"$($cs.Manufacturer) $($cs.Model)"
"BIOS: $($bios.SMBIOSBIOSVersion) ($($bios.ReleaseDate))"
"OS:   $($os.Caption) build $($os.BuildNumber)"
"CPU:  $($cpu.Name) — $($cpu.NumberOfCores)C/$($cpu.NumberOfLogicalProcessors)T"
"RAM:  {0:N1} GB" -f $ram
nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv
Get-PhysicalDisk | Format-Table FriendlyName, MediaType, BusType, @{N='GB';E={[math]::Round($_.Size/1GB,0)}}
```

Update the relevant machine's table above when any line changes (new GPU driver, RAM upgrade, BIOS update, OS build).

---

## Change log

- **2026-08-15** — Restructured to per-machine format (WO-P000-E10.002). Added AJZSTRATEGIESLG (LG Gram) as secondary, cloud-inference-only machine. No changes to ASUS spec content. Flagged MODEL_MAP as still hardcoded pending WO-P000-E10.004.
- **2026-05-02** — Initial spec captured. Machine confirmed as ASUS TUF F16 FX608LP, Core Ultra 9 275HX, RTX 5070 Laptop 8 GB, 96 GB DDR5-5600. hub_lib v0.1 MODEL_MAP recorded.
