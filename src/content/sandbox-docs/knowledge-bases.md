# Grounding AI with Knowledge Collections

A Knowledge Base lets you upload your own documents so the model searches them before responding. This process is called Retrieval-Augmented Generation (RAG): the model checks your files, retrieves relevant passages, and uses them to answer.

Consider the difference. A student asks your course model: "What does the syllabus say about late submissions?" Without a knowledge base, the model guesses, and the response might sound confident while being completely wrong. With your syllabus uploaded, the model retrieves the actual passage and cites what you wrote. At CUNY, where students navigate multiple courses, departments, and institutional policies, grounding a model in your actual materials gives students reliable answers from documents you trust.

---

## Creating a Knowledge Base

### Creating a Knowledge Base

1. Click **Workspace** in the left sidebar
2. Select **Knowledge**
3. Click **+ Create a Knowledge Base**
   - A dialog opens asking you to describe what you are building
4. Give it a **name**
   - Use something your students or colleagues will recognize: "ENG 2100 Fall 2026 Readings" or "IRB Protocol Archive"
5. Describe its **purpose**
   - A sentence or two about what you are trying to achieve. This helps you stay organized as you build more knowledge bases over time.
6. Set **visibility**
   - **Private**: only you can access it (good while you are building)
   - **Limited**: shared with specific users or groups (e.g., your course section)
   - **Public**: available to all Sandbox users
7. Click **Create**

### Uploading Documents

8. **Drag and drop files** into the knowledge base, or click to browse
   - Supported formats: PDF, Markdown, plain text
   - You can upload multiple files at once
9. Wait for processing to complete
   - The system splits your documents into chunks and creates searchable embeddings. This takes a few seconds per file.

That's it. Your documents are now searchable.

### Connecting to a Model

10. Go to **Workspace > Models** and edit the model you want to ground
11. Scroll to the **Knowledge** section
12. Select the knowledge base you just created
    - You can attach multiple knowledge bases to a single model. The system searches across all of them.
13. Click **Save**

Now every conversation with that model draws from your uploaded documents.

> **Tip:** Start with a small collection (syllabus + 2-3 key readings) to test how well the model retrieves and uses your materials. Add more documents once you are confident in the results.

---

## Advanced Settings

<details>
<summary>View details</summary>

### What Happens Under the Hood

When you upload a document, the Sandbox splits it into chunks and converts each chunk into a numerical representation called an embedding. Embeddings capture the meaning of the text, including synonyms and related concepts. This means a question about "thesis committee requirements" can surface a passage about "dissertation advisory boards" because the concepts are semantically related.

When a user asks a question, the system finds the chunks most relevant to the query and injects them into the model's context window. The model then generates its response with your documents as context.

### Choosing What to Upload

Not all documents work equally well. Clean, well-structured text produces better results than messy formatting.

**Works well:**
- Markdown files and plain text
- Well-formatted PDFs with clear headings and paragraphs
- Course syllabi, handbooks, policy documents
- Research papers and annotated bibliographies

**May need preprocessing:**
- Complex PDFs with multi-column layouts, tables, or embedded images
- Scanned documents without OCR
- Slide decks (convert to text or PDF with notes first)

If a PDF produces poor results, try converting it to Markdown first. The retrieval quality depends on how cleanly the text chunks.

### Managing Your Files

Access all uploaded files through **Settings > Data Controls > Manage Files**. This centralized manager lets you search by filename, sort by name or date, and inspect file metadata. When you delete a file here, the system performs deep cleanup: it removes the file from all knowledge bases and deletes the corresponding embeddings.

### RAG Template (Admin)

Administrators can customize how retrieved passages are presented to the model via **Admin Panel > Settings > Documents > RAG Template**. A good template tells the model to cite sources, acknowledge gaps, and prioritize retrieved content over general knowledge.

Example for CUNY:

```
You are assisting a CUNY researcher. Respond based primarily on
the provided context. When using information from documents,
indicate the source. If the context does not adequately address
the query, say so and suggest how the user might find additional
information. Prioritize accuracy over elaboration.
```

### Embedding Model Configuration

The default embedding model (Sentence Transformers MiniLM-L6) works well for most use cases. Administrators can change it in **Admin Panel > Settings > Documents**. Alternative models are available through Hugging Face. Changing the embedding model re-indexes all uploaded documents, so plan accordingly.

</details>

---

## Callout

<div class="callout">
  <strong>For researchers:</strong> Consider building knowledge bases around your methodological frameworks and foundational literature. A model grounded in your curated sources can help with literature review, source comparison, and gap identification while citing the documents you actually trust.
</div>

---

## Additional Resources

- [Open WebUI RAG Documentation](https://docs.openwebui.com) — technical details on embedding models, chunk size, and retrieval configuration
- [Teach@CUNY AI Toolkit](https://aitoolkit.commons.gc.cuny.edu/) — pedagogical resources for integrating AI into CUNY courses
- [Hugging Face Sentence Transformers](https://huggingface.co/sentence-transformers) — alternative embedding models if the default does not meet your needs

---

[← Return to Custom Models](models.md) | [Continue to Tools & Skills →](tools-skills.md)
