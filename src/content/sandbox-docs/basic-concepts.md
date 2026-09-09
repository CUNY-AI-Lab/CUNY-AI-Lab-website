---
title: "Basic Concepts"
headingId: "basic-concepts"
---

Use these definitions when building custom configurations or navigating the Sandbox.

---

## Models

A **model** generates the responses you receive when you enter prompts in the Sandbox.

The Sandbox connects to multiple models. Some are better at reasoning, some at writing, some at multilingual tasks. You can switch between them mid-chat or create custom configurations that combine a base model with your own instructions.

A **base model** generates responses from the instructions and content in a chat. When creating a custom model, choose which base model it will use.

**Custom model.** A configuration you build. It includes a base model, system prompt (instructions on how to behave), knowledge bases (documents to reference), and tools (capabilities like web search).

---

## System Prompts

A **system prompt** is the set of instructions you give a model about how to behave.

Example
> You help students analyze data. When a student shares a dataset or research question, guide them through: (1) identifying variables and measurement scales, (2) choosing appropriate visualizations, (3) selecting statistical tests, and (4) interpreting results. Ask questions that help them understand *why* a method fits their data. Do not generate full analysis reports. Point to their course materials when relevant concepts appear.

System prompts define tone, boundaries, and role. You write them when creating a custom model.

---

## Knowledge Bases

A **knowledge base** is a collection of documents the model can search before responding.

After uploading files (PDFs, Markdown, plain text) to a knowledge collection, custom models can retrieve relevant passages from those documents in response to situated tasks or course-specific questions.

This process, **retrieval-augmented generation (RAG)**, gives the model passages from your materials to use when generating a response.

---

## Tools

**Tools** extend what a model can do beyond generating text.

Examples
- **Web Search.** Model searches the internet for current information
- **Code Interpreter.** Model runs Python code and returns results
- **arXiv Search.** Model queries academic papers

You can enable tools for a single chat or make them available whenever you use a custom model.

---

## Skills

**Skills** are reusable Markdown instructions you can attach to models.

Skills can hold detailed procedures, such as a feedback protocol, that you attach to a model without including them in its general system prompt.

Example skills
- Quantitative Methods (statistical analysis)
- Academic Writing (citation practices, genre conventions)
- Research Ethics (IRB compliance)

Attach a skill to a custom model to make those instructions available when it responds to the tasks you specify.

---

## Roles & Permissions

**Roles** are Admin, User, or Pending. Administrators manage the platform. Faculty, staff, and student access depends on the permissions and groups assigned to their accounts.

**Permissions** control who can see and use your custom models and knowledge bases
- **Private.** You and any users or groups you add through **Add Access**
- **Public.** All signed-in Sandbox users, where public sharing is permitted

---

## Workspace

Individual access lets you use resources shared by the CUNY AI Lab, but does not automatically include **Workspace**. Email the [CUNY AI Lab team](mailto:ailab@gc.cuny.edu) to request Workspace access for creating configurations in these sections.
- Go to **Workspace > Models** to create custom models
- Go to **Workspace > Knowledge** to create knowledge bases
- Go to **Workspace > Prompts** to save and share reusable prompt templates
- Go to **Workspace > Tools** to browse available tools (if you have access)
- Go to **Workspace > Skills** to create and share reusable instructions

---

## Chats<span id="conversations-chats" aria-hidden="true"></span>

A **chat** contains your messages and the model’s responses. Regular chats are saved automatically; temporary chats are excluded from history. You can
- Rename them (use the three-dot menu beside the chat in the sidebar)
- Archive them (remove from active list)
- Delete them (permanent)
- Share them (send a link to someone else)

Chats are private by default. Sharing requires generating a share link.

---

## Provider

In Open WebUI, a **provider** is a service that hosts models.

The Sandbox uses one connection, the CAIL Model API, which serves the models listed in the [Model Registry](https://ailab.gc.cuny.edu/models/). Administrators configure that connection in the settings for the Sandbox.

---

## Next Steps

Now that you know the basic concepts, you can
- Take the [Quick Tour](quick-tour.md) to see where these concepts live in the interface
- Jump into [Getting Started](getting-started.md) to log in and start your first chat
- Or skip ahead to [Design & Test](index.md) if you're ready to start building

---

## Learn More

The CAIL Sandbox is hosted and maintained by the [CUNY AI Lab](https://ailab.gc.cuny.edu) at the Graduate Center. For workshops, office hours, and additional resources, visit the [AI Lab website](https://ailab.gc.cuny.edu).

---

[← Return to Getting Started](getting-started.md) | [Continue to Quick Tour →](quick-tour.md)
