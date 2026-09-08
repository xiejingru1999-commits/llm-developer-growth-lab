# LLM Developer Growth Lab

A small-scale LLM evaluation and developer growth experiment based on OpenRouter and OpenAI-compatible APIs.

This project was designed to simulate part of a model overseas growth workflow: calling a model through an API, recording request-level data, evaluating output quality, analyzing latency and token behavior, and translating the findings into developer-facing launch content, FAQ, feedback tracking, and weekly growth review.

## 1. Project Background

For overseas model growth, publishing a model is not enough. Developers need to understand:

- How to call the model
- Whether the API is compatible with their existing stack
- How much it costs
- How fast it responds
- What tasks it performs well on
- Where it fails
- Whether the documentation is clear enough for a first trial

This project connects technical model evaluation with developer adoption analysis.

Instead of only asking whether a model can generate text, the project asks:

> Would a developer be able to understand, test, compare, and potentially adopt this model?

## 2. Project Goals

The project focuses on five goals:

1. Build a simple Python workflow for calling an OpenRouter model through an OpenAI-compatible API.
2. Record request-level data such as model ID, prompt type, duration, output length, API status, and error type.
3. Compare model behavior across different prompt types.
4. Separate API-level success from task-level success.
5. Turn evaluation findings into developer growth materials, including launch content, FAQ, feedback tracker, and weekly memo.

## 3. Why This Matters for Developer Growth

A model growth team needs more than benchmark numbers. It needs to understand how developers experience the model in real workflows.

This includes:

- API integration friction
- Latency and long-tail response time
- Token usage and cost expectations
- Prompt compliance
- Output reliability
- Failure modes
- Documentation gaps
- Community feedback
- Use-case fit

This project demonstrates how basic evaluation data can support model positioning, developer documentation, community feedback tracking, and weekly growth review.

## 4. Workflow Overview

The workflow contains four parts:

```text
Prompt Design
     ↓
API Request via OpenRouter
     ↓
Request-Level Logging
     ↓
Evaluation and Growth Analysis
```

The request data can then be used for:

```text
Latency Analysis
Token / Output Analysis
Task Success Evaluation
Failure Analysis
Developer FAQ
Launch Post
Community Feedback Tracker
Weekly Growth Memo
```

## 5. Technical Setup

The project uses:

- Python
- OpenRouter
- OpenAI-compatible API format
- CSV data export
- Excel analysis
- Basic dashboard-style charts
- Git and GitHub for version control

The API call follows an OpenAI-compatible structure with:

- `base_url`
- `api_key`
- `model`
- `messages`

This makes the workflow closer to how developers would test a model before integrating it into a product.

## 6. Evaluation Design

The experiment uses multiple prompt types to observe model behavior under different task conditions.

| Prompt Type | Description | Evaluation Focus |
|---|---|---|
| Prompt A | Short creative writing task | Basic output quality and instruction following |
| Prompt B | Medium structured writing task | Format control, completeness, and consistency |
| Prompt C | Longer analytical or technical task | Long-form generation, latency, and stability |

The project evaluates not only whether a response is returned, but whether the response satisfies the actual task.

## 7. Metrics Tracked

| Metric | Meaning | Developer Growth Relevance |
|---|---|---|
| API Success | Whether the API returned a valid response | Measures endpoint availability |
| Task Success | Whether the model completed the task | Measures practical usefulness |
| Strict Task Success | Whether the model followed stricter requirements | Helps identify production-level risks |
| Duration | Total request time | Reflects latency and user experience |
| Output Length | Length of generated answer | Helps estimate cost and use-case fit |
| Observed Tokens per Second | Approximate output speed | Helps compare perceived response speed |
| Error Type | API error, rate limit, timeout, or other failure | Helps improve documentation and reliability |

## 8. Key Findings

### 8.1 API success is not equal to task success

A request may return a valid API response but still fail the user’s actual task. This means growth teams should not only look at call volume or API availability. They should also track whether developers receive useful outputs.

### 8.2 Latency affects adoption

Latency is a major developer experience factor. A slow model may still be acceptable for batch writing or offline analysis, but it is less suitable for interactive chatbots, coding assistants, support tools, or agent workflows.

### 8.3 Documentation reduces trial friction

Developers need clear information before testing a model:

- Model ID
- Base URL
- API key setup
- Context window
- Pricing
- Quickstart code
- Known limitations
- Error handling
- Recommended use cases

