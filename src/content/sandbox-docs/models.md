---
title: "Custom Models"
headingId: "custom-models"
---

Custom models combine a base model with instructions, documents, and tools for tasks such as reviewing drafts or working through course readings. You can specify which materials the model should reference, how it should respond, and which requests it should decline. Creating this configuration does not train a new base model.

## Creating a Model

1. Request **Workspace** access by emailing the [CUNY AI Lab team](mailto:ailab@gc.cuny.edu). Once enabled, click **Workspace** in the left sidebar.
2. Select **Models**
3. Click **Create** beside the Workspace tabs
   - Enter a **Model Name**. In the editor, define its behavior, connect documents, and choose its tools.
4. Choose a **base model** from the dropdown
   - Test the available models with the kinds of prompts you plan to use before choosing one. If you need a specific model and do not see it listed, contact the CUNY AI Lab team.
5. Write a **system prompt** (see below for guidance)
6. Attach **knowledge bases** if you want the model to draw from your documents
   - See [Knowledge Bases](knowledge-bases.md) for how to create one
7. Select **Tools** for connected services, and configure Web Search or Code Interpreter under **Capabilities** and **Default Features** if available
   - See [Tools & Skills](tools-skills.md) for available options
8. Add **prompt suggestions**
   - These appear as clickable suggestions above the input bar when students open a new chat. Write examples of tasks or questions the model is configured to support.
9. Open **Access**
   - Keep **Private** while building. Use **Add Access** to share with your course group or selected users.
   - Choose **Public** only if the model should be available to all signed-in Sandbox users and your account permits it.
10. Click **Save & Create** (or **Save & Update** when editing)

## System Prompt

In step 5, write a system prompt that specifies the model’s role, boundaries, and instructional approach. For patterns, examples, and advanced prompt techniques, see [System Prompts as Instructional Design](system-prompts.md).

### Prompt Suggestions

Write short prompts that students can select to begin a task, such as choosing a statistical test or interpreting a result. Examples for a data analysis model

- "What visualization works best for this data?"
- "Help me interpret these statistical results"
- "Which test should I use for this research question?"

## Advanced Settings

<details>
<summary>View details</summary>

### Advanced Parameters

These parameters control response generation; adjust them when the default settings do not fit your task.

- **Max Tokens** caps output length. One token is roughly three-quarters of an English word. Lower limits (100-500) can cut responses short; higher limits (1000-4000) leave more room. Use the prompt to request concise responses.
- **Temperature** controls randomness. Lower values (0.1 to 0.3) reduce variation; higher values (0.7 to 1.0) allow more variation. Low temperature does not guarantee identical or accurate responses.
- **Top P** (nucleus sampling) controls diversity of word selection. Leave at default unless you have a specific reason to change it.
- **Stop Sequences** force the model to stop generating when it encounters specific text strings. Enter sequences like `<|end_of_text|>` or `User:` and press Enter.

### Switching Models Mid-Chat

You can change models during a chat by clicking the model name on the right inside the message box. The chat context carries across the switch. This lets you use different models for different stages of a task.

> **Tip.** Ask students to compare how two models respond to the same prompt.

</details>

## Callout

<div class="callout">
  <strong>For instructors.</strong> Specify which parts of an assignment the model should support and what it should do when students ask for work outside those limits. Test the configuration with likely student requests, then explain the permitted uses in the assignment instructions.
</div>

## Additional Resources

- [Open WebUI Model Configuration Docs](https://docs.openwebui.com/features/workspace/models/) — official reference for all model settings
- [Teach@CUNY AI Toolkit: Course Policies](https://aitoolkit.commons.gc.cuny.edu/course-policies/) — guidance on setting expectations for AI use in your courses
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering) — OpenAI's strategies for writing effective prompts

---

[← Return to Getting Started](getting-started.md) | [Continue to Knowledge Bases →](knowledge-bases.md)
