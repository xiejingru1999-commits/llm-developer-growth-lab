# What API Success Rates Miss: Building a Small LLM Evaluation and Developer Growth Lab

When developers evaluate a new language model, a successful API response is only the beginning.

The request may return a `200` status while the answer is incomplete, ignores an output constraint, introduces unsupported claims, or takes too long for an interactive product. A model launch can also fail for reasons that have little to do with benchmark scores: unclear pricing, missing quickstart code, vague limitations, or no structured way to bring developer feedback back to the product team.

I built the [LLM Developer Growth Lab](https://github.com/xiejingru1999-commits/llm-developer-growth-lab) to explore that gap between technical availability and practical adoption.

The project combines API experimentation, request-level logging, model and prompt evaluation, dashboard analysis, developer documentation, and a simulated overseas growth workflow. It is a small personal experiment—not a production benchmark—but it helped me understand what a model growth team needs to measure and communicate beyond “the API works.”

![Prompt evaluation dashboard](https://raw.githubusercontent.com/xiejingru1999-commits/llm-developer-growth-lab/main/05-prompt-evaluation/screenshots/dashboard.png)

## From an API Call to an Evaluation Workflow

I used Python to call models through OpenRouter with an OpenAI-compatible API. For each request, I recorded operational and evaluation fields such as:

- model ID and prompt variant;
- API status and error type;
- input, output, and total tokens;
- end-to-end request duration;
- observed output tokens per second;
- word count and output-length compliance;
- task success and strict task success;
- rule-based and LLM-as-a-Judge scores.

This structure let me separate three layers that are often collapsed into a single “success” metric:

1. **API success:** Did the endpoint return a normal response?
2. **Task success:** Did the response complete the intended job?
3. **Constraint success:** Did it follow requirements such as length, format, and factual boundaries?

That distinction became the clearest lesson from the model comparison.

## Experiment 1: API Success Did Not Equal Usability

I sent the same controlled task to three models, with three runs per model. All nine requests achieved a 100% API success rate. Their task-level results, however, were very different:

- LFM 2.5-2.6B: 0% task success;
- dots-3-note-preview: 33.3% task success;
- MiniMax: 100% task success.

The failure modes were also different. Some responses reached the configured output-token ceiling without returning usable visible content. Others completed the general task but missed the requested 100–150-word range.

If I had monitored only API status, every model would have appeared equally healthy. The task and constraint metrics revealed the actual developer experience.

![Model comparison dashboard](https://raw.githubusercontent.com/xiejingru1999-commits/llm-developer-growth-lab/main/04-model-comparison/screenshots/dashboard.png)

Because there were only three runs per model, these results are observations from this setup, not general rankings. The useful outcome was the evaluation framework and the failure investigation—not a claim that one model is universally better.

## Experiment 2: More Instructions Were Not Always Better

The second experiment tested three prompt designs for the same developer-facing writing task using one generator model:

- **A — Minimal:** a short instruction with few explicit constraints;
- **B — Structured:** audience, length, content, tone, and factual requirements;
- **C — Constrained:** a fixed structure plus stricter prohibitions on unsupported claims.

Each variant was run five times, for 15 generation requests in total. I combined deterministic checks with a separate LLM judge because the first rule-based evaluator saturated: all outputs looked almost equally strong when evaluation relied mainly on keyword coverage.

Semantic judging exposed differences the rules missed. The minimal prompt received an average factual-accuracy score of 3.0/5, compared with 4.4/5 for the structured prompt and 4.6/5 for the constrained prompt. Unsupported promotional claims were a recurring issue in the minimally constrained outputs.

The structured prompt delivered the strongest observed quality–efficiency trade-off:

- highest average Judge Overall score: **4.8/5**;
- lowest average total-token usage: **516.6 tokens**;
- median latency: **3.025 seconds**.

The constrained prompt achieved the highest factual-accuracy score, but its average overall score was slightly lower at 4.6/5 and its average total-token usage was higher at 586.8. In this experiment, adding more constraints improved factual control but did not automatically improve the overall result.

The minimal prompt also showed why “shorter prompt” does not necessarily mean “lower cost.” It produced longer answers and used 740 total tokens on average—the highest of the three variants.

## Translating Evaluation into Developer Growth Work

Model evaluation becomes more useful when the findings change what developers see and what product teams do next.

For this project, I translated the technical observations into four developer-growth deliverables:

- an English launch brief explaining compatibility, use cases, and limitations;
- a developer FAQ covering API setup, latency, tokens, errors, and evaluation caveats;
- a community feedback tracker for GitHub, Hugging Face, Reddit, Discord, X, LinkedIn, Medium, and Dev.to;
- a weekly growth memo that organizes users, use cases, friction points, evidence, owners, and next actions.

This connected a full workflow:

> API data → evaluation → failure analysis → documentation → feedback tracking → growth review

The same logic can support a real model launch. A latency outlier can become a known limitation or an engineering investigation. Repeated format failures can lead to better examples or structured-output guidance. Unsupported claims can trigger documentation QA. Community questions can become FAQ updates and product priorities.

## What I Would Improve Next

The project is intentionally small. It uses limited samples, a small set of tasks and models, application-side latency measurements, and an LLM judge that can introduce its own bias.

My next iteration would include:

- more runs and task categories, including coding, extraction, translation, and tool use;
- cost calculations using provider-specific input and output pricing;
- separate time-to-first-token and generation-time measurements;
- SQL-based event analysis using user, session, channel, and trace identifiers;
- human review to calibrate automated evaluation;
- real feedback from developers who try the repository.

## Final Takeaway

The most important lesson was simple: model growth requires more than publishing an endpoint or repeating benchmark numbers.

Developers need evidence that a model works for their use case, clear expectations about cost and latency, honest limitations, and documentation that reduces trial friction. Product teams need structured signals that distinguish API failures from task failures and turn scattered feedback into decisions.

This project gave me a practical way to connect those two sides—measuring model behavior and communicating it in a form developers can use.

If you work on LLM evaluation, developer relations, or model growth, I would be interested in your feedback on the metrics and workflow. The code, results, dashboards, and documentation are available in the [GitHub repository](https://github.com/xiejingru1999-commits/llm-developer-growth-lab).

---

**Suggested tags:** `#LLM` `#AIEvaluation` `#DeveloperExperience` `#DeveloperRelations` `#OpenRouter` `#PromptEngineering`
