# PAVAN SIDDAPURAM

Anantapur, India — siddapurampavan9381@gmail.com — +91 9381276155 — LinkedIn — GitHub

## Professional Summary

Systems-oriented Software Engineer building performance-critical web platforms and reliability-aware AI systems. Experienced in GPU-accelerated computation, async architectures, WebAssembly pipelines, and evaluation-driven LLM integrations across production environments.

## Experience

### Software Engineer I — Fracktal Works Pvt. Ltd. (Aug 2025 – Present)

- Led architecture and implementation of a browser-based 3D CAD platform (React 18, TypeScript, Three.js, React Three Fiber), reducing traditional fixture workflows from hours of manual CAD to minutes of guided in-browser generation.
- Engineered GPU-accelerated geometry pipelines using custom GLSL shaders and WebAssembly (Manifold 3D, MeshOptimizer), achieving 10x performance gains over CPU-based approaches; implemented tiled heightmap persistence for large models.
- Designed multi-backend CSG boolean engine with BVH acceleration and automatic fallback to WASM-based kernels; built 3-stage mesh decimation pipeline reducing 2M-triangle meshes to 50K while preserving boundary topology.
- Offloaded compute-intensive tasks (CSG, decimation, mesh repair) to Web Workers with zero-copy ArrayBuffer transfers, maintaining 60fps UI responsiveness; packaged CAD engine as framework-agnostic monorepo module.

### Full Stack Web Developer — Manipal Academy of Higher Education (Apr 2024 – Jul 2025)

- Built and deployed production applications using React and Django REST Framework with authentication, structured validation, and CI-driven release workflows.

### Data Analyst Intern — MITRAz Skills (Oct 2023 – Mar 2024)

- Built business dashboards and automated data preprocessing pipelines using Python and SQL to streamline recurring reporting cycles.

## Projects

### OpenClaw – Local-First Multi-Agent Harness (Rust), 2026

- Built a local-first agent harness in Rust orchestrating specialized agent personas over a private, on-device context store, with deterministic routing and no cloud dependency for end-to-end execution.

### CheckoutMind – Dual-Agent Payment Recovery Platform, 2026

- Built a dual-agent recovery system on AWS Bedrock (Claude) coordinating a consumer-intelligence agent and a merchant-recovery agent over a shared order-context store, with offer-aware retry logic and a circuit-breaker fallback.

### HonestRAG – Deterministic Retrieval-First LLM System, 2026

- Designed retrieval-first RAG architecture prioritizing explicit refusal over generative confidence, built on ChromaDB vector indexing and locally hosted LLM inference.
- Implemented cosine-similarity threshold gating prior to generation to decouple retrieval quality from model output; validated against curated in-/out-of-domain golden test cases to reduce high-confidence hallucination.

### RepriceAI – AI-Assisted Dynamic Pricing Platform, 2025

- Designed LLM-assisted pricing engine with explainability layer (FastAPI, React) deployed on Google Cloud Run; selected Top 10 out of 300+ submissions in Google Cloud Build & Blog Marathon.

## Technical Skills

- **Languages:** TypeScript, Python, JavaScript (ES6+), Go, Rust
- **Frontend:** React 18, Next.js, Three.js, React Three Fiber, Zustand, React Query, Tailwind CSS
- **Backend:** FastAPI, Django, Fastify, Express, Redis, BullMQ
- **Systems & Performance:** WebAssembly, Web Workers, BVH, CSG, Mesh Decimation, GPU Compute, Zero-Copy Transfers
- **AI & Agents:** Multi-Agent Orchestration, Retrieval-Augmented Generation (RAG), Vector Search (ChromaDB), LLM Tool Calling, AWS Bedrock
- **Databases:** PostgreSQL, MySQL, MongoDB
- **Cloud & DevOps:** Docker, GitHub Actions, AWS (EC2, S3, RDS), Google Cloud Run

## Education

- **M.S. Applied Mathematics (Online)** — Lovely Professional University, Aug 2025 – Feb 2026 (discontinued)
- **B.Sc. Mathematics, Physics and Computer Science** — Sri Krishnadevaraya University, 2020 – Aug 2023

## Certifications

- Building with the Claude API – Anthropic, 2026
- Introduction to Model Context Protocol – Anthropic, 2026
- Startup School, Founder Curriculum – Y Combinator, 2026
