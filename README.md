---
title: SovereignCore Autonomous Personal AI
emoji: 🛡️
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.38.0
app_file: app.py
pinned: false
license: apache-2.0
---

# SovereignCore: Autonomous Sovereign Personal AI Platform
### Built for the Nebius × NVIDIA Global AI Hackathon (Personal AI Track & Best Use of Tavily Prize)

[![NVIDIA Nemotron](https://img.shields.io/badge/Model-NVIDIA%20Nemotron-76B900.svg)](https://developer.nvidia.com)
[![Nebius Token Factory](https://img.shields.io/badge/Cloud-Nebius%20Serverless-0070F3.svg)](https://nebius.com)
[![Tavily Search](https://img.shields.io/badge/Tool-Tavily%20MCP-orange.svg)](https://tavily.com)
[![Protocol Stack](https://img.shields.io/badge/Protocols-MCP%20%7C%20A2A%20%7C%20AG--UI-blueviolet.svg)](#tri-protocol-architecture)

---

## 💡 Executive Summary
**SovereignCore** is an on-device and private-cloud personal AI assistant governed by **NVIDIA NeMo Guardrails**, isolated inside **NVIDIA OpenShell** sandboxes, and powered by **NVIDIA Nemotron** models running on **Nebius Serverless** infrastructure. It is the first personal assistant to unify all three modern agent protocols (**MCP + A2A + AG-UI**) into a sovereign commercial product.

---

## 🏛️ Tri-Protocol Architecture

1. **MCP (Model Context Protocol):**
   - **Local Encrypted Vault:** AES-GCM (256-bit) authenticated encryption for private memories at rest.
   - **Zero-Cloud Vector RAG:** Private on-device cosine semantic retrieval.
   - **Context-Aware Tavily Engine:** Real-time web intelligence with intent-based domain routing (Technical, News, Finance, Academic) and Zero-Hallucination Grounding verification.

2. **A2A (Agent-to-Agent Protocol):**
   - **Signed Agent Cards:** Cryptographically signed tokens (HMAC-SHA256) with granular database scopes (`vault:read:schedule`, `tavily:search:academic`, etc.).
   - **Specialized Sub-Agents:** Dedicated sub-agents for Study Coaching, Financial Advisory, and Competitive Intelligence.

3. **AG-UI (Agent-User Interaction Protocol):**
   - **Dynamic Approval Interceptors:** Halts high-risk write operations, issuing cryptographic nonces requiring user confirmation before committing.
   - **Streaming Token Chunk Parser:** Streams internal chain-of-thought tokens directly into the live thought feed without latency.
