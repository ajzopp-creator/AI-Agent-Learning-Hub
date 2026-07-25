# Break and Retest Trading Strategy: Python Architecture & Implementation Specification

Based on the core price action principles from [The Break and Retest: The Only Pattern You Actually Need](http://www.youtube.com/watch?v=7yjz0xucODA), this document outlines the algorithmic state machine and Python logic required to automate the strategy.

---

## 1. System Architecture & State Machine

To translate price action into quantitative code, the strategy operates as a deterministic **Finite State Machine (FSM)** with four distinct operational states: