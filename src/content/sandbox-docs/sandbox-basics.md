# Sandbox Basics

Core terminology, interface layout, and navigation.

---

## Key Concepts

**Base model:** The underlying AI (e.g., DeepSeek V3.2, Kimi K2.5). You pick one when creating a custom model.

**Custom model:** A configuration you build: base model + system prompt + knowledge bases + tools.

**System prompt:** Instructions that define how a model behaves: its role, tone, boundaries, and response style.

**Knowledge base:** A collection of uploaded documents (PDFs, Markdown, plain text) the model searches before responding. This is called RAG (Retrieval-Augmented Generation): responses grounded in your materials instead of general training data.

**Tools:** Capabilities beyond text generation: Web Search, Code Interpreter, arXiv Search. Enable per-chat or per-model.

**Skills:** Specialized knowledge domains (e.g., Quantitative Methods, Research Ethics) you bind to models for procedural expertise.

**Roles:**
- **Administrators** — full platform access, configure providers, install tools
- **Faculty/Staff** — create and share models, knowledge bases, manage groups
- **Students** — use shared resources, create private configurations

**Visibility levels:** Private (only you), Limited (specific users/groups), Public (all Sandbox users).

---

## Interface Layout

Three areas on screen:

1. **Sidebar (left)** — conversation history, Workspace access, settings
2. **Chat area (center)** — conversation thread and input box
3. **Top bar** — model selector, profile, settings

---

## Sidebar

- **Chats** — conversation history. Click to reopen. Hover for rename/archive/delete.
- **Workspace** — Models, Knowledge, Tools (requires Workspace access)
- **Settings** — preferences, defaults, profile

---

## Chat Controls

- **Model selector** (top of chat) — click to switch models mid-conversation
- **➕** (input box) — add tools to the current chat
- **📎** (input box) — attach files (images, PDFs, documents)
- **Message actions** (three dots on any message) — edit, copy, delete, regenerate

---

## Workspace

Where you build custom configurations (requires Workspace access):

- **Workspace > Models** — create, edit, share custom AI models
- **Workspace > Knowledge** — upload documents, build knowledge bases
- **Workspace > Prompts** — save and share reusable system prompts
- **Workspace > Tools** — browse and manage available tools
- **Workspace > Skills** — add specialized knowledge domains to models

---

## Next Steps

- [Getting Started](getting-started.md) — log in and have your first conversation
- [Custom Models](models.md) — build your first custom configuration

---

[← Return to Getting Started](getting-started.md) | [Continue to Custom Models →](models.md)
