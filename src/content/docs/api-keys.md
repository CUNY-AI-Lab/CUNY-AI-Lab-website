---
title: API keys and model access
description: Manage a personal CAIL API key and use it to send model requests.
section: API access
sectionOrder: 2
order: 1
preview: true
draft: false
---

A personal CAIL API key is the credential an authorized user sends to the Model API. Manage keys in the signed-in Model Access page supplied with your access; the Model API origin does not host key management. An active key is sent as a Bearer token when calling `/v1/chat/completions`.

## Manage your keys

In the signed-in Model Access page, authorized users can create a personal key, view its secret once, list active keys, rotate a key, or revoke it. Creating or rotating a key does not reset the account's usage allowance.

## Set up a request

Start with the API origin and active API key supplied with your access. Store both values in environment variables:

| Variable | Purpose |
| --- | --- |
| `CAIL_API_BASE_URL` | Model API origin supplied with your access, without a trailing `/v1`. |
| `CAIL_API_KEY` | Personal key sent as a Bearer token. |

Keep the API key out of source code, shared shell history, screenshots, and public logs.

## Cost and data handling

The Model API preview is operated on the CUNY AI Lab's institutional budget. Authorized CUNY users are not billed per request. Access may be limited by the account allowance or available model-provider capacity, and the Lab may pause the preview.

Send only material that your project is allowed to send. Configured model routes may use zero-data-retention settings for model requests and responses. The Sandbox and other apps have separate storage behavior. Their settings determine how they handle account data and saved work; provider and external-service terms can differ. Do not send confidential material without institutional approval.

## List available models

Send an authenticated `GET` request to `/v1/models` to retrieve the models currently discoverable through the API:

```bash
curl --silent --show-error --fail-with-body \
  --url "$CAIL_API_BASE_URL/v1/models" \
  --header "Authorization: Bearer $CAIL_API_KEY" \
  | jq -r '.data[].id'
```

Choose one of the returned identifiers and store it in `CAIL_MODEL`. The [Model Registry](../../models/) provides Lab-reviewed context for a smaller set of models.

## Send a chat completion

This request sends one non-streaming message to `/v1/chat/completions`:

```bash
response="$(
  curl --silent --show-error --fail-with-body \
    --request POST \
    --url "$CAIL_API_BASE_URL/v1/chat/completions" \
    --header "Authorization: Bearer $CAIL_API_KEY" \
    --header "Content-Type: application/json" \
    --data @- <<JSON
{
  "model": "$CAIL_MODEL",
  "messages": [
    {
      "role": "user",
      "content": "Explain this topic in two concise sentences."
    }
  ],
  "stream": false
}
JSON
)"
```

The server returns one complete JSON response because `stream` is `false`.

## Read the response

The generated text is in `response.choices[0].message.content`. If `jq` is installed, extract it with:

```bash
printf '%s\n' "$response" | jq -r '.choices[0].message.content'
```

## Usage limits

Model usage is subject to an account-level allowance shared across the account's API keys. Exact limits may change.

An exhausted allowance returns HTTP `429` with the error code `quota_exceeded`. A separate `429 upstream_rate_limited` response means the model provider is temporarily rate limited.

## Recover access

If a key is lost or exposed, stop using it and revoke or rotate it in the signed-in Model Access page. For help recovering access or resolving an account allowance, email [ailab@gc.cuny.edu](mailto:ailab@gc.cuny.edu). Never send the key itself in email or a support form.

## Preview status

This service is not generally available. Interfaces and access details may change during the preview. For access questions, contact [ailab@gc.cuny.edu](mailto:ailab@gc.cuny.edu).
