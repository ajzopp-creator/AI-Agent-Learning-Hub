# P_005 Local LLM Core — System Architecture Master

## 1. System Overview
P_005_local-llm-core provides an interface and runtime for local LLMs under LM Studio.

## 2. Layered Architecture Standard
- config.py: Constants and system limits
- schemas.py: Pydantic schemas
- domain/: Pure logic, ToolRegistry, TypeAdapter validation
- infrastructure/: LM Studio client, PowerShell runner, BOM-safe I/O
- application/: Multi-turn tool orchestration & benchmark logging
- tests/: Permanent regression test suite

## 3. Hardware Profile & Offload
- CPU: Intel Core Ultra 9 275HX
- GPU: RTX 5070 (8GB VRAM)
- RAM: 96GB DDR5
- Granite 4.1 8B: 100% VRAM offload (~58 tok/s)
- DeepSeek-R1 14B: Hybrid offload (~13 tok/s)
