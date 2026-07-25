---
title: "Building a Decentralized RAG with Blockchain Verification & Source Code"
source: "https://aiengineeringinsider.substack.com/p/building-a-decentralized-rag-with"
author:
  - "[[AI Engineering Insider]]"
date: "2026-07-20"
published: 2026-07-17
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
sector:
origin:
---
A production-grade Retrieval-Augmented Generation (RAG) platform with document integrity secured by an Ethereum smart contract registry and local IPFS storage.

## Why Do We Need Blockchain in RAG?

In standard Retrieval-Augmented Generation (RAG) applications, documents are parsed, chunked, embedded, and stored in a vector database. When a user asks a question, the system retrieves semantically relevant chunks and feeds them to the LLM to generate an answer.

This architecture has a critical vulnerability: **Vector Database Poisoning & Tampering**.

![](https://substackcdn.com/image/fetch/$s_!s14T!,w_1456,c_limit,f_webp,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F77cdabff-3e7e-4562-9993-5d8d73aa6f3a_3447x2045.png)

System Architecture

### The Vulnerability

If an attacker gains write access to the vector database or document storage (such as a local file folder, S3 bucket, or SQL database), they can alter document contents, inject false data, or modify system instructions. When the RAG engine queries the database, it retrieves this compromised text and sends it to the LLM. The LLM, unaware of the tampering, will answer the user’s question with false information, citing the compromised document as a source.

### The Solution: Blockchain Verification

A blockchain provides a **tamper-proof, decentralized, and immutable ledger**. In our RAG system, we use the blockchain as a cryptographically secure root of trust:

1. **Immutable Registration**: When a document is uploaded, we compute its unique SHA256 checksum and record it on the Ethereum blockchain via a smart contract (`DocumentRegistry.sol`), bound to the document’s IPFS Content Identifier (CID). Once written, this transaction is permanent and cannot be modified or forged.
2. **On-Retrieval Audits (Zero-Trust)**: When a chunk is retrieved for a query, the backend fetches the original document bytes from storage and computes the SHA256 hash. It calls the blockchain registry to check:
	- Does this document’s CID exist on-chain?
		- Does the computed SHA256 match the recorded hash on the blockchain?
3. **Refusal to Answer**: If the hashes do not match (meaning the document has been tampered with or poisoned), the verifier immediately flags it. The system discards the chunk, and if no verified context remains, the LLM refuses to answer, protecting the user from database poisoning.

## Why IPFS + Blockchain?

Storing large documents (such as PDFs or text files) directly on the blockchain is extremely inefficient and cost-prohibitive due to the high gas costs of on-chain storage.

Instead, we use a hybrid model:

- **Off-Chain Storage (IPFS)**: IPFS (InterPlanetary File System) uses **Content Addressing**. A file is identified by its Content Identifier (CID), a cryptographic hash of its contents. If a single character changes, the CID changes.
- **On-Chain Indexing (Ethereum)**: The blockchain contract stores only the small metadata records (IPFS CID, SHA256 hash, owner address, block timestamp, version).

This design provides decentralized, secure storage with lightweight, inexpensive blockchain validation.

## Core Libraries & Technologies Used

We utilize a modern stack of libraries to build this robust environment:

### Web3 & Smart Contracts

- **Solidity (v0.8.24)**: The contract programming language used to write `DocumentRegistry.sol`. It defines the mapping schema and handles access controls (checking that only the owner can delete or update a registered document).
- **Hardhat**: A Node.js development environment for Ethereum. We use it to:
	- Compile smart contracts to generate the ABI.
		- Spin up a local EVM network (npx hardhat node) running on port `8545` to test transactions without paying real gas.
		- Automate contract deployments using script runners.
- **Web3.py (v7.16)**: The Python adapter library. Our FastAPI backend uses it to connect to the Hardhat JSON-RPC node over HTTP. Web3.py handles transaction building, account credential signing, gas limit estimations, transaction receipt waiting, and contract view calls.

### Artificial Intelligence & Database

- **Ollama**: A lightweight local LLM execution engine. We use it to:
	- Run the nomic-embed-text:latest model to generate 768-dimensional vector embeddings of text chunks.
		- Run the `llama3.2:1b` model to execute local reasoning and stream responses.
- **ChromaDB**: An AI native vector database. It stores semantic chunks alongside metadata indexes and provides fast cosine-similarity lookups (<2s latency) without requiring external cloud databases.

### Backend, Frontend, and Testing

- **FastAPI**: The high-performance Python web framework used to expose API routes (/upload, /query, /documents, /verify/{cid}, /document). It manages CORS, multi-part form file uploads, JWT token issuance, and JSON/text response streaming.
- **Streamlit**: A Python framework for building interactive user interfaces. It runs on port 8501, managing user login states, system connection indicators, file uploads, chat queries, and displays detailed log outputs.
- **PyPDF2**: Extracts raw text from binary PDF layouts.
- **Playwright**: A cross-browser testing library. It automates Chrome in headless or headful mode to run end-to-end tests, filling forms, uploading files, and making assertions to automatically verify the app’s health.

Github link: [https://github.com/lamhotsiagian/llm-blockchain](https://github.com/lamhotsiagian/llm-blockchain)

---

## Folder Structure

```markup
llm-blockchain/
├── README.md                  # Detailed startup and run commands
├── requirements.txt           # Python application dependencies
├── .env                       # Environment configurations
├── config.yaml                # RAG parameter setup
├── blockchain/                # Smart Contract & Hardhat project
│   ├── contracts/
│   │   └── DocumentRegistry.sol
│   ├── scripts/
│   │   └── deploy.js
│   ├── hardhat.config.js
│   └── package.json
├── src/                       # Source codebase
│   ├── api/
│   │   └── main.py            # FastAPI endpoints
│   ├── auth/
│   │   └── jwt.py             # JWT token helpers
│   ├── blockchain/
│   │   └── client.py          # Web3.py wrapper client
│   ├── chunking/
│   │   └── chunker.py         # Sliding window text chunking
│   ├── config/
│   │   └── config.py          # Config registry loader
│   ├── ingestion/
│   │   └── extractor.py       # PDF/TXT parser
│   ├── ipfs/
│   │   └── client.py          # IPFS connection & mock storage
│   ├── llm/
│   │   └── client.py          # Ollama LLM client
│   ├── vectordb/
│   │   └── client.py          # ChromaDB persistent client
│   ├── verifier/
│   │   └── verifier.py        # Hash verification logic
│   └── app.py                 # Streamlit client portal
└── tests/                     # Integration tests
    ├── generate_seed_data.py  # programmatically generate seed docs
    ├── seed.py                # Upload seed data via API
    └── test_e2e.py            # Playwright E2E browser test
```

## Prerequisites

1. **Python**: **python3** (v3.10+)
2. **Node.js & npm**: For a local Hardhat Ethereum node network.
3. **Ollama**: Download and run Ollama, then fetch models:
```markup
ollama pull llama3.2:1b
ollama pull nomic-embed-text:latest
```

---

## Installation

1. Install Python dependencies:
```markup
pip install -r requirements.txt
```
1. Install Node.js dependencies for Hardhat:
```markup
cd blockchain
npm install
cd ..
```

---

## Running the Application

Follow these steps sequentially to run the full decentralized RAG ecosystem locally:

### Step 1: Start the Local Ethereum Blockchain

In your terminal, navigate to the **blockchain** folder and launch the Hardhat development node:

```markup
cd blockchain
npx hardhat node
```

This runs a local EVM-compatible blockchain node on

http://127.0.0.1:8545

and outputs default developer accounts. Keep this process running.

### Step 2: Deploy the Document Registry Smart Contract

Compile and deploy the Solidity registry contract:

```markup
cd blockchain
npx hardhat run scripts/deploy.js --network localhost
```

This compiles the contract and writes the deployed address to the configuration directory (**src/config/deployed\_contract.json**).

### Step 3: Run the FastAPI Backend Server

In a new terminal window, start the FastAPI server:

```markup
python3 -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

### Step 4: Run the Streamlit Frontend App

In a new terminal window, launch the interactive UI portal:

```markup
python3 -m streamlit run src/app.py --server.port 8501
```

Navigate your browser to

http://localhost:8501

to use the portal. Log in using:

- **Username**: **admin**
- **Password**: **adminpassword123**

---

## Seeding Sample Data

To populate the database with sample policies and service agreements:

1. Generate the seed files:
```markup
python3 tests/generate_seed_data.py
```
1. Upload the seed data to the active backend:
```markup
python3 tests/seed.py
```

---

## Automated End-to-End Testing

We use **Playwright** to execute E2E browser tests.

### Run Tests

```markup
pytest -v tests/test_e2e.py
```

> \[!IMPORTANT\]  
> The E2E test suite automatically wipes/cleans existing ChromaDB indices and IPFS mock files before running to guarantee a fresh, isolated state.