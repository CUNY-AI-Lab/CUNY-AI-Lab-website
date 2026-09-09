# Basic Concepts

Before you build custom configurations, it helps to understand a few core concepts. This page covers the terminology and structure of the Sandbox.

---

## Models

A **model** is the AI you talk to. It generates responses to your prompts.

The Sandbox connects to multiple models. Some are better at reasoning, some at writing, some at multilingual tasks. You can switch between them mid-conversation or create custom configurations that combine a base model with your own instructions.

**Base model:** The underlying AI (e.g., DeepSeek V3.2, Kimi K2.5). You pick one when creating a custom model.

**Custom model:** A configuration you build. It includes a base model, system prompt (instructions on how to behave), knowledge bases (documents to reference), and tools (capabilities like web search).

---

## System Prompts

A **system prompt** is the set of instructions you give a model about how to behave.

Example:
> You help students analyze data. When a student shares a dataset or research question, guide them through: (1) identifying variables and measurement scales, (2) choosing appropriate visualizations, (3) selecting statistical tests, and (4) interpreting results. Ask questions that help them understand *why* a method fits their data. Do not generate full analysis reports. Point to their course materials when relevant concepts appear.

System prompts define tone, boundaries, and role. You write them when creating a custom model.

---

## Knowledge Bases

A **knowledge base** is a collection of documents the model can search before responding.

You upload files (PDFs, Markdown, plain text). When a user asks a question, the model retrieves relevant passages from your documents and uses them to answer.

This is called **RAG** (Retrieval-Augmented Generation). It grounds responses in your materials instead of the model's general training data.

---

## Tools

**Tools** extend what a model can do beyond generating text.

Examples:
- **Web Search:** Model searches the internet for current information
- **Code Interpreter:** Model runs Python code and returns results
- **arXiv Search:** Model queries academic papers

You enable tools per-chat (just for one conversation) or per-model (always available with that custom model).

---

## Skills

**Skills** are specialized knowledge domains you can attach to models.

Where system prompts define general behavior and knowledge bases provide specific documents, skills offer procedural expertise. Think of them as reference manuals the model can consult.

Example skills:
- Quantitative Methods (statistical analysis)
- Academic Writing (citation practices, genre conventions)
- Research Ethics (IRB compliance)

You bind skills to models when you want them to have access to detailed domain knowledge without writing it all into the system prompt.

---

## Roles & Permissions

**Roles** determine what you can do in the Sandbox:
- **Administrators:** Full access (configure instance, install tools)
- **Faculty/Staff:** Create and share models, knowledge bases, tools
- **Students:** Use shared resources, create private configurations

**Permissions** control who can see and use your custom models and knowledge bases:
- **Private:** Only you
- **Limited:** Specific users or groups (e.g., your course section)
- **Public:** Everyone on the Sandbox

---

## Workspace

The **Workspace** is where you build:
- Go to **Workspace > Models** to create custom models
- Go to **Workspace > Knowledge** to create knowledge bases
- Go to **Workspace > Prompts** to save and share reusable system prompts
- Go to **Workspace > Tools** to browse available tools (if you have access)
- Go to **Workspace > Skills** to add specialized knowledge domains

You'll spend most of your building time in the Workspace.

---

## Conversations (Chats)

Each conversation you have with a model is called a **chat**. Chats are saved automatically. You can:
- Rename them (click the title in the sidebar)
- Archive them (remove from active list)
- Delete them (permanent)
- Share them (send a link to someone else)

Chats are private by default. Sharing requires generating a share link.

---

## Provider

A **provider** is the service that hosts the base models.

The Sandbox connects to multiple providers to offer a range of models. You don't need to worry about providers unless you're an administrator configuring instance-wide settings.

---

## Next Steps

Now that you know the basic concepts, you can:
- Take the [Quick Tour](quick-tour.md) to see where these concepts live in the interface
- Jump into [Getting Started](getting-started.md) to log in and have your first conversation
- Or skip ahead to [Design & Test](index.md) if you're ready to start building

---

## Learn More

The CUNY CAIL Sandbox is hosted and maintained by the [CUNY AI Lab](https://ailab.gc.cuny.edu) at the Graduate Center. For workshops, office hours, and additional resources, visit the [AI Lab website](https://ailab.gc.cuny.edu).

---

[← Return to Getting Started](getting-started.md) | [Continue to Quick Tour →](quick-tour.md)
