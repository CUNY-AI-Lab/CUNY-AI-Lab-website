# Integrated Use Cases

These use cases show how workspace components combine to support teaching and learning across a semester. Each describes a realistic CUNY course scenario, the models and knowledge bases built for it, and how students and instructors use them over time.

Use these as templates. Adapt the components and workflows to fit your discipline, course level, and student population.

---

## Use Case 1: Literature Review Support (Graduate Seminar)

**Context:**

A graduate seminar in Public Health requires students to conduct a systematic literature review on a health policy topic. Students must identify 20-30 relevant sources, synthesize findings, and write a review paper. Many students are unfamiliar with advanced database search strategies and struggle to evaluate source quality.

**Components:**

**Model:** Literature Review Support  
- **Base model:** DeepSeek V3.2 or Kimi K2.5 (strong reasoning and synthesis)
- **System prompt:** Guides students through literature review stages (topic refinement, search strategy development, source evaluation)
- **Knowledge base:** Uploaded documents include:
  - Methodological readings on systematic reviews
  - Sample literature reviews from the field
  - Program handbook section on citation practices
- **Tools enabled:**
  - arXiv Search (for preprints and working papers)
  - Web Search (for recent policy reports)

**Workflow:**

**Week 1-2: Topic Refinement**

Students use the model to:
- Brainstorm potential topics
- Identify key terms and related concepts
- Formulate answerable research questions

Instructor provides feedback on question scope and feasibility.

**Week 3-5: Search Strategy**

Students develop search strings with model support:
- Model suggests database-specific syntax (PubMed, Web of Science, Google Scholar)
- Students test searches and refine based on results
- Model helps identify inclusion/exclusion criteria

**Week 6-10: Source Evaluation and Annotation**

Students upload PDFs to a personal knowledge base and use the model to:
- Summarize each source
- Identify methodological approaches
- Note key findings and limitations
- Flag contradictions across sources

Students submit annotated bibliographies for formative feedback.

**Week 11-14: Synthesis and Writing**

Students use the model to:
- Identify themes across sources
- Outline the review structure
- Draft sections with evidence from their knowledge base
- Receive feedback on argument coherence

Instructor reviews drafts. Final papers submitted Week 15.

**What to Watch For:**

- Students may over-rely on model summaries without reading original sources. Require direct quotes or page-specific citations to ensure engagement.
- Model may hallucinate citations when prompted for additional sources. Remind students to verify every reference.
- Some students will struggle with prompt specificity. Provide example prompts and workshop effective questioning.

**Student-Facing Instructions:**

> Use the model to support your literature review process. It can help you refine your topic, develop search strategies, and synthesize findings. It cannot replace reading the sources yourself. You are expected to read each article, evaluate its methods, and determine its relevance to your research question. Use the model to organize your thinking, not to do your thinking for you.

---

## Use Case 2: Writing Process Scaffolding (Composition Course)

**Context:**

An undergraduate composition course (ENG 110) focuses on developing academic writing skills. Students write four essays across the semester: narrative, analysis, argument, and research-based. Many students are multilingual or returning to college after years away. They benefit from iterative feedback but the instructor cannot provide extensive comments on every draft.

**Components:**

**Model:** Writing Process Support  
- **Base model:** DeepSeek V3.2 or Kimi K2.5
- **System prompt:** Configured to ask questions instead of rewriting. Responds to drafts with feedback aligned with the course rubric.
- **Knowledge base:** Uploaded documents include:
  - Course rubric
  - Sample essays (strong and weak)
  - Style guide (APA or MLA)
  - Grammar resources
- **Tools enabled:** None (focus on text interaction)

**Workflow:**

**Essay 1: Narrative (Weeks 1-4)**

Students submit outlines and rough drafts to the model for feedback:
- Model asks: "What is the central moment in your story? How does each paragraph lead to or away from that moment?"
- Students revise based on model questions and peer feedback
- Instructor reviews final drafts

**Essay 2: Analysis (Weeks 5-8)**

Students analyze a short reading from the syllabus:
- Model helps students identify thesis, evidence, and reasoning
- Model asks: "What textual evidence supports your interpretation? What alternative interpretations might a reader consider?"
- Students submit drafts with a reflection on how they used model feedback

**Essay 3: Argument (Weeks 9-12)**

Students develop evidence-based arguments on topics of their choosing:
- Model challenges weak reasoning: "You claim X. What would someone who disagrees say? How do you respond to that objection?"
- Students revise iteratively, documenting their revision process
- Instructor provides targeted feedback on final drafts

**Essay 4: Research-Based (Weeks 13-16)**

Students integrate 5-7 sources into an argument:
- Model helps students evaluate source credibility and integrate quotations smoothly
- Model asks: "How does this source support your argument? What does it add that your other sources do not?"
- Students submit final papers with annotated bibliography and process reflection

