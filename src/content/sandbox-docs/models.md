---
title: "Custom Models"
headingId: "custom-models"
---

Create a custom model when you want to reuse instructions and materials for a particular task. Begin with one task you can test, such as asking questions about a course passage. You can add documents and tools later; creating the configuration does not train a new base model.

## Create a Private Configuration

You need **Workspace** access to build a model. Individual Lab access does not include it automatically; request it from [ailab@gc.cuny.edu](mailto:ailab@gc.cuny.edu).

1. Open **Workspace > Models** and select **Create** beside the tabs.
2. Enter a **Model Name** that identifies the task or course, then choose a base model. Test models available in the selector before deciding; contact the Lab if a required model is missing.
3. In **System Prompt**, describe what the model should do and what work remains with the student. Use the [prompt walkthrough](system-prompts.md) to draft those instructions.
4. Add prompt suggestions that show how to begin the intended task. These appear above the input bar in a new chat.
5. Open **Access** and keep **Private** while building.
6. Select **Save & Create**, or **Save & Update** when editing an existing model.

Now open a new chat with this configuration. Try a likely student question, an unclear request, and a request outside the assignment's limits. Compare the response with your instructions. A prompt asks the model to behave a certain way; it cannot guarantee that behavior.

## Add Materials Only When Needed

If the task depends on course readings, attach a tested collection in **Knowledge**. Follow [Knowledge Collections](knowledge-bases.md) to prepare the files and check whether the model retrieves relevant passages.

Use **Tools** for connected services. Web Search and Code Interpreter are configured under **Capabilities** and **Default Features**, when available. [Tools & Skills](tools-skills.md) explains the permissions and tests these additions require. Leave unused capabilities off so students can understand what the configuration is doing.

## Test, Then Share

Test with the actual materials students will use, including a question the materials cannot answer. Check citations and look for invented details, excessive help, or ignored boundaries. Revise one part of the configuration and repeat the same test before adding another feature.

When ready, open **Access**, keep **Private**, and use **Add Access** to grant your course group **Read** access. Share attached knowledge collections, tools, and skills with the intended users too. Use **Write** only for collaborators who should edit. **Public**, where permitted, makes the resource available to all signed-in Sandbox users. See [Roles & Permissions](roles-permissions.md).

## Adjust Generation Settings

<details>
<summary>Open optional advanced settings</summary>

Start with defaults. **Max Tokens** limits output length and can cut a response short; request concise answers in the prompt rather than relying only on a small limit. **Temperature** changes response variation, but lowering it does not guarantee accuracy or identical answers. Leave **Top P** at its default unless you have a specific reason to change it.

**Stop Sequences** end generation when matching text appears. Use them only when the task requires that behavior and test for premature stops. Available parameters and their effects depend on the base model.

You can switch models from the selector during a chat, but the existing context carries over. Use fresh chats when testing a changed configuration from the same starting point.

</details>

The [Open WebUI model reference](https://docs.openwebui.com/features/workspace/models/) covers the wider editor. For a course setup, continue with the features your task needs.

[← Return to Sandbox Basics](sandbox-basics.md) | [Continue to System Prompts →](system-prompts.md)
