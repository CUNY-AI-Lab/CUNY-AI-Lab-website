---
title: "Grounding AI with Knowledge Collections"
headingId: "grounding-ai-with-knowledge-collections"
---

A **knowledge base** contains documents the model can search before responding. Through **retrieval-augmented generation (RAG)**, the model receives relevant passages from those files as context for its response.

When a student asks, "What does the syllabus say about late submissions?", an uploaded syllabus gives the model a document to search and cite. Without that document, the model may generate a confident but incorrect response. Test whether it retrieves the relevant passage and represents your policy accurately before students rely on it.

---

## Creating a Knowledge Base<span id="creating-a-knowledge-base-1" aria-hidden="true"></span>

1. Click **Workspace** in the left sidebar
2. Select **Knowledge**
3. Click **Create** beside the Workspace tabs
   - A dialog opens asking you to describe what you are building
4. Give it a **name**
   - Use a name your students or colleagues will recognize, such as "ENG 2100 Fall 2026 Readings" or "IRB Protocol Archive"
5. Describe its **purpose**
   - A sentence or two about what you are trying to achieve. This helps you stay organized as you build more knowledge bases over time.
6. Set access
   - Keep **Private** while building. Use **Add Access** to grant your course group **Read** access.
   - Choose **Public** only for materials intended for all signed-in Sandbox users, where permitted.
7. Click **Create Knowledge**

### Uploading Documents

8. **Drag and drop files** into the knowledge base, or click to browse
   - Supported formats. PDF, Markdown, plain text
   - You can upload multiple files at once
9. Wait for processing to complete
   - The system splits your documents into chunks and creates searchable embeddings. Processing time depends on file size and the configured services.

Once processing finishes, your documents are searchable.

### Connecting to a Model

10. Go to **Workspace > Models** and edit the model you want to ground
11. Scroll to the **Knowledge** section
12. Select the knowledge base you just created
    - You can attach multiple knowledge bases to a single model so it can retrieve from those collections.
13. Click **Save & Update**

The knowledge base is now attached to the model. Grant its intended users access to the knowledge base as well as the model so they can use it for retrieval.

> **Tip.** Start with a small collection (syllabus + 2-3 key readings) to test how well the model retrieves and uses your materials. Add more documents once you are confident in the results.

---

## Advanced Settings

<details>
<summary>View details</summary>

### What Happens Under the Hood

When you upload a document, the Sandbox splits it into chunks and converts each chunk into a numerical representation called an embedding. Embeddings capture the meaning of the text, including synonyms and related concepts. This means a question about "thesis committee requirements" can surface a passage about "dissertation advisory boards" because the concepts are semantically related.

Retrieval depends on the model’s configuration. In native tool-calling mode, the model can use knowledge tools to fetch passages; other modes add retrieved context automatically. Check that it retrieves the relevant material when testing.

### Choosing What to Upload

Use clean, well-structured text so the system can divide it into usable passages.

**Works well**
- Markdown files and plain text
- Well-formatted PDFs with clear headings and paragraphs
- Course syllabi, handbooks, policy documents
- Research papers and annotated bibliographies

**May need preprocessing**
- Complex PDFs with multi-column layouts, tables, or embedded images
- Scanned documents without OCR
- Slide decks (convert to text or PDF with notes first)

If a PDF produces poor results, try converting it to Markdown first. The retrieval quality depends on how cleanly the text chunks.

### Managing Your Files

Access all uploaded files through **Settings > Data Controls > Manage Files**. This centralized manager lets you search by filename, sort by name or date, and inspect file metadata. Deleting a file here removes it from all knowledge bases and deletes the corresponding embeddings.

### RAG Template (Admin)

Administrators can customize how retrieved passages are presented to the model via **Settings > Admin > Documents > RAG Template**. A good template tells the model to cite sources, acknowledge gaps, and prioritize retrieved content over general knowledge.

Example for CUNY

```
You are assisting a CUNY researcher. Respond based primarily on
the provided context. When using information from documents,
indicate the source. If the context does not adequately address
the query, say so and suggest how the user might find additional
information. Prioritize accuracy over elaboration.
```

### Embedding Model Configuration

Administrators can check or change the embedding model in **Settings > Admin > Documents**. After changing it, use **Reindex** to rebuild knowledge-base embeddings. Files uploaded directly to chats must be uploaded again; changing the setting does not rebuild them automatically.

</details>

---

## Callout

<div class="callout">
  <strong>For researchers.</strong> Consider building knowledge bases around your methodological frameworks and foundational literature. A model grounded in your curated sources can help with literature review, source comparison, and gap identification while citing the documents you actually trust.
</div>

---

## Additional Resources

- [Open WebUI RAG Documentation](https://docs.openwebui.com/features/chat-conversations/rag/) — technical details on embedding models, chunk size, and retrieval configuration
- [Teach@CUNY AI Toolkit](https://aitoolkit.commons.gc.cuny.edu/) — pedagogical resources for integrating AI into CUNY courses
- [Hugging Face Sentence Transformers](https://huggingface.co/sentence-transformers) — alternative embedding models if the default does not meet your needs

---

[← Return to Custom Models](models.md) | [Continue to Tools & Skills →](tools-skills.md)
