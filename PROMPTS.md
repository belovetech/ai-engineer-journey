# Prompt Experiments

## Week 1 - Contact Extraction

### Goal

Extract contact details into the `Contact` schema without guessing missing
fields.

### Test Input

```text
Lead note: wants someone to walk them through pricing. Name was not captured. Email: lead@example.org
```

### Before Prompt

```text
Extract contact details from the text into the given schema. If a field is not present, leave it null - do not guess or invent values.
```

### Before Output

```json
{
  "name": null,
  "email": "lead@example.org",
  "company": null,
  "plan": "pricing",
  "demo_requested": false
}
```

### After Prompt

```text
Extract contact details from the text into the given schema. If a field is not present, leave it null - do not guess or invent values. Set demo_requested to true when the text asks for a demo, showing, walkthrough, product tour, or to be shown the product. Keep it false when the text explicitly says no demo is needed.
```

### After Output

```json
{
  "name": null,
  "email": "lead@example.org",
  "company": null,
  "plan": "pricing",
  "demo_requested": true
}
```

### What Changed

The original prompt only said to extract fields and avoid guessing. It did not
define which phrases should count as a demo request, so "walk them through
pricing" was interpreted as general pricing interest.

The revised prompt explicitly maps demo-like phrases such as "walkthrough",
"showing", and "product tour" to `demo_requested: true`, while preserving the
negative case for text like "no demo needed".
