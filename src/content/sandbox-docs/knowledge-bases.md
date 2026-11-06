---
title: "Grounding AI with Knowledge Collections"
headingId: "grounding-ai-with-knowledge-collections"
---

Use a knowledge collection when a custom model needs to consult the same documents across chats. Start with a small set of permitted course materials and a question whose answer you can locate yourself. Retrieval can supply useful passages, but you still need to check whether the response represents them accurately.

## Create a Knowledge Base<span id="creating-a-knowledge-base-1" aria-hidden="true"></span>

Creating collections requires **Workspace** access. If it is missing, request it from [ailab@gc.cuny.edu](mailto:ailab@gc.cuny.edu).

1. Open **Workspace > Knowledge** and select **Create** beside the tabs.
2. Enter a recognizable name and a description of the materials and intended task.
3. Keep **Private** while preparing the collection. Do not upload confidential material or other people's work without appropriate permission.
4. Select **Create Knowledge**.
5. Drag in PDF, Markdown, or plain-text files, or browse to select them. Wait for processing to finish.

Use readable text with clear headings. Scanned documents may need OCR, and multi-column PDFs, tables, or images may not be extracted as you expect. If a PDF performs poorly, inspect its text or convert it to Markdown, checking passage order before uploading again.

## Connect It to a Model

1. Open **Workspace > Models** and edit the intended model.
2. In **Knowledge**, select the collection. You can attach more than one when the task requires it.
3. Select **Save & Update**.

Attaching a collection does not grant its audience access. Before sharing the model, use **Add Access** to grant the intended course group **Read** access to the collection as well. Choose **Public** only for materials intended for all signed-in Sandbox users, where permitted.

## Check What the Model Retrieves

Ask a question tied to a specific passage, such as the late-submission policy in an uploaded syllabus. Open the cited source and compare the answer with that passage. Then ask a question the documents do not answer. Does the model acknowledge the gap, or supply an unsupported policy?

Repeat after changing the documents or model. If retrieval fails, check the file's text and the attached collection before adding more material. A larger collection is not necessarily easier to search well. Explain to students that they should consult the original reading or policy when an answer is unclear.

## Manage Files Carefully

Open **Settings > Data Controls > Manage Files** to search uploads, sort by name or date, and inspect metadata. Deleting a file there removes it from every knowledge base that uses it and deletes its embeddings. Check its uses before deletion.

## Optional Technical Details

<details>
<summary>Read about retrieval and administrator settings</summary>

During processing, documents are divided into chunks and converted into numerical representations called embeddings. These help locate related passages even when a question uses different words. Related wording does not establish that a passage answers the question.

Retrieval also depends on configuration. Native tool-calling mode can use knowledge tools to fetch passages; other modes add retrieved context automatically. Test the chosen mode with the collection rather than assuming every response consulted it.

Administrators can edit **Settings > Admin > Documents > RAG Template** to guide citation and responses to missing evidence. Embedding settings are also under **Settings > Admin > Documents**. After changing the embedding model, **Reindex** rebuilds knowledge-base embeddings; files attached directly to chats must be uploaded again. Instructors should contact the Lab rather than changing platform-wide settings to repair one collection.

The [Open WebUI retrieval reference](https://docs.openwebui.com/features/chat-conversations/rag/) explains these settings in detail.

</details>

[← Return to System Prompts](system-prompts.md) | [Continue to Tools & Skills →](tools-skills.md)