**What to Watch For:**

- Some students will submit AI-generated essays unchanged. Process documentation (outlines, reflections) makes this visible.
- Model feedback may be too generic if students submit incomplete drafts. Require full drafts for substantive feedback.
- Multilingual students benefit from the model explaining grammar patterns. Encourage them to ask follow-up questions.

**Student-Facing Instructions:**

> The model is available to help you develop your essays. It will not write essays for you. Instead, it asks questions about your drafts to help you clarify your thinking and strengthen your arguments. You can submit outlines, rough drafts, and revised drafts for feedback. Include your revision reflections in your final submission to show how you used feedback from the model, peers, and me.

---

## Use Case 3: Research Methods Support (Methods Seminar)

**Context:**

A graduate methods seminar in Education requires students to design a small-scale research study. Students must formulate research questions, select appropriate methods, design instruments (e.g., interview protocols, surveys), and conduct preliminary data analysis. Many students are new to qualitative or quantitative methods and need support translating conceptual knowledge into practice.

**Components:**

**Model:** Methods Consultant  
- **Base model:** DeepSeek V3.2 or Kimi K2.5
- **System prompt:** Provides methodological guidance. Asks probing questions about research design choices.
- **Knowledge base:** Uploaded documents include:
  - Course readings on qualitative and quantitative methods
  - IRB guidelines and sample protocols
  - Example studies from the field
- **Tools enabled:**
  - Code Interpreter (for basic data analysis)
  - arXiv Search (for methodological literature)
- **Skills bound:** Quantitative Methods, Research Ethics

**Workflow:**

**Weeks 1-3: Research Question Development**

Students use the model to:
- Refine broad topics into answerable questions
- Explore alignment between questions and methods (qualitative, quantitative, mixed)
- Identify potential ethical concerns

Instructor provides feedback on feasibility and scope.

**Weeks 4-6: Methods Selection and Design**

Students develop study designs:
- Qualitative students: Model helps draft interview protocols and coding schemes
- Quantitative students: Model suggests statistical tests and sample size considerations
- All students: Model reviews IRB protocols for completeness

**Weeks 7-10: Data Collection and Analysis**

Students collect preliminary data and use the model to:
- Analyze qualitative data: Model helps identify themes, test coding reliability
- Analyze quantitative data: Students upload datasets to Code Interpreter, run descriptive statistics, interpret results
- Model prompts: "What patterns do you see? What surprises you? What alternative explanations might account for these findings?"

**Weeks 11-15: Writing and Presentation**

Students draft research reports and use the model to:
- Ensure alignment between questions, methods, and findings
- Strengthen discussion sections (connecting findings to literature)
- Prepare presentations for the final seminar session

**What to Watch For:**

- Students may treat the model as an authority on research design. Emphasize that it offers suggestions, not prescriptions.
- Quantitative students may struggle with Code Interpreter errors. Provide debugging workshops early in the semester.
- IRB protocols require human oversight. Review all protocols yourself before students submit to the IRB.

**Student-Facing Instructions:**

> The Methods Consultant model supports your research design process. It can help you refine questions, select methods, and interpret preliminary data. It cannot replace your engagement with the course readings or consultation with me. Use it to test ideas and get feedback on drafts. Always document your methodological choices and explain your reasoning in your final report.

---

## Use Case 4: Multilingual Academic Writing (ESL/Academic English)

**Context:**

An advanced academic writing course for multilingual graduate students. Students are fluent in their home languages but developing proficiency in academic English. They struggle with disciplinary writing conventions, sentence-level clarity, and integrating sources smoothly. The course focuses on writing in students' fields (STEM, social sciences, humanities).

**Components:**

**Model:** Language Learning Partner  
- **Base model:** Kimi K2.5 or GLM 5 (strong multilingual support)
- **System prompt:** Configured to support multilingual writers. Responds to writing in English, translates when requested, explains academic conventions.
- **Knowledge base:** Uploaded documents include:
  - Disciplinary writing samples (e.g., STEM lab reports, humanities literature reviews)
  - Style guides (APA, MLA, Chicago)
  - Grammar and usage resources
- **Tools enabled:** Translation tools (if available)

**Workflow:**

**Weeks 1-4: Disciplinary Genres**

Students analyze published writing in their fields:
- Model helps identify genre conventions (structure, tone, citation practices)
- Students draft short genre exercises (abstract, literature review paragraph, methods section)
- Model provides feedback on alignment with conventions

**Weeks 5-8: Sentence-Level Clarity**

Students submit paragraphs for sentence-level feedback:
- Model explains grammatical patterns and suggests revisions
- Students practice paraphrasing complex sentences
- Model translates difficult concepts from students' home languages to academic English

**Weeks 9-12: Source Integration**

Students work on a longer research-based paper:
- Model helps students integrate quotations, paraphrases, and citations smoothly
- Model explains how to signal author perspective (e.g., "argues," "suggests," "demonstrates")
- Students revise iteratively with model support

