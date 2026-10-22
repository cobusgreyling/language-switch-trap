![language-switch-trap](assets/header.png)

# language-switch-trap

The language can change. The task has to stay.

Three contact-centre journeys switch language in the middle. The CLI reads only the agent reply after that turn. **Task Kept** means every required fact is still in that reply. **Language Drift** means at least one fact is missing. A fact said before the switch does not count. The command prints a report and does not change the file.

The journeys are a missing claim field (en-ZA English to Afrikaans), a shift swap (en-NG English to Pidgin), and a failed delivery (English to French). Each one is stored twice: once where the agent holds the task, once where it greets the caller and drops it.

## Run

```bash
python3 -m language_switch_trap transcripts/*.jsonl
python3 -m language_switch_trap --verbose transcripts/claim-drift.jsonl
python3 -m unittest discover -s tests -v
```

No install and no API key. Python 3.11 or newer. Text only.

## Score

```
transcript                        switch                      result
--------------------------------  --------------------------  -----------------------------
transcripts/claim-drift.jsonl     en-ZA English to Afrikaans  Language Drift
transcripts/claim-kept.jsonl      en-ZA English to Afrikaans  Task Kept
transcripts/delivery-drift.jsonl  English to French           Language Drift
transcripts/delivery-kept.jsonl   English to French           Task Kept
transcripts/shift-drift.jsonl     en-NG English to Pidgin     Language Drift
transcripts/shift-kept.jsonl      en-NG English to Pidgin     Task Kept
TOTAL                             6 journeys                  Task Kept 3, Language Drift 3
```

Six replies. Three keep the task. Three drift.

| Journey | Switch | Facts required after the switch |
|---|---|---|
| Missing claim field | en-ZA English to Afrikaans | `gister`, `eis` |
| Shift swap | en-NG English to Pidgin | `tunde`, `shift` |
| Failed delivery | English to French | `14 rue de la paix`, `livraison` |

The drift replies are a fresh greeting: "Hoe kan ek vandag help?", "Wetin you want make I do?", and "Comment puis-je vous aider aujourd'hui?"

## Transcript shape

One JSON object per line. `switch` on a user turn marks the language change. `require` lists the facts the next agent reply must still contain.

```json
{"type":"journey","id":"claim-field","title":"Missing claim field","switch":"en-ZA English to Afrikaans","require":["gister","eis"]}
{"type":"user","lang":"en-ZA","text":"I need to register a claim. The incident date is missing."}
{"type":"agent","lang":"en-ZA","text":"I can register the claim once I have the incident date."}
{"type":"user","lang":"af","text":"Dit het gister gebeur. Gaan aan met die eis.","switch":true}
{"type":"agent","lang":"af","text":"Die voorvaldatum is gister. Ek registreer die eis nou."}
```

## License

MIT
