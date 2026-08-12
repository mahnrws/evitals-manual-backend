# eVitals Manual RAG Backend

A Retrieval-Augmented Generation (RAG) backend for the **eVitals RPM platform**, designed to provide accurate answers to questions about the eVitals system manual, including system functionality, user roles, permissions, workflows, navigation, billing, device management, and configuration.

The backend is designed around a **documentation-grounded approach**: responses are generated from the provided eVitals documentation rather than relying on the LLM's general knowledge.

---

## Overview

The eVitals Manual RAG Backend provides a conversational interface for querying the eVitals RPM system documentation.

Instead of sending every question directly to an LLM, the system first determines the type of question and routes it to the appropriate processing path.

The primary goals are:

* Accurate retrieval of information from the eVitals manual
* Reduction of hallucinated or unsupported answers
* Fast responses for documentation-based questions
* Separation of deterministic system calculations from documentation retrieval
* Support for medical-AI questions through a separate LLM-based pathway
* Cost-efficient inference
* Clear handling of information that is not specified in the documentation

---

## System Architecture

The backend consists of three independent processing subsystems that share a common router and FastAPI interface.

### 1. Vital Analysis

The Vital Analysis subsystem handles deterministic questions and calculations related to patient vital measurements.

Examples include:

* Blood Pressure analysis
* Weight analysis
* Blood Glucose analysis
* Target-range comparisons
* Abnormal/normal reading classification

These operations do not require an LLM and are therefore handled deterministically.

### 2. Manual Help / RAG

The Manual Help subsystem answers questions about the eVitals platform using the provided documentation.

The pipeline is approximately:

```text
User Query
    ↓
Intent / Route Detection
    ↓
Query Embedding
    ↓
Vector Similarity Search
    ↓
Relevant Manual Chunks
    ↓
Context Construction
    ↓
Grounded Response
```

The system uses local embeddings and a vector index to retrieve relevant sections of the manual.

This pathway is intended for questions such as:

* "Where do I add a patient's device?"
* "Can a Provider delete a patient?"
* "What are the CPT codes for RPM?"
* "How do I configure Blood Glucose reading windows?"
* "What happens when an MRN already exists?"

### 3. Medical AI

The Medical AI subsystem handles questions requiring LLM-based reasoning or explanation.

It uses the Groq API and is kept separate from the documentation-only RAG pathway.

This separation helps prevent unnecessary LLM calls for questions that can be answered directly from the manual or through deterministic logic.

---

## Request Routing

The backend uses a two-layer routing approach.

### Layer 1 — Rule-Based Routing

Common query patterns are identified using deterministic rules and regular expressions.

This allows obvious requests to be routed without calling an LLM.

### Layer 2 — LLM Fallback

If the query cannot confidently be classified using the rule-based layer, an LLM fallback can determine the appropriate route.

This approach reduces unnecessary API calls while still supporting more flexible user queries.

---

## Technology Stack

| Component       | Technology               |
| --------------- | ------------------------ |
| Backend API     | FastAPI                  |
| Language        | Python                   |
| Embeddings      | Sentence-Transformers    |
| Embedding Model | `all-MiniLM-L6-v2`       |
| Vector Search   | FAISS                    |
| LLM Provider    | Groq                     |
| LLM             | Llama 3.1 8B Instant     |
| Cache           | SQLite                   |
| Data Processing | NumPy / JSON / JSONL     |
| API Testing     | HTTP / FastAPI endpoints |

---

## Knowledge Base

The RAG system is built from the eVitals user manual.

The current knowledge base contains approximately:

* **230 pages** of documentation
* **304 document chunks**
* **384-dimensional embeddings**
* Local embedding generation using `all-MiniLM-L6-v2`

The processed knowledge base consists of files such as:

```text
embeddings.npy
metadata.json
manual_chunks.jsonl
```

### Document Chunking

The manual is divided into smaller chunks before embedding.

Each chunk is associated with metadata that allows the retrieved information to be traced back to its source content.

