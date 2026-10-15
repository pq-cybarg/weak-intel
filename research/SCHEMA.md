# Research block schema

Every `research/*.json` is one cited block. Matching `research/*.md` is the human narrative.

## Required

```json
{
  "as_of": "YYYY-MM-DD",
  "metadata": {
    "title": "short title",
    "layer": "proven | evidenced | speculative",
    "theme": "crypto | apt | criminal | malware | protectors | intel | blue-team | quantum | dual-use | facilities | capabilities"
  },
  "entities": [
    {
      "name": "Canonical_Id",
      "type": "apt | criminal | malware | researcher | standard | method | vendor | agency | facility | system | control | quantum | affiliate | capability | target",
      "bucket": "optional override of type->bucket",
      "notes": "public-record notes",
      "lat": null,
      "lon": null,
      "capability_tier": "industrial | commercial | artisan | unknown",
      "source": ["https://..."]
    }
  ],
  "edges": [
    {
      "from": "A",
      "to": "B",
      "kind": "targets | uses | attributed_to | protects | standardizes | authored | hosted_at | affiliates | exploits | harvests | dual_use | has_capability | survives_crqc | dies_under_crqc | got_away | did_not_get_away | route",
      "instrument": "short label",
      "confidence": "high | moderate | low",
      "status": "public-record | declassified | alleged | speculative",
      "grade": "fact | strong | moderate | weak | speculative",
      "notes": "",
      "source": ["https://..."]
    }
  ]
}
```

## Honesty rules

- Grade speculation. Never infer intent from adjacency.
- "Got away with" means *publicly documented non-accountability or delayed exposure*, not a finding of guilt.
- Collective nouns (the NSA, China, Moscow) may describe institutional *actions* with citations; they may not be given a mind (`wants`, `believes`).
- Criminal vs clear-world affiliation is an edge with a grade, not a smear.
