---
title: Model API Documentation
description: Preview documentation for CAIL model access and model requests.
section: Documentation
sectionOrder: 0
order: 0
preview: true
draft: false
---

CAIL API keys give authorized users access to the Model API. This preview explains how personal keys work and how to send a model request.

## API keys and model access

Authorized users manage personal keys in the signed-in Model Access page supplied with their access. The Model API origin handles model requests; it does not host key management. An active key is sent as a Bearer token when calling `/v1/chat/completions`.

- [Read the API key guide](/docs/api-keys/)
