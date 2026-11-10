---
title: "Integrated Use Cases"
headingId: "integrated-use-cases"
---

These examples distinguish an instructor's reported classroom assignment from published workshop configurations. They show how a learning task shapes the model's instructions and materials. They do not establish measured learning gains or guarantee that a model is currently available to your account.

## Translate and Question a Literary Passage

In her [July 15, 2026 account](https://ailab.gc.cuny.edu/blog/translating-shakespeare/), Ellen Siyuan Pan describes a Sandbox assignment for *Twelfth Night* and *Antony and Cleopatra*. Students requested modern-English translations from a custom model instructed to include subtle errors. They checked those interpretations against the plays, reflected on what the translations preserved or missed, and returned to class to revise them.

Pan describes discussing critical AI literacy and the model's instructions with students before the assignment. The configuration allowed discussion in languages other than English while keeping the translation in modern English. Students shared prompts and exchanges through group channels to compare approaches.

To adapt this design, choose a short passage you can evaluate, define what counts as a supported interpretation, and test the configuration before sharing it. Explain any deliberately introduced errors to students as part of the exercise. Preserve the source text so students can challenge both intended mistakes and unplanned ones. Use [System Prompts](system-prompts.md) and [Student Onboarding](student-onboarding.md) for setup, rather than copying historical access instructions or assuming Pan's base-model choice remains available.

## Examine Experimental Choices Through a Text Adventure

The published [STEM Adventure Games workshop card](https://github.com/CUNY-AI-Lab/sandbox-series/blob/45ffd2a3a42c54b4b8239a14d3b4225d82da0f28/examples/model-cards.md#stem-adventure-games) opens with four experiment options and waits for a choice. It then uses attached sources to frame short scenes and procedural decisions. Its instructions ask the model to distinguish documented details from invented scenes, omit unsupported historical specifics, and pause to quote source passages when asked.

To adapt this workshop configuration, ask students to choose an experiment, explain one procedural decision, and compare a narrated observation with a source passage. The learning discussion should distinguish a game's designed consequences from a physical measurement or a historical reconstruction.

The basic card uses attached knowledge and does not require custom tools or skills. The separately documented Advanced version has different dependencies and interaction rules; do not combine their setup instructions. Check the card and your available resources before using either version. [Knowledge Collections](knowledge-bases.md) explains how to test the source material.

## Compare What Changed in a Wikipedia Revision

The published [Compare Wikipedia Edits workshop card](https://github.com/CUNY-AI-Lab/sandbox-series/blob/45ffd2a3a42c54b4b8239a14d3b4225d82da0f28/examples/model-cards.md#compare-wikipedia-edits) lets a user choose an article or work with supplied revisions. It asks the model to retain revision IDs and dates, quote the changed passages, and distinguish added or removed claims, changed qualifications, citation changes, and wording-only changes.

When working with uploaded revisions, the card instructs the model to use those saved versions rather than silently substitute newer pages. Live comparisons require successful retrieval. Missing text, dates, or links must remain identified as gaps.

For a proposed class adaptation, students can compare two verified revisions and decide which description of the change the quoted evidence supports. A changed citation does not establish improved accuracy; the comparison also cannot establish an editor's motives or effects on readers.

## Prepare an Adaptation

Choose the source and task before creating the model. Build privately if you have **Workspace** access, test with the actual materials, and check access to every attached resource before sharing with the course group. The [Sample Activities](sample-activities.md) page turns these designs into proposed short tasks; [Roles & Permissions](roles-permissions.md) covers the sharing step.

[← Return to Teaching Tips](teaching-tips.md) | [Return to Home](index.md)