**Weeks 13-16: Final Paper and Presentation**

Students complete discipline-specific writing projects:
- Model provides feedback on drafts
- Students prepare oral presentations with model help (translating ideas, clarifying pronunciation)
- Final papers submitted with process reflections

**What to Watch For:**

- Students may feel self-conscious about asking "basic" grammar questions. Normalize model use for language support.
- Model explanations may be too abstract. Encourage students to ask for examples.
- Some students will use the model to translate entire drafts from their home language. Discuss when translation supports learning and when it shortcuts it.

**Student-Facing Instructions:**

> The Language Learning Partner model is designed to support your development as an academic writer in English. You can ask it to explain grammar patterns, suggest revisions, or translate concepts from your home language. Use it to strengthen your writing, not to avoid writing. The goal is for you to develop fluency in academic English over time.

---

## Use Case 5: Capstone Project Support (Senior Seminar)

**Context:**

A senior capstone seminar requires students to complete a major independent project: original research, a creative work with critical reflection, or a community-based project. Students work across the semester with milestones and checkpoints. The instructor provides guidance but cannot meet with every student weekly.

**Components:**

**Model:** Capstone Advisor  
- **Base model:** DeepSeek V3.2 or Kimi K2.5
- **System prompt:** Configured to ask guiding questions, provide accountability, and surface issues early.
- **Knowledge base:** Uploaded documents include:
  - Capstone guidelines and rubric
  - Sample capstone projects from prior years
  - Departmental resources (style guides, IRB info, presentation templates)
- **Tools enabled:**
  - arXiv Search (for research projects)
  - Code Interpreter (for data analysis projects)
  - Web Search (for current events integration)

**Workflow:**

**Weeks 1-3: Project Proposal**

Students develop proposals with model support:
- Model helps students articulate research questions or project goals
- Model asks: "What makes this project significant? How does it build on prior work in your field?"
- Students submit proposals to instructor for approval

**Weeks 4-6: Literature Review or Background Research**

Students gather sources and background material:
- Research projects: Model helps organize literature and identify gaps
- Creative projects: Model helps students situate their work in relevant artistic or theoretical traditions
- Community projects: Model helps students research best practices and case studies

**Weeks 7-10: Data Collection, Creation, or Implementation**

Students execute their projects:
- Model provides weekly check-ins: "What progress have you made this week? What obstacles have you encountered?"
- Students use model to troubleshoot problems, brainstorm solutions, and stay on track
- Instructor meets with students periodically for targeted support

**Weeks 11-14: Analysis, Reflection, and Writing**

Students draft final papers or presentations:
- Model helps students synthesize findings, reflect on process, and connect to broader themes
- Model provides feedback on drafts aligned with the rubric
- Students revise with peer and instructor feedback

**Week 15: Final Presentations**

Students present projects to peers and faculty:
- Model helps students prepare presentation slides and talking points
- Students deliver presentations and submit final written work

**What to Watch For:**

- Some students will struggle with motivation and accountability. Weekly model check-ins help but cannot replace human connection. Schedule periodic meetings.
- Students may treat the model as a supervisor. Clarify that it provides support, not approval. All major decisions require instructor feedback.
- Creative and community-based projects may push the model's limits. Encourage students to use it for process support (reflection, organization) rather than content generation.

**Student-Facing Instructions:**

> The Capstone Advisor model is available to support your project throughout the semester. Use it for weekly check-ins, brainstorming, and draft feedback. It can help you stay organized and troubleshoot problems, but it cannot replace meetings with me or your peers. Major decisions (proposal changes, methods adjustments, scope revisions) require my approval. Document your use of the model in your final process reflection.

---

## Key Takeaways Across Use Cases

These use cases share common principles:

1. **Integration over isolation:** Models work best when embedded in a workflow, not used as standalone tools.
2. **Iterative processes:** Students submit drafts, get feedback, and revise. Learning happens through iteration.
3. **Documentation and reflection:** Students document their AI use to build metacognitive awareness and demonstrate learning.
4. **Human oversight:** Instructors review critical work (proposals, final papers) and provide targeted feedback.
5. **CUNY context:** Use cases acknowledge CUNY students' diverse needs and leverage AI to provide equitable support.

---

## Additional Resources

- **[Teaching Tips](teaching-tips.md)** — conceptual frameworks for AI integration
- **[Sample Activities](sample-activities.md)** — shorter, modular exercises you can drop into courses
- **[Student Onboarding](student-onboarding.md)** — guidance for introducing students to AI tools responsibly
- **[Teach@CUNY AI Toolkit](https://aitoolkit.commons.gc.cuny.edu/)** — assignment redesign strategies and policy templates

---

[← Return to Teaching Tips](teaching-tips.md) | [Return to Home](index.md)
