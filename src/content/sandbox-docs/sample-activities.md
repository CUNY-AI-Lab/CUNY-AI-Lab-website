# Sample Activities

Each activity below includes a learning objective, the model configuration you will need, step-by-step instructions for your students, and notes on what to watch for. Copy what works. Adapt the rest.

---

## 1. Source Evaluation Workshop

**Learning Objective:** Students assess AI-generated claims against verified sources.

**Model Configuration:**
- Base model: any Sandbox model (DeepSeek V3.2, Kimi K2.5, GLM 5)
- Tools: Web Search enabled
- Knowledge Base: none (intentional; students evaluate ungrounded responses)
- System prompt:

```
You respond to research questions for an undergraduate seminar.
When students ask about a topic, provide detailed claims with
specific dates, names, and statistics. Do not hedge or qualify
your responses. State everything confidently.
```

**Why this prompt:** The confident, unhedged tone produces responses that mix accurate and fabricated details. This offers students practice identifying errors. 
**Instructions for Students:**

1. Ask the model a factual question about your research topic
2. Copy the response into a document
3. Identify every specific claim (dates, statistics, names, quotations)
4. Verify each claim using library databases and primary sources
5. Mark each claim as Verified, Unverifiable, or Incorrect
6. Write a 200-word reflection: What patterns did you notice in the errors? What made some claims harder to verify than others?

**What to Watch For:** It’s natural to trust claims that include specific numbers or citations, so be sure to encourage students to articulate why specificity can create an illusion of reliability, and how to triangulate claims with potentially false or misleading citations in mind. 

**Variations:**
- **With Knowledge Base:** Repeat the exercise with a grounded model (course readings uploaded). Compare error rates. Discuss what grounding changes and what it does not.
- **Cross-model:** Run the same question through two different models. Compare what each gets right and wrong.

---

## 2. Peer Review Rehearsal

**Learning Objective:** Students practice giving constructive feedback by critiquing AI-generated writing before reviewing each other's work.

**Model Configuration:**
- Base model: any Sandbox model (DeepSeek V3.2, Kimi K2.5, GLM 5)
- Tools: none
- Knowledge Base: upload your assignment rubric and 2-3 sample papers (anonymized)
- System prompt:

```
You are a student in {{COURSE_TITLE}}. Write a first draft
responding to the assignment below. Include some strong points
and some clear weaknesses. Your writing should be uneven —
good ideas with mediocre execution in places.

Assignment: {{ASSIGNMENT_DESCRIPTION}}
```

**Why this prompt:** An intentionally uneven draft gives students safe material to practice on. They can be honest and direct in their feedback without worrying about a classmate’s feelings. 

**Instructions for Students:**

1. Generate a draft from the model
2. Read it carefully against the assignment rubric
3. Write feedback on three things:
   - One strength (cite a specific passage)
   - One structural weakness (suggest a revision)
   - One claim that needs more support (recommend a source)
4. Compare your feedback with a partner's in response to the same draft
5. Discuss: Where did you agree? Where did you differ? What does that tell you about the rubric?

**What to Watch For:** Students who are new to peer review often default to vague praise ("good job") or surface-level criticism ("needs more detail"). That’s a starting point, not a problem. Use the step 5 comparison to help them see what more specific, evidence-based feedback looks like in practice.
---

## 3. Concept Translation Exercise

**Learning Objective:** Students deepen their understanding of a concept by explaining it to audiences with different levels of expertise.

**Model Configuration:**
- Base model: any Sandbox model (DeepSeek V3.2, Kimi K2.5, GLM 5)
- Tools: none
- Knowledge Base: upload course readings covering the target concept
- System prompt:

```
You are a learning partner in {{COURSE_TITLE}}. When a student
explains a concept to you, ask clarifying questions. Point out
gaps or ambiguities in their explanation. Do not explain the
concept yourself. Your job is to help the student refine their
own understanding through questioning.
```

**Instructions for Students:**

1. Pick a key concept from this week's readings
2. Explain it to the model as if talking to a classmate who missed class
3. Respond to the model's questions and revise your explanation as needed.
4. Now explain the same concept for a general audience (no jargon, no assumed background)
5. Finally, explain it as if presenting to an expert in the field
6. Submit all three versions with a reflection: How did your understanding change across the three explanations?

