---
title: "Basic Concepts"
headingId: "basic-concepts"
---

Use this page when a term appears in a walkthrough. You do not need to learn every configuration option before starting a chat.

## Models

A base model generates responses from the instructions and content it receives. A custom model combines a base model with instructions and, when needed, knowledge collections, tools, or skills. Creating a custom model changes its configuration rather than training a new base model. Check the Sandbox selector for available models and test them on your task.

## System Prompts

A system prompt describes the model's role, expected actions, and boundaries. For example, an instructor can ask it to question an interpretation before offering feedback. These instructions guide responses; testing is still needed to see whether the model follows them. See [System Prompts](system-prompts.md).

## Knowledge Bases

A knowledge base is a collection of uploaded documents that a configured model can search. Retrieval-augmented generation, or RAG, supplies relevant passages as context for a response. It does not guarantee that the right passage will be found or accurately represented. See [Knowledge Collections](knowledge-bases.md).

## Tools and Skills

Tools perform actions beyond generating text, such as web search or code execution, when the platform, model, and your permissions support them. Skills supply reusable procedural instructions. Attaching a skill does not give the model a tool's capabilities or grant additional access. See [Tools & Skills](tools-skills.md).

## Roles and Workspace

The account roles are **Admin**, **User**, and **Pending**. Administrators manage the platform; a Pending account awaits activation. Faculty, staff, and student access depends on assigned permissions and groups.

**Workspace** is the area for creating models, knowledge collections, prompt templates, tools, and skills, subject to those permissions. Individual Lab access does not automatically include it. Request configuration access from [ailab@gc.cuny.edu](mailto:ailab@gc.cuny.edu).

## Resource Access

A **Private** resource is available to you and any users or groups you add through **Add Access**. **Public** makes it available to all signed-in Sandbox users, where permitted. Administrators may also access resources for platform management. Use [Roles & Permissions](roles-permissions.md) before sharing course materials.

## Chats<span id="conversations-chats" aria-hidden="true"></span>

A chat contains your messages and the model's responses. Regular chats save automatically; temporary chats are excluded from history. The sidebar menu lets you rename, archive, delete, or share a chat. Archiving removes it from the active list; deletion is permanent.

Chats are not shared with classmates by default. A share link or course-channel post changes the audience, and administrators can access stored chats. Review [Privacy and Chat History](getting-started.md#privacy-and-chat-history) before adding sensitive material.

## Providers

A provider hosts models. Administrators configure the Sandbox's model connections, including the CAIL Model API. Its [Model Registry](https://ailab.gc.cuny.edu/models/) describes API offerings, which may differ from the Sandbox selector.

[← Return to Getting Started](getting-started.md) | [Continue to Quick Tour →](quick-tour.md)
