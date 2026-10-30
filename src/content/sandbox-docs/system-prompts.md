---
title: "System Prompts as Instructional Design"
headingId: "system-prompts-as-instructional-design"
---

A system prompt tells a custom model how to approach its task before a student enters a message. Begin with what the student should do during the exchange, then describe the help the model should offer. Keep the first version small enough to test.

## Choose One Task

For a passage-comparison activity, the student might need to distinguish a changed claim from a change in wording. The model can present the passages and ask for a judgment without deciding what the revision proves. The published [Compare Wikipedia Edits workshop card](https://github.com/CUNY-AI-Lab/sandbox-series/blob/45ffd2a3a42c54b4b8239a14d3b4225d82da0f28/examples/model-cards.md#compare-wikipedia-edits) shows a fuller version of this design, including source and quotation limits.

Write down the input, the next action, and the boundary. In this case, the input is two revisions; the action is to compare their wording; the boundary is to avoid inventing missing text or inferring an editor's motives. This gives you something more concrete to test than a general instruction to be a helpful tutor.

## Write and Save the Prompt

The following is a proposed starting draft for a passage-comparison activity, not the exact workshop prompt or a tested classroom configuration:

```text
Help students compare two versions of a passage.

Ask for both versions and any source labels if they are missing.
Quote one relevant passage from each version exactly, labeled
Before and After. Ask the student what changed, then wait.

After the student responds, discuss whether the quoted wording
supports their interpretation. Distinguish a changed claim,
a changed qualification, a citation change, and wording only.
Use only categories the passages support.

Do not invent missing passages, dates, or source details.
Do not infer an editor's motives. A changed citation does not
by itself establish greater accuracy. Explain what evidence
is missing when it limits the comparison.
```

With **Workspace** access enabled:

1. Open **Workspace > Models** and create or edit the intended model.
2. Paste your instructions into **System Prompt**.
3. Add a prompt suggestion that shows students how to begin the task.
4. Keep **Access** set to **Private** while testing.
5. Select **Save & Create** or **Save & Update**.

## Test the Instructions Against Materials

Open a fresh chat and supply two short, permitted passages whose differences you have checked. Does the model quote them accurately, wait for your response, and keep its explanation within the evidence?

Next, supply only one passage. The model should ask for what is missing rather than invent the other version. Finally, ask it to explain an editor's intentions or declare which version is true. Check whether it respects the boundary you wrote. These are proposed tests; a saved prompt does not establish that they will pass.

Revise the instruction that failed and repeat the same test. If you change the base model, retest. Different models can interpret the same wording differently, and even a successful trial does not guarantee every response.

## Add Course Context Carefully

Attach a [knowledge collection](knowledge-bases.md) when the task requires recurring course materials. Instruct the model to identify the passages it uses and acknowledge missing evidence. A prompt cannot supply access to a file or tool that is not available to the configuration.

Replace course placeholders such as `{{COURSE_TITLE}}` and `{{DISCIPLINE}}` yourself. They are not automatic course settings. Open WebUI also supports system variables; check its [current variable reference](https://docs.openwebui.com/features/workspace/prompts/#system-variables) before relying on one.

Before sharing, explain the permitted uses in the assignment and review [Roles & Permissions](roles-permissions.md). Students should know which work remains theirs even if the model offers to do more.

[← Return to Custom Models](models.md) | [Continue to Knowledge Collections →](knowledge-bases.md)