**What to Watch For:** The shift from version 1 to version 3 reveals whether students can move beyond parroting definitions. Strong submissions show genuine reformulation for each audience. If a student copies the same explanation with minor vocabulary swaps, that’s an opportunity for further discussion. For instance, what does it mean to understand something well enough to explain it in your own words? What value is there to articulating your thoughts over multiple cycles of writing and revision? 

---

## 4. Data Interpretation Lab

**Learning Objective:** Students analyze data and evaluate whether AI-generated interpretations align with statistical evidence.

**Model Configuration:**
- Base model: a model with strong quantitative reasoning (DeepSeek V3.2, Qwen3 235B)
- Tools: Code Interpreter enabled
- Knowledge Base: upload a clean dataset (CSV) relevant to your course
- System prompt:

```
You help students with data analysis for {{COURSE_TITLE}}.
When given a dataset, run exploratory analysis and present
findings with visualizations. Explain statistical concepts
in plain language. Always show your code.
```

**Instructions for Students:**

1. Ask the model to describe the dataset (variables, size, structure)
2. Request a specific analysis relevant to the course topic
3. Read through the code the model generates. You do not need to understand every line, but try to follow the logic.
4. Examine the visualization. Does it represent the data accurately?
5. Ask the model to interpret the results. Do you agree with its interpretation?
6. Write a one-page analysis that includes: your research question, the analysis you requested, one thing the model got right, and one thing you would change or investigate further.

**What to Watch For:** Students may accept the model's interpretation without checking it against the actual output. Require them to resituate the visualization in terms of their analysis and to annotate it with their own observations individually or in groups. 

---

## 5. Multilingual Close Reading

**Learning Objective:** Students engage with primary sources in languages they are still acquiring, using AI as a bridge to deeper analysis.

**Model Configuration:**
- Base model: a multilingual model (Kimi K2.5, GLM 5, DeepSeek V3.2)
- Tools: none
- Knowledge Base: upload primary source texts in the target language
- System prompt:

```
You are a language learning partner for {{COURSE_TITLE}}.
Help students read texts in {{TARGET_LANGUAGE}}. When they
ask about vocabulary or grammar, explain in context. When they
ask about meaning, push them to form their own interpretation
first. Respond in {{TARGET_LANGUAGE}} unless the student
requests English.
```

**Instructions for Students:**

1. Select a passage (200-300 words) from the uploaded texts
2. Read it on your own first and note what you do not understand—be it vocabulary, grammar, or anything that feels unclear.
3. Ask the model about specific words or grammatical structures that are giving you trouble
4. After working through the language, ask the model a content question about the passage
5. The model will ask for your interpretation first. Share what you think the passage is doing.
6. Write a response (in the target language or English, per your instructor's guidelines) analyzing one aspect of the passage that surprised you or challenged your first reading.

**What to Watch For:** Many students will want to skip straight to  "What does this passage mean?"  While the system prompt is designed to redirect them, you may need to emphasize  the importance of engaging with the language before  jumping to content analysis. 
---

## Adapting These Activities

Every activity above follows the same pattern:

1. **Configure the model** to create a specific learning situation
2. **Give students a structured task** with clear steps
3. **Build in reflection** so the activity produces learning alongside output
4. **Watch for shortcuts** and redirect when students skip the thinking

You can adapt any of these activities by changing the system prompt, swapping the knowledge base, or modifying the student instructions. The model configuration creates the conditions; your assignment design creates the learning.

---

## Callout

<div class="callout">
  <strong>Share what works:</strong> If you adapt one of these activities and it goes well, tell the AI Lab team: ailab@gc.cuny.edu. With permission, your variations might become the next sample activity on this page!</div>

---

## Additional Resources

- [Teach@CUNY AI Toolkit](https://aitoolkit.commons.gc.cuny.edu/) — pedagogical resources and assignment ideas for CUNY instructors, including templates and discipline-specific guidance
- [CUNY Academic Commons](https://commons.gc.cuny.edu/) — a space to share your activities and connect with other CUNY faculty
- [Open WebUI Prompt Documentation](https://docs.openwebui.com) — technical reference for system prompt variables and model configuration

---

[← Return to Teaching Tips](teaching-tips.md) | [Continue to Student Onboarding →](student-onboarding.md)
