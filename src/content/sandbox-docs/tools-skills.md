---
title: "Extending Models with Tools & Skills"
headingId: "extending-models-with-tools--skills"
---

Add a tool only when the task needs an action the model cannot perform through text alone. A skill serves a different purpose: it supplies reusable instructions for a procedure. Neither needs to be part of every course model.

## Try an Available Tool

Tools and capabilities depend on the platform configuration, your permissions, and the selected model. Seeing a tool in the Open WebUI community library does not mean it is installed in the Sandbox.

1. Open a chat and choose **Integrations** beside the plus button in the message box.
2. Browse the available options and enable the one needed for your task.
3. Make a small, non-sensitive test request. Check what the tool returned and whether the model represented that result accurately.

Selections made here apply to the current chat. If the needed option is missing, contact [ailab@gc.cuny.edu](mailto:ailab@gc.cuny.edu) rather than assuming you can install it yourself. External services may have their own access and data-handling requirements; check them before sending course or research material.

## Attach a Tool to a Model

With **Workspace** access enabled, open **Workspace > Models** and edit the model. Select connected tools in **Tools**; configure built-in Web Search or Code Interpreter under **Capabilities** and **Default Features**, when available. Select **Save & Update**.

Use a base model that supports tool calling. Its **Function Calling** setting is under **Advanced Parameters**; Native mode lets it request tools with structured arguments. Test the chosen model with each attached tool. Share the tool with the intended users or course group as well as sharing the model.

## Add Reusable Instructions with a Skill

A skill is a Markdown procedure that a model can load for a relevant task. For example, you could write the steps of an approved course feedback process as a skill instead of putting the entire procedure in the system prompt. This is a possible configuration, not a claim that a particular course skill is installed.

With the necessary Workspace permissions, create it in **Workspace > Skills** or select one shared with you. Then:

1. Edit the model in **Workspace > Models**.
2. Select the skill in **Skills**.
3. Set **Function Calling** to **Native** under **Advanced Parameters** so the model can load attached skill instructions.
4. Select **Save & Update**, then test a request that should use the skill.

Share the skill with the same intended audience. Check whether it was used as expected; attaching instructions does not guarantee compliance or grant access to additional data.

## Request or Build an Extension

<details>
<summary>Read before adding a new tool</summary>

The [Open WebUI community library](https://openwebui.com/tools) offers tools administrators can review. Send the Lab a link and explain the task before requesting installation. Workspace tools are Python code that executes on the server; malicious or poorly written code can expose data or disrupt service. Installation requires appropriate permission and code review.

Administrators or otherwise authorized developers can use **Workspace > Tools > Create** to supply a tool name, description, and Python function. Do not treat a successful small test as a security review.

Configured MCP servers and OpenAPI services provide other tool connections. Built-in capabilities such as Web Search, Image Generation, URL fetching, and Memory also depend on administrator settings and account/model permissions. Availability in the upstream platform does not establish local availability.

See the [Open WebUI tools reference](https://docs.openwebui.com/features/extensibility/plugin/tools/) and [Model Context Protocol documentation](https://modelcontextprotocol.io) for technical detail.

</details>

[← Return to Knowledge Collections](knowledge-bases.md) | [Continue to Roles & Permissions →](roles-permissions.md)
