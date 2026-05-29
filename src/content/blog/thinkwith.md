---
title: "The ThinkWith Tool for the Composition Classroom"
description: "A CAIL workshop participant vibe-codes a tool that gives composition students real-time feedback on whether their paragraphs genuinely 'think with' a text — and reflects on what that means for the value of a humanities education."
pubDate: 2026-06-11
authors:
  - "Nicole Walker"
tags:
  - "workshops"
  - "ai-assisted-coding"
  - "teaching"
draft: true
---

<figure>
  <img src="/images/blog/thinkwith-tool.png" alt="The ThinkWith tool's two-panel interface. On the left, three labeled text fields: 'Thinking With,' 'Being Thought Upon,' and 'Your Paragraph,' with an 'Analyze' button. On the right, an illustrated darkroom with a sheet of photographic paper in a developer tray and the prompt 'Begin writing to develop your thinking…'" />
  <figcaption>The ThinkWith tool's two-panel interface: students draft on the left, and an image develops in the darkroom on the right as their paragraph moves toward full synthesis.</figcaption>
</figure>

> “A book is a machine to think with.” — I. A. Richards

Earlier this spring, I made [a digital tool to help my students visualize the difference between their own writing and the writing produced by A.I.](https://gcdi.commons.gc.cuny.edu/2026/04/17/vibe-coding-my-way-out-of-a-teaching-problem/) Because the tool's success exceeded my expectations, I continued to attend [CUNY AI Lab's workshops](https://ailab.gc.cuny.edu/events/) at the [New Media Lab](https://newmedialab.cuny.edu/) and to build my skills. I knew that whatever the next teaching problem might be, I would likely try to vibe-code my way out of it again. Sure enough, I soon had an idea for a new tool.

For ENG 111's final paper, I asked students to choose cultural artifacts that interested them and to examine these artifacts by applying the aesthetic philosophies of Audre Lorde, Toni Morrison, Herbert Marcuse, Oscar Wilde, and/or Plato. In their first pass, my students handed in paragraphs in which quotes sat inertly next to descriptions of artifacts, the relationship between them implied but not explored.

When I pressed my students on their reasoning, some revealed that they could easily voice the relationship between the quote and the artifact; their logic just hadn't made it to the page. Others, it seemed, had intuited a relationship but couldn't articulate it yet. Their thoughts required digging.

I wanted to make a tool that would encourage students to do this digging and provide them with the kind of real-time, formative feedback one person could not possibly offer a whole class simultaneously. Because a large language model would need help determining whether a student succeeded, I arrived at the next CAIL workshop with a four-stage rubric.

* Stage 1: The student mentions the quote and the artifact but doesn't connect them. They sit inertly side by side.
* Stage 2: The student asserts a surface connection by noting shared subject matter or keyword overlap, but does not explain why the connection matters.
* Stage 3: The student establishes a thematic or conceptual link but does not derive a synthesis or new insight from the pairing.
* Stage 4: Full synthesis. The student's paragraph offers a claim or insight that requires both artifacts. If you remove either one, the claim collapses.

Using this rubric, Claude Code helped me create the [ThinkWith tool](https://kimeswalk.github.io/ThinkWith/). The tool's interface has two panels—one on the left, and one on the right. On the left, the student enters three things: a description or quotation from a text they would like to “think with,” a description or quotation from the artifact to be “thought upon,” and the third, most crucial entry: a paragraph that “thinks with” the quote, using it as a lens through which to view the artifact.

Previous workshops had taught me how to route inputs through a large language model using an API key. Once a student entered their paragraph and clicked on a button marked “Analyze,” a large language model evaluated their paragraph against the rubric I gave it. Their success registered on the right-hand side of the screen, which showed an illustrated darkroom with photographic paper immersed in developer. When students' paragraphs achieved full synthesis, an image took shape on the paper, signaling that they had contributed something of their own to the conversation.

My students greeted this tool with as much enthusiasm as they'd met the last one. Nearly all my students needed several tries to achieve synthesis, and the tool offered useful feedback each time, sometimes naming the kind of connection they were reaching for with terms like “complication,” “contrast,” “illustration,” or “extension.” We practiced as a class, celebrating all the various ways students achieved synthesis between the same quote and artifact. While decades of process-pedagogy research suggest that timely feedback is more effective than summative correction, it is often impossible to give students as much timely feedback as they need,[^1] and it was delightful to watch the tool solve this problem in real time. Students appeared not only invigorated by the tool's novelty but also more relaxed. The immediate feedback appeared to lessen their anxiety.

Ultimately, I intend this new ThinkWith tool to serve a still greater problem: the fact that the value of a humanities-based education is difficult to explain. The value of “thinking with” text is obvious outside the humanities, when written instructions help you install new software or diagnose a problem with a household appliance. That “thinking with” a text can contribute to the value of your thoughts about life more broadly is less obvious, and this problem is connected to the difficulty of quantifying or even explaining the value of a humanities-based education. In introducing the ThinkWith tool, I hope to help students recognize literature, theory, and philosophy as ancient but still-quite-potent technologies to “think with.” As I am aware, doing so requires committing all the sins of instrumentalist thinking. However, I do so in defense of all that is not so easily reduced.

[^1]: "Inside the Black Box: Raising Standards Through Classroom Assessment." Phi Delta Kappan, vol. 80, no. 2, 1998, pp. 139–148. Black and Wiliam's foundational study on formative assessment demonstrates that feedback is most effective when it is timely and integrated into the learning process rather than delivered after the fact.
