---
title: "Running the CUNY AI Lab on Open Weights"
description: "Why the CUNY AI Lab runs nearly all of its tools on open-weight models — what open weights are, what frontier models cost to run, and how open models have closed the capability gap."
pubDate: 2026-07-20
authors:
  - "CUNY AI Lab"
tags:
  - "open-weights"
  - "infrastructure"
draft: false
---

For nearly two decades, CUNY has demonstrated an intrepid commitment to open educational resources, zero-cost textbook courses, free and open-source software, and the broader promise of open infrastructure in public higher education. At the CUNY AI Lab, we seek to extend this commitment by providing open-weight language models that students, faculty, and staff can explore and customize, yielding openly licensed tools and configurations that others can adapt, reuse, and improve. The CUNY AI Lab runs nearly all of its applications on open-weight models,[^1] which cost a fraction of what the proprietary flagships cost, and have nearly closed the gap in capability. Open-weight models also keep us from depending on any single AI lab.

## What Are Open Weights?

A model's weights are the numerical values that represent what the model learned during training, encoding the statistical patterns it uses to parse input and generate responses. More specifically, "open weights" mean the AI lab developing that model has published and openly licensed those numerical values so that anyone can download and use them, provided they have enough hardware to run the model, which allows them to sell access to it, in the form of what is called inference. The CUNY AI Lab purchases access to that service from external providers that we vet and choose, with the option to change providers without changing the models we serve. Currently, our models are served through Amazon Bedrock, Cloudflare's AI Gateway, and OpenRouter.

Today, many frontier AI labs specialize in training and developing open-weight models. Prominent open-weight model families include DeepSeek, Kimi, GLM, Qwen, and Llama. Some companies offer both open- and closed-weight models; for instance, OpenAI provides both closed-weight models like GPT-5.6 and publishes smaller open-weight models like GPT-OSS, while Google similarly offers access to both closed-weight Gemini models and openly licenses open-weight Gemma models.

## What Frontier Models Cost to Run

Most people pay for AI through a subscription model, with a flat monthly fee per user. At the enterprise level (including the public sector), pricing works differently. Providers charge per token, resulting in various costs per user and per use. Although this pricing model may seem costly or unpredictable, open-weight models are often low-cost per token with very little to no trade-off in model performance.

With about 225,000 degree-seeking students across 25 campuses, CUNY operates at a scale that makes commercial AI pricing difficult to sustain. The CUNY AI Lab, therefore, runs open-weight models on a fixed budget, allowing more faculty members and graduate students to experiment with our tools, while avoiding the high per-use costs of proprietary systems.

<figure>
  <img src="/images/blog/open-weights-pricing.png" alt="Horizontal bar chart titled 'Output token pricing, July 2026.' Closed-weight models: GPT-5.5 at $30.00, Claude Opus 4.8 at $25.00, Claude Sonnet 4.6 at $15.00, and Gemini 3.1 Pro at $12.00 per million output tokens. Open-weight models: GLM-5.2 and GLM-5.1 at $4.40, Kimi K2.6 at $3.49, and DeepSeek V4 Pro at $0.87." />
  <figcaption>Figure 1. Output token pricing, July 2026. Source: vendor public pricing and competitive provider rates, retrieved July 13, 2026.</figcaption>
</figure>

In Figure 1, we can see that flagship proprietary models charge $12 to $30 per million output tokens, whereas frontier open-weight models used by the CUNY AI Lab charge $0.87 to $4.40 per million output tokens, with DeepSeek charging an order of magnitude below the cost of every major proprietary model on the chart.

## Are Open-Weight Models Good Enough?

It is fair to worry that savings come at the expense of quality when it comes to the prospect of choosing open-weight models over their closed-weight counterparts. Two major benchmarks, however, reveal that open models are quickly closing the capability gap. The first benchmark, GPQA Diamond, tasks models with completing graduate-level science questions that are hard to answer with a search engine alone. Meanwhile, SWE-bench Pro runs a set of software-engineering tasks from real open-source projects where the model must produce working fixes.

<figure>
  <img src="/images/blog/open-weights-benchmarks.png" alt="Grouped horizontal bar chart titled 'Benchmark performance, July 2026,' comparing closed-weight and open-weight models on two benchmarks. On GPQA Diamond, closed-weight scores are Gemini 3.1 Pro 94.3, Claude Opus 4.8 93.6, GPT-5.5 93.6, and Claude Sonnet 4.6 89.9; open-weight scores are GLM-5.2 91.2, Kimi K2.6 90.5, DeepSeek V4 Pro 90.1, and GLM-5.1 86.2. On SWE-bench Pro, closed-weight scores are Claude Opus 4.8 69.2, GPT-5.5 58.6, Claude Sonnet 4.6 58.1, and Gemini 3.1 Pro 54.2; open-weight scores are GLM-5.2 62.1, Kimi K2.6 58.6, GLM-5.1 58.4, and DeepSeek V4 Pro 55.4." />
  <figcaption>Figure 2. Benchmark performance, July 2026. Source: vendor model cards and benchmark aggregators, retrieved July 13, 2026.</figcaption>
</figure>

On GPQA Diamond, the best open-weight model in our [registry](https://ailab.gc.cuny.edu/models/), GLM 5.2, scored 91.2, while the best closed-weight model, Gemini 3.1 Pro, scored 94.3. Meanwhile, on SWE-bench Pro, GLM 5.2 scored 62.1, surpassing GPT-5.5 and trailing only Claude Opus by about seven points.

There is no benchmark yet that tells us whether an open-weight model is as useful as a proprietary model across the range of work a university might ask it to do. The available results suggest that the overall level is likely quite high. The recently released Kimi K3, for example, performs close to Claude Fable 5 and GPT-5.6 Sol on current evaluations, though its weights have not yet been released.

## Cost and Capability

<figure>
  <img src="/images/blog/open-weights-cost-capability.png" alt="Scatter plot titled 'Cost vs. capability, July 2026,' with USD per million output tokens on the horizontal axis and average benchmark score on the vertical axis. Open-weight models (DeepSeek V4 Pro, GLM-5.1, Kimi K2.6, GLM-5.2) cluster in the lower-left at low cost and high capability. Closed-weight models (Gemini 3.1 Pro, Claude Sonnet 4.6, Claude Opus 4.8, GPT-5.5) sit farther right at higher cost for a few more benchmark points." />
  <figcaption>Figure 3. Cost vs. capability, July 2026. Source: vendor pricing pages, vendor model cards, and benchmark aggregations, retrieved July 13, 2026.</figcaption>
</figure>

The scatter plot in Figure 3 represents capability on the vertical axis and price on the horizontal axis. The open-weight models cluster in the lower left, as they are both capable and cheap to run. The proprietary models sit to the right. Their few extra benchmark points cost several times as much per token.

[^1]: The Studios are the only exception that still runs on Claude and will move to open weights when we finalize our procurement process.