Unclear documentation can reduce adoption even when the model itself is capable.

### 8.4 Failure analysis can become product feedback

Failure patterns such as unsupported claims, incomplete output, latency spikes, format errors, or unclear model behavior can be converted into product, documentation, and growth recommendations.

## 9. Developer Growth Deliverables

This repository includes several developer growth documents:

| Document | Purpose |
|---|---|
| [`docs/launch-post.md`](docs/launch-post.md) | Simulates an English model launch brief for overseas developers |
| [`docs/developer-faq.md`](docs/developer-faq.md) | Answers common developer questions about API usage, latency, token cost, context window, and failure modes |
| [`docs/community-feedback-tracker.md`](docs/community-feedback-tracker.md) | Provides a structured template for tracking overseas developer feedback across OpenRouter, Hugging Face, GitHub, Reddit, Hacker News, Discord, X, LinkedIn, Medium, and Dev.to |
| [`docs/weekly-growth-memo.md`](docs/weekly-growth-memo.md) | Simulates a weekly model growth review: who used it, how they used it, where they got stuck, and what to do next |
| [`docs/project-summary-article.md`](docs/project-summary-article.md) | Summarizes the experiment, findings, limitations, and developer-growth lessons in a publishable English article |

## 10. Results Dashboards

The dashboards below were created from the experiment results in this repository. They summarize two complementary views: model-level reliability and prompt-level quality, cost, and latency.

### Model Comparison Dashboard

![Model Comparison Dashboard](04-model-comparison/screenshots/dashboard.png)

All three models returned technically successful API responses in the nine-request comparison, but task success ranged from 0% to 100%. This illustrates why endpoint availability, task completion, and strict instruction compliance need to be tracked separately.

### Prompt Evaluation Dashboard

![Prompt Evaluation Dashboard](05-prompt-evaluation/screenshots/dashboard.png)

Across 15 generation requests, the structured prompt produced the highest average Judge Overall score (4.8/5), the lowest average total-token usage (516.6), and a median latency of 3.025 seconds. The constrained prompt achieved the highest average Judge Accuracy score (4.6/5).

> These are exploratory results from small samples: three runs per model in the model comparison and five runs per prompt variant in the prompt evaluation. They describe this test setup and should not be interpreted as production benchmarks or universal model rankings.

## 11. Example Growth Questions

This project is designed to answer questions such as:

- Which prompt type creates the highest latency?
- Which task type causes more incomplete outputs?
- Is the model better for short-form or long-form tasks?
- What information should be added to the model page before launch?
- What should be included in the FAQ?
- Which failure modes should be escalated to product or engineering?
- What should the team track after publishing the model?

## 12. Relevance to Model Overseas Growth

This project is relevant to model overseas growth because it combines:

- OpenRouter platform understanding
- OpenAI-compatible API usage
- Request-level data logging
- Token and latency analysis
- LLM evaluation
- Developer documentation
- Community feedback tracking
- Weekly growth review
- English technical communication

It simulates a practical workflow for supporting model launch, developer adoption, feedback collection, and usage analysis.

## 13. Limitations

This is a small-scale personal experiment, not a full production benchmark.

Current limitations include:

- Small sample size
- Limited number of tested models
- Limited prompt diversity
- No real external user cohort
- No long-term retention data
- Simple evaluation criteria
- Possible rate limit impact
- Limited cost estimation precision

Future improvements could include more models, more prompt categories, real community feedback, larger-scale logging, SQL-based analysis, and BI dashboard integration.

## 14. Next Steps

Potential next steps:

1. Add more model providers for comparison.
2. Add more prompt categories, including coding, summarization, translation, and agent-style tasks.
3. Build a more complete token cost calculator.
4. Add SQL-based usage analysis.
5. Add real community feedback examples.
6. Improve charts and dashboard screenshots.
7. Compare model launch strategies across OpenAI, Anthropic, DeepSeek, Mistral, and Qwen.

## 15. Project Summary

This project shows how a candidate with product, content, and data analysis skills can support model overseas growth.

The core value is not only calling an LLM API, but turning model behavior into structured developer insights:

```text
API Data → Evaluation → Failure Analysis → Documentation → Feedback Tracking → Growth Review
```

That workflow is directly relevant to model launch, developer relations, and overseas growth operations.
