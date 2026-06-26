# 🧠 Operating System (OS) Mechanisms Documentation
**Component 5: Environmental and Safety Monitoring (Group B-5)**

This document provides a detailed technical analysis of the core Operating System (OS) mechanisms implemented within our real-time monitoring infrastructure. It maps software execution pathways directly to kernel-level resource handling concepts.

---

1. Process Management & Concurrency (Multi-threading)

The core backend system (`server.py`) operates as a multi-threaded execution environment to handle asynchronous, non-blocking I/O network operations.

```text
               ┌──────────────────────────────────────────┐
               │         Host OS Kernel Scheduler                 │
               └────────────────────┬─────────────────────┘
                                        │ (Spawns worker threads)
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Worker Thread 1    │       │  Worker Thread 2    │       │  Daemon Thread 3     │
│  (HTTP /admin)      │       │ (HTTP /register)    │       │ (IoT TCP Socket)     │
└──────────────────┘       └──────────────────┘       └──────────────────┘
2. Synchronization, Mutual Exclusion, and the Critical Section

To manage shared memory spaces among multiple concurrent execution threads without data degradation, the system addresses the classic **Critical Section Problem**.

```text
                        Incoming Concurrent Threads
                       (IoT Nodes / Web Portal Users)
                                     │
                                     ▼
                      ┌─────────────────────────────┐
                      │    Request Mutual Lock           │
                      │     (data_lock.acquire)          │
                      └──────────────┬──────────────┘
                                       │
                        [Is Lock Free? (Mutex)]
                         /                 \
                   YES  /                   \  NO
                       ▼                     ▼
        ┌─────────────────────────────┐    ┌─────────────────────────────┐
        │   ENTER CRITICAL SECTION         │    │     THREAD BLOCKED / WAIT        │
        │  (Write to REGISTERED_           │    │  (Suspended by OS Kernel)        │
        │   RUNNERS & LIVE_LOGS)           │    └──────────────▲──────────────┘
        └──────────────┬──────────────┘                     │
                       │                                         │ Moves to
                       ▼                                         │ Ready State
        ┌─────────────────────────────┐                     │ when free
        │    RELEASE MUTEX LOCK            │──────────────────┘
        │     (data_lock.release)          │
        └─────────────────────────────┘
3. Inter-Process Communication (IPC): The Producer-Consumer Model

Communication between our decentralized edge layer and the visualization interface is modeled directly after the OS Bounded-Buffer Pattern.

┌─────────────────────────┐                   ┌─────────────────────────┐
│        PRODUCERS            │                   │        CONSUMER              │
│                             │                   │                              │
│ 1. ESP32 Node Payload       ├──────┐   ┌─────►│  Admin Dashboard View       │
│ 2. Web Portal SOS Click     │       │   │       │  (SSE Stream Interface)     │
└─────────────────────────┘      ▼   │       └─────────────────────────┘
                               ┌─────┴───┴─────┐
                               │ SHARED BUFFER    │
                               │                  │
                               │ ThreadSafe-      │
                               │Queue Interface   │
                               └───────────────┘

4. Asynchronous I/O & Software Interrupt Handling

The architecture treats critical safety anomalies (such as a runner triggering an alert state) similarly to how an OS kernel responds to a hardware trap or software exception.

[Normal State] ──► Background Logging Thread Processing (Low CPU Usage Loop)
                                   │
                                   ▼ (Runner hits Emergency SOS button)
            ┌────────────────────────────────────────┐
            │   TRAP / SOFTWARE INTERRUPT GENERATED         │
            └───────────────────┬────────────────────┘
                                    │
                                    ▼ (Preempts Standard Queue Layout)
            ┌────────────────────────────────────────┐
            │    HQ OVERLAY INTERRUPT ROUTINE               │
            │  (Instantly flashes red alarm window)         │
            └────────────────────────────────────────┘
