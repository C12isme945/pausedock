# PauseDock

**Put the work down. Keep your place.**

PauseDock turns a few scratch notes into a return card: one place to begin, what is finished, what can wait, and context worth keeping. Qwen2.5 7B runs through local Ollama. The model only returns note IDs and categories; the application copies the user's original wording into the card.

Created from an empty project directory on **24 October 2026** for the Hacktoberfest Open-Source AI Challenge, Week 3: Slow and Steady. This is a new project, not an extension of an earlier competition entry. Code and documentation were AI-assisted. All demonstrations and tests use invented, nonpersonal notes.

## Run

Requirements: Python 3.11+ and [Ollama](https://ollama.com/download). No Python packages, cloud account, API key, subscription or paid service is needed. The model download is about 4.7 GB; it needs suitable local memory and compute. Downloading software/model weights requires internet once. Subsequent inference uses only the local endpoint.

```sh
ollama pull qwen2.5:7b
python server.py
```

Open **http://127.0.0.1:8768**. If Ollama is not already running, start the Ollama application or run `ollama serve` in another terminal. Do not start a second server if one is already running. On Windows, if the installed launcher opens the Ollama app instead of handling CLI arguments, use the app's model picker to install Qwen2.5 7B.

1. Paste 2–20 notes, one thought per line, or use the synthetic garden sample.
2. Click **Make my return card**.
3. Review categories; correct any misclassification with the dropdown. Use **Start here** to select a different unfinished note.
4. Download a Markdown return card or explicitly save it in this browser.
5. Clear the session, then reopen a saved card when you return. Use its × button to remove the saved copy.

Nothing is automatically saved by the PauseDock server. Browser saving is opt-in and limited to eight cards. Browser storage is not encrypted; use it only on a device/profile you trust. Ollama is a separate application with its own storage/logging behavior. This prototype does not schedule jobs, send messages or modify any source file.

## Why open-weight AI is central

The core task is semantic classification: “not done” is different from “done”; “cannot finalise until guests reply” describes an external dependency even without the word “waiting.” The local model supplies these judgments and chooses an unfinished note as the return point. There is no keyword fallback presented as an AI result.

Ollama's structured-output JSON schema restricts the model to the input IDs and four categories. The application then independently checks complete, unique coverage, valid categories and an unfinished return reference. If validation fails, the operation reports failure and saves no card. This prevents invented card text or missing references; it **does not** prove a category is semantically correct. Human correction remains part of the experience.

The open setup keeps runtime inference on the user's machine and makes the model/prompt inspectable and replaceable in the source. This version deliberately fixes the endpoint to `127.0.0.1:11434` and the model to `qwen2.5:7b` so a cloud URL cannot be substituted accidentally. A different model requires a deliberate source edit and rechecking behavior.

## Verification and observed limitations

```sh
python -m unittest discover -s tests -v
python evaluate.py
```

The first command runs 15 deterministic checks without model access. They cover invalid/duplicate/invented references, unchanged source wording, absent output, empty/long input, local host/origin restrictions, static-file boundaries and malformed requests.

The second command makes real local-model requests for **16 synthetic notes across three small examples**. The checked-in `evidence/evaluation.json` records every example, editorial reference label, actual model label, weak keyword baseline and observed latency. Following one prompt refinement, the model agreed with all 16 editorial labels; the simple keyword baseline agreed with 13. Successful runs took 3.07–5.15 seconds on the machine used. These examples are a small development sanity check, not a blind test set or a general accuracy estimate.

The first garden run misclassified “Still need to check whether the balcony gets four hours of sun” as waiting. The development prompt was clarified: waiting requires an explicit outside dependency. The earlier outcome is retained in `evidence/first_run_observation.json`; the UI also supports correcting this kind of mistake. Model choices and runtime can vary on other machines, versions and notes.

A separate first model-loading probe took about 146 seconds. Warm runs are not a promise of fast startup. There is no independent usability study or measured time-saving claim, and no competition result is asserted. Long, ambiguous or contradictory notes can still be categorised incorrectly. Keep one thought per line and check the result.

## Files

| File | Purpose |
| --- | --- |
| `core.py` | Input limits, local model call, schema and post-generation checks |
| `server.py` | Loopback-only HTTP server and request boundaries |
| `public/` | Responsive UI, local save/reopen/delete and Markdown export |
| `tests/` | Deterministic numerical/behavior and HTTP checks |
| `evaluate.py` | Repeatable local-model development examples |
| `evidence/` | Synthetic cases, actual outputs and development observation |

## Credits and licenses

Original application code: MIT, copyright 2026 Yansong Li. No model weights are redistributed here. The existing Qwen2.5 7B model and Ollama runtime are pre-existing dependencies, not original work claimed for this entry.

- [Qwen2.5 7B through Ollama](https://ollama.com/library/qwen2.5:7b): open weights, Apache 2.0. Tested local digest `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`, Q4_K_M.
- [Qwen2.5 project](https://github.com/QwenLM/Qwen2.5).
- [Ollama](https://github.com/ollama/ollama): MIT runtime.
- [Structured outputs documentation](https://docs.ollama.com/capabilities/structured-outputs).

No partner prize category is claimed. This project uses neither Gemma nor a paid cloud service. The frontend uses system fonts and original CSS artwork, with no third-party imagery, music or UI template.
