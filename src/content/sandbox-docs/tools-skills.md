---
title: "Extending Models with Tools & Skills"
headingId: "extending-models-with-tools--skills"
---

Out of the box, a model can only generate text. Tools change that: enable a tool and the model can search the web, run code, query a database, or look up papers on arXiv during a conversation. Skills work differently. Where tools connect to external services, skills provide specialized knowledge domains the model draws on without you modifying the system prompt. Think of tools as hands and skills as expertise.

---

## Tools

### Types of Tools

- **Native features**: Built into Open WebUI and ready to use. Web Search, Image Generation, URL Fetch, and Memory require no setup.
- **Workspace tools**: Python scripts registered in the platform. These run on the server when the model calls them.
- **MCP (Model Context Protocol)**: Anthropic's open standard for connecting AI models to external data sources and services. MCP servers expose structured capabilities that models discover and invoke automatically.
- **OpenAPI servers**: Any web service with an OpenAPI specification can be connected as a tool provider.

### Enabling Tools Per-Chat

1. Open a conversation
2. Click the **➕** icon next to the input box
3. Browse or search available tools
4. Toggle on the tools you want for this session
   - Tools enabled this way apply only to the current conversation

### Enabling Tools Per-Model

1. Go to **Workspace > Models**
2. Edit the model you want to configure
3. Scroll to the **Tools** section
4. Check the tools you want always available with this model
5. Click **Save**
   - Every conversation with this model will now have access to these tools

### Community Tool Library

Open WebUI maintains a community library of pre-built tools. Some relevant to academic work:

- **arXiv Search** — query academic papers directly from chat. No API key required.
- **Perplexica Search** — web search with inline citations.
- **Pexels Media Search** — find stock photos and videos for presentations.
- **YouTube Search & Embed** — locate and embed instructional videos.

> **Tip:** Browse the community library before building your own tool. Someone may have already solved your problem.

### Function Calling

Some models support native function calling (indicated by a **TOOLS** tag in Ollama). These models determine when to call a tool, what arguments to pass, and how to incorporate results without extra prompt engineering. If your model supports function calling, tool use becomes more reliable and natural.

---

## Skills

Skills are specialized knowledge domains you bind to models. Unlike system prompts (which define general behavior), skills provide on-demand access to detailed procedural instructions for specific topics.

### Binding Skills

1. Go to **Workspace > Models**
2. Edit the model
3. Scroll to the **Skills** section
4. Select the skills you want to bind
5. Click **Save**

When a user's question falls within a skill's domain, the model loads the relevant instructions automatically. You do not need to anticipate every possible question in your system prompt.

### Example Skills for CUNY

- **Quantitative Methods**: statistical analysis, research design, SPSS and R guidance
- **Academic Writing**: scholarly conventions, citation practices, genre awareness
- **Research Ethics**: IRB compliance, data privacy, informed consent protocols
- **Digital Humanities**: text analysis, corpus methods, visualization techniques

---

## Advanced Settings

<details>
<summary>View details</summary>

### Building Custom Tools

If the community library does not have what you need, administrators can write custom tools. Each tool requires a name, description, and Python function body. The function runs on the server when the model invokes it.

Go to **Workspace > Tools > + New Tool** to get started. Consult with the AI Lab team if you are unsure about security implications.

### Tool Security

Tools are Python scripts that execute on the server. A poorly written or malicious tool can access system resources, exfiltrate data, or disrupt service. Only install tools from trusted sources. The AI Lab maintains an approved tool list. Contact the team before adding community tools to the instance.

</details>

---

## Callout

<div class="callout">
  <strong>Security reminder:</strong> Review any community tool's code before installing it. Tools run with server-level access. If you are not comfortable evaluating Python code, ask the AI Lab team to review it for you.
</div>

---

## Additional Resources

- [Open WebUI Tools Documentation](https://docs.openwebui.com) — official reference for tool development and configuration
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io) — Anthropic's specification for connecting AI models to external data
- [Open WebUI Community Tools](https://openwebui.com/tools) — browse and download pre-built tools

---

[← Return to Knowledge Bases](knowledge-bases.md) | [Continue to Roles & Permissions →](roles-permissions.md)
