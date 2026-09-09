---
title: "Extending Models with Tools & Skills"
headingId: "extending-models-with-tools--skills"
---

Tools let a model search the web, run code, query a database, or look up papers on arXiv during a conversation. Skills give it access to specialized procedural instructions without requiring you to put those instructions in the system prompt.

---

## Tools

### Types of Tools

- **Built-in capabilities**. Web Search, Image Generation, URL fetching, and Memory are available when configured and enabled by administrators and permitted for your account and model.
- **Workspace tools**. Python scripts registered in the platform. These run on the server when the model calls them.
- **MCP (Model Context Protocol)**. Anthropic's open standard for connecting AI models to external data sources and services. MCP servers expose structured capabilities that models discover and invoke automatically.
- **OpenAPI servers**. Any web service with an OpenAPI specification can be connected as a tool provider.

### Enabling Tools Per-Chat

1. Open a conversation
2. Open **Integrations** beside the plus button in the message box
3. Browse or search available tools
4. Toggle on the tools you want for this session
   - Tools enabled this way apply only to the current conversation

### Enabling Tools Per-Model

1. Go to **Workspace > Models**
2. Edit the model you want to configure
3. Scroll to the **Tools** section
4. Select the default tools for this model
5. Click **Save & Update**
   - Share each attached tool with the intended users or course group as well as sharing the model.

### Community Tool Library

Open WebUI maintains a community library of pre-built tools. Some relevant to academic work

- **arXiv Search** — query academic papers directly from chat. No API key required.
- **Perplexica Search** — web search with inline citations.
- **Pexels Media Search** — find stock photos and videos for presentations.
- **YouTube Search & Embed** — locate and embed instructional videos.

> **Tip.** Browse the community library before building your own tool. Someone may have already solved your problem.

### Function Calling

Use a model that supports tool calling and check its **Function Calling** setting under **Advanced Parameters**. Native mode lets the model request a tool with structured arguments. Test the chosen model with each tool before sharing the configuration.

---

## Skills

Skills are reusable Markdown instructions for tasks or procedures. Attach them to a model when it needs guidance beyond its general system prompt.

### Binding Skills

1. Go to **Workspace > Models**
2. Edit the model
3. Scroll to the **Skills** section
4. Select the skills you want to bind
5. Click **Save & Update**

Share attached skills with the intended users or course group as well as sharing the model. Skills can be loaded on demand, depending on the model’s tool support and configuration; test them with the intended task.

### Example Skills for CUNY

- **Quantitative Methods**. Statistical analysis, research design, SPSS and R guidance
- **Academic Writing**. Scholarly conventions, citation practices, genre awareness
- **Research Ethics**. IRB compliance, data privacy, informed consent protocols
- **Digital Humanities**. Text analysis, corpus methods, visualization techniques

---

## Advanced Settings

<details>
<summary>View details</summary>

### Building Custom Tools

If the community library does not have what you need, administrators can write custom tools. Each tool requires a name, description, and Python function body. The function runs on the server when the model invokes it.

Open **Workspace > Tools** and choose **Create** to get started, if your account has permission. Consult with the AI Lab team if you are unsure about security implications.

### Tool Security

Tools are Python scripts that execute on the server. A poorly written or malicious tool can access system resources, exfiltrate data, or disrupt service. Only install tools from trusted sources. Contact the AI Lab team before adding community tools to the instance.

</details>

---

## Callout

<div class="callout">
  <strong>Security reminder.</strong> Review any community tool's code before installing it. Tools run with server-level access. If you are not comfortable evaluating Python code, ask the AI Lab team to review it for you.
</div>

---

## Additional Resources

- [Open WebUI Tools Documentation](https://docs.openwebui.com/features/extensibility/plugin/tools/) — official reference for tool development and configuration
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io) — Anthropic's specification for connecting AI models to external data
- [Open WebUI Community Tools](https://openwebui.com/tools) — browse and download pre-built tools

---

[← Return to Knowledge Bases](knowledge-bases.md) | [Continue to Roles & Permissions →](roles-permissions.md)