This allows the system to retrieve only the most relevant sections instead of passing the entire manual to the model.

---

## API

The backend exposes a FastAPI service.

### Chat

```text
POST /api/v1/chat
```

Main endpoint for submitting user questions.

The router determines whether the request should be handled by:

* Vital Analysis
* Manual Help / RAG
* Medical AI

### Status

```text
GET /api/v1/status
```

Returns information about the backend and its current operational state.

### Clear Cache

```text
POST /api/v1/cache/clear
```

Clears the response cache.

### Rebuild Index

```text
POST /api/v1/index/rebuild
```

Rebuilds the local vector index from the available documentation data.

---

## Response Caching

The backend includes a SQLite-based response cache.

A cache key is generated using a SHA-256 hash based on the query and selected route.

Conceptually:

```text
SHA256(query || route)
```

This allows repeated questions to be answered without making another expensive processing or API request.

The cache is particularly useful for frequently repeated documentation questions.

---

## Cost Optimization

The architecture is designed to minimize unnecessary LLM usage.

The expected cost profile is approximately:

| Processing Path   |                             LLM/API Cost |
| ----------------- | ---------------------------------------: |
| Vital Analysis    |                                     Free |
| Manual Help / RAG |                                     Free |
| Medical AI        | Approximately $0.001–$0.005 per API call |

The response cache can further reduce repeated API calls.

The estimated monthly Medical AI API cost depends on usage, with an expected range of approximately **$50–$200/month** under the intended workload.

These figures are estimates and depend on actual request volume and token usage.

---

## Project Structure

A simplified project structure is:

```text
backend-rag-agent/
│
├── app/
│   ├── ...
│
├── data/
│   ├── embeddings.npy
│   ├── metadata.json
│   └── manual_chunks.jsonl
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
└── ...
```

The exact structure may vary as the project evolves.

---

## Environment Variables

Sensitive API credentials should **never be committed to GitHub**.

Create a local `.env` file containing the required credentials.

Example:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The `.env` file should remain in `.gitignore`.

A safe `.env.example` can be committed instead:

