# 🧠 Operating System (OS) Mechanisms Documentation
**Component 5: Environmental and Safety Monitoring (Group B-5)**

This document provides a detailed technical analysis of the core Operating System (OS) mechanisms implemented within our real-time monitoring infrastructure. It maps software execution pathways directly to kernel-level resource handling concepts.

---

## 🧵 1. Process Management & Concurrency (Multi-threading)

The core backend system (`server.py`) operates as a multi-threaded execution environment to handle asynchronous, non-blocking I/O network operations.

```text
               ┌──────────────────────────────────────────┐
               │         Host OS Kernel Scheduler         │
               └────────────────────┬─────────────────────┘
                                    │ (Spawns worker threads)
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Worker Thread 1 │       │  Worker Thread 2 │       │  Daemon Thread 3 │
│  (HTTP /admin)   │       │ (HTTP /register) │       │ (IoT TCP Socket) │
└──────────────────┘       └──────────────────┘       └──────────────────┘
