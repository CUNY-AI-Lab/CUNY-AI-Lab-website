---
title: "Translating Shakespeare: Teaching Critical AI Literacy with a Customized Chatbot"
description: "A CUNY instructor designs a Shakespeare translation assignment in the CUNY AI Lab Sandbox, using a custom model seeded with deliberate errors to teach students to critically evaluate AI-generated interpretations."
pubDate: 2026-07-15
authors:
  - "Ellen Siyuan Pan"
tags:
  - "teaching"
  - "critical-ai-literacy"
draft: false
---

The idea for creating a translation bot for my students began with a discussion question in my introductory Shakespeare class: *What do you do when you do not understand Shakespearean language in a play?* Some said they would use online study guides; others admitted that they often turn to AI tools. That response got me thinking: since generative AI is already part of how students interact with texts, would it be possible to integrate this technology into a structured, critically reflective learning environment? Using the CUNY AI Lab's [Sandbox](https://ailab.gc.cuny.edu/), an open-source zero-retention[^1] chat interface that is being piloted in classrooms across the CUNY system, I designed a translation assignment that used a custom AI model with deliberately embedded inaccuracies, encouraging students to critically evaluate AI-generated interpretations.

The project had two goals: to help students complete a translation assignment and to familiarize them with AI tools so they could learn to engage with open-weight large language models (LLMs) ethically and effectively within a situated course context. Before introducing the assignment, I first spent class time discussing critical AI literacy. While many students were already using AI tools regularly, fewer had considered the labor implications or the presumptions underlying their operation. Using materials from the [Teach@CUNY AI Toolkit](https://aitoolkit.commons.gc.cuny.edu/), the class discussed ethical AI use, the environmental impact of computational infrastructure, and the ways LLMs reproduce biases embedded in their training data.

After that, I spent a class session [onboarding students to the Sandbox](https://cuny-ai-lab.github.io/sandbox-docs/#student-onboarding) itself. We set up individual accounts, navigated the chat window, and explored the group channels we would use for the assignment. The class also discussed the standards of successful translations and invited everyone to think carefully about the kinds of constraints we wanted to place on the system.

I then introduced students to the [custom model card](https://docs.openwebui.com/features/workspace/models/)[^2] I created, asking them to read the [system prompts](https://cuny-ai-lab.github.io/system-prompting/#1), a standing set of instructions that shapes how a custom model behaves before students' input. The model was designed as a translation tool tailored specifically for the two Shakespearean plays I was teaching at the time, *Twelfth Night* and *Antony and Cleopatra*. Its primary function was to help students render passages from those plays into modern English while deliberately incorporating a small number of subtle errors, such as contextual misinterpretations or inaccurate translations (rendering figurative language too literally, misattributing a speaker, overlooking a pun, etc.). During class, students were tasked with identifying these errors and discussing them with the custom model as part of this interactive learning exercise.

<figure>
  <img src="/images/blog/translating-shakespeare-model-card.png" alt="White interface displays model card settings with Z.ai: GLM-5 as the base. The text outlines the role of the translation assistant in Shakespeare courses." />
  <figcaption>Figure 1. Model card's configuration, including the base and system prompts.</figcaption>
</figure>

One of the first challenges was that AI systems are generally designed to avoid making mistakes, so it was surprisingly difficult to instruct the model to introduce errors deliberately. After revising the system prompt language several times, I eventually chose the instruction shown in the above screenshot. I used [Z.ai: GLM-5](https://ailab.gc.cuny.edu/models/) as the [basis](https://toloka.ai/blog/base-llm-vs-instruction-tuned-llm/) for my model card because it performed best when I tested the instructions against each available base. A multilingual component was also included: if students chose to communicate with the model in a language other than English, the AI should respond in that language, except for the translation itself, which would always remain in modern English. Since most of my students have diverse language backgrounds, this feature allowed them to engage critically with Shakespeare without forcing English to be the only language of discussion.

One major advantage of the CUNY AI Lab Sandbox is that it allows instructors to create group text channels designed for collaborative assignments. In this setup, students could see one another's interactions with the model card within the same interface. In other words, the assignment was designed to break the isolated experience students often have when interacting with commercial LLMs on their own. By encouraging students to place their prompts and conversations into a shared group channel visible to everyone in the class, I hoped they would learn from each other's prompting strategies and observe how their peers critiqued, questioned, and challenged the model's responses.

<figure>
  <img src="/images/blog/translating-shakespeare-conversation.png" alt="Two users discuss Shakespeare text in the Sandbox. The posts show dialogue from Olivia and Viola in Twelfth Night." />
  <figcaption>Figure 2. A conversation between a student and the custom model about an identified translation error.</figcaption>
</figure>

The assignment itself was straightforward. Students were asked to find several passages from two Shakespeare plays, paste them into the chat, ask the AI model to translate them, and then write a reflection on the process. In their reflections, students considered questions such as: do you find the translation compelling and convincing? Has the modern English translation honestly and loyally conveyed everything Shakespeare intended, including tone, wordplay, cultural references, and other layers of meaning? Is anything missing from the translation? Were you able to spot any mistakes the AI made? If yes, what were they? What do you think about AI as a tool after completing this assignment? In the end, students brought their reflections back to class and revised the modern English translation they received from prompting the model. The final translation should be a collaborative product between students and the AI tool within the Sandbox environment.

Admittedly, this was still a relatively small-scale experience compared to the broader and more sustained engagement with AI that I ultimately hope students will develop. Even so, I hoped the assignment would encourage students to think critically about both the possibilities and limitations of AI. Because the model was designed for a narrowly defined pedagogical purpose, students encountered AI not as an answering machine but as a tool shaped by specific goals and constraints. The exercise, therefore, invited them to reflect on how AI systems are constructed, where they can be useful, and why their outputs still require human judgment and interpretation.

[^1]: "At its core, Zero Data Retention is the practice of not storing personal or sensitive data once it is no longer necessary. This differs from traditional data management practices, where companies often store vast amounts of data indefinitely for future analytics, customer profiling, or legal backups." Read more at this [website](https://nexttechtoday.com/tech/ai/explained-zero-data-retention/).

[^2]: A model card is the configuration layer that lets an instructor customize a base model for a specific task while limiting its functionality, setting its constraints, and attaching a system prompt. For more, see this [brief tutorial](https://www.kaggle.com/code/var0101/model-cards) and this [paper](https://arxiv.org/abs/1810.03993).