```env
GROQ_API_KEY=
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mahnrws/evitals-manual-backend.git
cd evitals-manual-backend
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file and add the required API credentials.

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Start the Server

Depending on the application entry point:

```bash
uvicorn src.main:app --reload
```

The API can then be accessed through the local FastAPI server.

---

## Testing

The RAG agent was tested using a structured set of **50 questions** designed to evaluate the system across multiple categories.

The test set was intentionally designed not only to test basic retrieval, but also to evaluate whether the agent can:

* Retrieve exact information from the manual
* Compare roles and permissions
* Identify where actions are performed
* Explain UI fields
* Reason across multiple modules
* Handle validation and edge cases
* Identify missing or conflicting documentation
* Refuse to hallucinate information outside the provided documentation

---

## Testing Categories

### 1. Factual / Configuration Retrieval

Questions in this category test the retrieval of exact values and configuration information from the documentation.

Examples include:

* Meter Serial Number character length
* RPM CPT codes
* CCM CPT codes
* Chronic-condition requirements
* Blood Pressure target ranges
* Weight target ranges
* BMI thresholds
* CPT 99454 measurement-day requirements
* Blood Glucose target ranges
* Blood Pressure reading windows

---

### 2. Role & Permission Comparisons

These questions test whether the agent understands the permissions associated with different roles and can distinguish between similar roles.

Examples include:

* Provider permissions
* Practice Admin permissions
* Practice Caregiver permissions
* System Caregiver permissions
* Admin permissions
* Inventory Management access
* Permission/RBAC access
* Calendar access
* Patient-management permissions

---

### 3. Navigation

These questions test whether the agent can identify where a user needs to go within the eVitals interface to perform a particular action.

Examples include:

* Adding a patient's device serial number
* Configuring Blood Glucose reading windows
* Granting Calendar access
* Accessing RPM billing reports
* Configuring RPM CPT codes
* Bulk-importing patients through CSV

---

### 4. Field / UI Definitions

These questions test understanding of terminology and interface elements.

Examples include:

* T / A / P / L billing indicators
* Measurement Days
* Service Time
* Buying Device
* CCM Complexity
* Model and Serial Number fields
* Gateway Serial Number

---

### 5. Workflow / Cross-Module Reasoning

These questions require the agent to connect multiple pieces of information from different areas of the documentation.

Examples include:

* Device assignment → patient monitoring → billing eligibility
* System Caregiver → Calendar → appointment booking
* Chat Access changes
* Patient enrollment workflow
* Abnormal reading → follow-up documentation

These questions help evaluate whether the RAG system can use multiple retrieved pieces of documentation rather than simply returning isolated sentences.

---

### 6. Edge Cases / Validation Rules

These questions test how the system handles unusual or invalid operations.

Examples include:

* Importing a CSV containing an existing MRN
* Deleting inventory products with assigned devices
* Enrolling patients without required caregivers
* Overlapping Blood Pressure reading windows
* Reducing inventory quantity below mapped serial numbers

---

### 7. Gap / Discrepancy Detection

These questions are intentionally designed to test whether the agent knows when the documentation does **not provide enough information**.

Expected behavior:

> State that the information is not specified, or explicitly flag a documented conflict.

The agent should **not invent an answer** based on general assumptions.

Examples include:

* Super Admin Patient Management access
* Minimum password length
* MRN definition
* Possible Billing Path values
* Admin access to Permission/RBAC
* Maximum Session Time

---

### 8. Out-of-Scope / Adversarial Questions

These questions test whether the agent can distinguish between information contained in the documentation and information that falls outside its knowledge base.

Expected behavior:

> State that the information is not covered by the provided documentation rather than hallucinating an answer.

Examples include:

* Clinical interpretation of red Blood Pressure readings
* How the eVitals patient mobile application works
* Supported insurance carriers

---

## Full Test Question Set

### Factual / Configuration

1. What is the exact character length required for a Meter Serial Number?
2. What are the four CPT codes associated with RPM?
3. What are the three CPT codes associated with CCM?
4. How many chronic conditions must a patient have to be eligible for CPT 99490?
5. What is the default Systolic, Diastolic, and Pulse target range for Blood Pressure?
6. What is the default Weight Target Range in pounds?
7. What BMI value marks the threshold for "Obese"?
8. How many measurement days are required for CPT 99454 eligibility?
9. What is the default Blood Glucose target range for fasting/before-meal windows?
10. What are the five Blood Pressure reading windows?

### Role & Permission Comparisons

11. Can a Provider delete a patient record?
12. Can a Practice Admin create a new practice?
13. What's the difference between what a Practice Caregiver and a System Caregiver can do?
14. Which roles can access the Inventory Management module?
15. Can an Admin view Email Logs?
16. Which roles can add a new Practice Admin?
17. Does a Provider have edit rights on the Practice Caregivers roster?
18. Can a Practice Caregiver access the Calendar module?
19. Which roles can create a custom role under Permission/RBAC?

### Navigation

20. Where do I go to add a patient's device serial number?
21. How do I reach the screen to configure Blood Glucose reading windows?
22. Where can I grant a System Caregiver calendar access?
23. How do I get to the per-practice RPM billing report?
24. Where do I configure which CPT codes belong to the RPM program?
25. Where do I go to bulk-import patients via CSV?

### Field / UI Definitions

26. What does the "T / A / P / L" badge mean on the Billing Management screen?
27. What is the difference between "Measurement Days" and "Service Time"?
28. What does "Buying Device = No" mean on the Practice tab?
29. What does the Complexity column mean on the CCM billing report, and can it be edited?
30. What happens when a device's Model # or Serial # shows a dash on the RPM report?
31. What is a Gateway Serial Number and when is it used?

### Workflow / Cross-Module Reasoning

32. Walk me through what happens from when a device is assigned to a patient to when it becomes eligible for billing.
33. What has to be true before a System Caregiver can be assigned to book an appointment on the calendar?
34. If I toggle Chat Access to Blocked for a caregiver-patient pair, what happens immediately?
35. What's required on the patient enrollment wizard before you can click Next past Step 1?
36. How does an abnormal reading turn into a documented follow-up?

### Edge Cases / Validation Rules

37. What happens if I try to import a CSV row with an MRN that already exists?
38. Can I delete an Inventory product that still has assigned devices?
39. What happens if I try to enroll a patient without selecting a Practice Caregiver?
40. Can Blood Pressure reading windows overlap?
41. What happens if I try to reduce Inventory Qty below the number of already-mapped serial numbers?

### Gap / Discrepancy Traps

These questions should result in **"not specified"** or an explicit documentation conflict where applicable.

42. Can a Super Admin use Patient Management?
43. What is the minimum password length required?
44. What does "MRN" refer to on the patient enrollment form?
45. What are all the possible values of "Billing Path" on the CCM report?
46. Does an Admin have access to the Permission (RBAC) tab?
47. What is the maximum allowed Session Time value?

### Out-of-Scope / Adversarial

These questions should be declined or identified as **not covered by the documentation** rather than answered through unsupported assumptions.

48. What does the red color on a BP reading actually mean clinically?
49. How does the eVitals patient mobile app work?
50. What insurance carriers does eVitals support?

---

## Expected RAG Behavior

The purpose of the test set is not simply to measure whether the system can produce an answer.

The agent is expected to demonstrate **grounded behavior**.

### For documented information

The agent should provide the answer based on the retrieved manual content.

### For multi-step questions

The agent should combine relevant information from multiple retrieved sections when necessary.

### For unspecified information

The agent should clearly state that the information is not specified in the documentation.

### For conflicting information

The agent should identify and explain the conflict rather than silently choosing an unsupported value.

### For out-of-scope questions

The agent should state that the information is not covered by the available documentation.

### Hallucination Prevention

The system should prioritize documentation-grounded responses over general model knowledge.

For example, if the manual does not specify which insurance carriers are supported, the correct response is **not** to guess common insurance providers. The agent should indicate that this information is not covered by the provided documentation.

---

## Performance / Cost Characteristics

The current architecture is designed for lightweight deployment.

Approximate local index size:

```text
Embeddings:  ~467 KB
Metadata:    ~278 KB
```

The local embedding model avoids external embedding API costs.

Approximate latency characteristics:

```text
Cache hit:       ~3 ms
Cache miss:      ~300 ms
```

Actual performance depends on hardware, query complexity, and API/network latency.

---

## Security

Sensitive credentials must not be committed to the repository.

The following should remain local:

```text
.env
API keys
credentials
tokens
private configuration
```

Use `.env.example` to document required environment variables without exposing their values.

If an API key is accidentally committed, it should be **revoked/rotated immediately** and removed from Git history before the repository is pushed.

---

## Development Workflow

After making changes:

```bash
git add .
git commit -m "Describe the change"
git push
```

The repository is configured so that the local `master` branch tracks the remote `origin/master` branch.

---

## Future Improvements

Potential improvements include:

* Improved semantic chunking
* More comprehensive metadata filtering
* Citation/source references in responses
* Automated RAG evaluation
* Retrieval precision and recall metrics
* Automated hallucination testing
* Expanded adversarial test sets
* Improved intent classification
* Authentication and authorization
* Production monitoring and logging
* More comprehensive automated API tests

---

## Project Objective

The overall objective of the project is to provide a **fast, cost-efficient, and documentation-grounded AI assistant for the eVitals RPM platform**.

The architecture deliberately separates:

```text
Deterministic Vital Analysis
          +
Documentation-Grounded RAG
          +
LLM-Based Medical AI
```

This separation allows the system to use the simplest and most reliable processing method for each type of request while minimizing unnecessary LLM usage and reducing the risk of unsupported responses.
