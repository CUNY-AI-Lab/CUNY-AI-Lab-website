# Model Registry Field Guide (for humanities & social science users)

This guide explains the **metadata fields** used in a model registry (like the JSON you’re building) in plain language.  
It’s meant to help you read a model listing and understand what the specs *actually mean* for everyday research and teaching.

---

## Basic identity fields

### `key`
A short, stable identifier used by software (URLs, filtering, config).  
Think of it like a database ID: it shouldn’t change even if the display name does.

### `display_name`
The human-readable model name shown in the UI.

### `vendor`
Who produced or maintains the model (e.g., Meta, Google, OpenAI, DeepSeek).

### `family` / `variant`
- **Family**: the broader model line (e.g., “Llama 3.1”).
- **Variant**: the specific version or tuning (e.g., “70B Instruct”, “Thinking”).

“Instruct” usually means the model is tuned to follow instructions and chat politely, rather than only predicting text.

---

## Modality: what kinds of inputs the model can handle

### `modality`
Typical values:
- `["text"]`: text in → text out
- `["text","image"]`: image + text in → text out (vision-enabled)

If a model is text-only, it can’t “see” screenshots, charts, photos, scans, etc.

---

## Size and architecture: what the model *is*, internally

### `parameters.total_b` (total parameters)
**Parameters** are the model’s internal “learned settings.”  
`total_b` expresses the *size* of the model in **billions** of parameters.

Bigger models often (not always) do better at:
- complex reasoning
- following nuanced instructions
- multilingual work
- writing in a consistent voice

But bigger models can also be:
- slower
- more expensive to run
- sometimes more verbose or overconfident if not guided

### `parameters.active_b` (active parameters)
Used mostly for **MoE** (see below).  
Some models are built so that *only part* of the model “turns on” for each token.  
That “active” subset is the compute cost you pay per request.

If `active_b` is much smaller than `total_b`, the model can behave like a very large model while running closer to a mid-sized compute footprint.

### `parameters.architecture`
Common values:
- **dense**: all parameters participate each time  
  - predictable compute cost
  - simpler to host/run
- **MoE (Mixture of Experts)**: the model contains many “expert” sub-models; only a few are activated per token  
  - can be very capable at lower per-request compute than the total size suggests  
  - serving stacks and providers may differ more in performance/behavior

### Why this matters in practice
- If you want **fast, steady performance**, dense models are often simpler.
- If you want **very strong capability**, many of today’s biggest models are MoE.

---

## Context window: how much the model can “keep in mind”

### `context_window_tokens`
The maximum number of **tokens** the model can consider at once (prompt + conversation history + system instructions + retrieved docs, etc.).

### What is a “token”?
A token is a chunk of text (often ~3–4 characters of English on average, but it varies by language and content).  
Rough rule-of-thumb:
- **1,000 tokens ≈ 750 words** (very approximate)

### Why context matters
A larger context window helps when you:
- paste long readings
- compare multiple documents
- work with long conversations (e.g., course assistants across weeks)
- include lots of citations/quotes/notes in one prompt

### Extended / max context (`context_window_tokens_extended`, `context_window_tokens_max`)
Sometimes a model has:
- a **native** context window (what it’s designed for), and
- an **extended** context using techniques like RoPE scaling / YaRN

Extended context can work well, but quality may degrade (more “drift,” more missed details).  
Providers may also cap context for cost/performance reasons.

---

## Capabilities: what the model can do (or can be configured to do)

### `capabilities.vision`
- `true`: can take images as input (usually image + prompt)
- `false`: text only

### `capabilities.tool_calling`
Tool calling means the model can produce structured instructions for external actions, such as:
- searching a library catalog or database
- fetching citations
- calling a transcription service
- running a calculation
- triggering a workflow step

Important: tool calling is partly a **model skill** and partly **system plumbing**.  
Even if a model *can* tool-call, your platform has to implement the tools.

### `capabilities.structured_output`
This describes whether the model can reliably produce structured formats:
- JSON
- CSV-like records
- schema-shaped outputs (fields with labels)

Many models can *attempt* JSON if you ask—but strict correctness varies.  
If you see values like:
- `true`: model/provider advertises it explicitly
- `"prompted"`: achievable via prompting, but not guaranteed without enforcement
- `"unknown"`: not confirmed

### `capabilities.reasoning_mode`
Some models support an explicit “thinking” mode or switch that changes behavior:
- more deliberate
- better at multi-step problems
- sometimes slower / more tokens consumed

---

## Openness and licensing: what you’re allowed to do with the model

### `open_weights`
- `true`: the model weights are available for download and self-hosting
- this does **not** necessarily mean:
  - training data is open
  - training code is open
  - the license is fully permissive

### `license` vs `license_id`
- `license`: a human-readable label (e.g., “Apache-2.0”, “Gemma Terms of Use”)
- `license_id`: a consistent machine-readable identifier used for filtering

### `license_family`
A coarse category that helps non-lawyers quickly understand restrictions:
- `permissive`: standard open-source-style license (e.g., Apache-2.0, MIT)
- `permissive_modified`: mostly permissive but with extra clauses (branding/trademark notice, etc.)
- `community`: “open weights” with additional use restrictions (often including acceptable-use policies and/or commercial thresholds)
- `restricted_terms`: gated and governed by terms-of-use licenses with additional constraints

### `requires_clickthrough` / `gated_weights_download`
These reflect whether you typically must:
- accept special terms in a web UI, and/or
- request access to download weights (common for “community” or “restricted terms” models)

### Why this matters in practice
- For **reproducible research** and long-term institutional sustainability, licenses and gating matter as much as model quality.
- “Open weights” models can still have meaningful restrictions.

(Always consult your institution’s counsel or policy guidance for licensing decisions.)

---

## “Soft” metadata fields: how humans choose models

### `best_for`
Short task-oriented descriptions: what this model tends to do well.

### `strengths` / `limitations`
Fast, practical notes on what users should expect.

### `tags` / `ui_badges`
- `tags`: used for filtering/search in a UI
- `ui_badges`: quick visual hints (“Long context”, “Vision”, “Tool use”)

---

## How to pick a model (quick heuristics)

### If you’re doing long reading or comparing sources
Prefer:
- large `context_window_tokens`
- strong summarization/synthesis notes
- models known for “long-context coherence”

### If you need help with code, data wrangling, or structured outputs
Prefer:
- `tool_calling: true`
- `structured_output: true` or `"prompted"`
- strengths mentioning “structured outputs” or “coding”

### If you’re working from images (charts, manuscripts, screenshots)
You need:
- `vision: true`

### If you need strict reproducibility / long-term stability
Prefer:
- permissive `license_family`
- `open_weights: true`
- not gated (or at least clearly documented gating)

---

## A note on “accuracy”
A bigger model or a “reasoning” model is not automatically more accurate.  
For scholarly work, best practice is:
- ask for citations / quotations
- verify against sources
- treat the model as a drafting and exploration tool, not an authority

---

## Glossary (very short)

- **Token**: chunk of text used by LLMs; not the same as a word.
- **Context window**: how much text the model can consider at once.
- **Dense**: all parameters active for each token.
- **MoE**: mixture-of-experts; only some parameters used per token.
- **Tool calling**: structured requests to external tools/APIs.
- **Structured output**: consistent JSON/fields output.
- **Open weights**: weights downloadable; not necessarily open data/code.
