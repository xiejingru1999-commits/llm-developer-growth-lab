# LLM Developer Growth Lab

A hands-on project exploring LLM APIs, model evaluation, developer experience, and usage analysis through OpenRouter, Python, and Excel.

## Project Goal

This project was created to understand LLMs from a developer and model-operations perspective rather than only as an end user.

The workflow covers:

- OpenRouter API integration
- OpenAI-compatible API usage
- token and request logging
- model comparison
- task success and instruction-following evaluation
- latency and output-speed analysis
- failure-pattern analysis
- developer-oriented product interpretation

## Project Structure

```text
llm-developer-growth-lab/
│
├── 02-api-demo/
│   └── openrouter_demo.py
│
├── 03-usage-analysis/
│   ├── api_usage_log.csv
│   ├── experiment_results.csv
│   └── model_comparison_results.csv
│
└── 04-model-comparison/
    ├── README.md
    ├── model_comparison.py
    ├── requirements.txt
    ├── results/
    │   └── model_comparison_v2.csv
    └── screenshots/
        └── dashboard.png


        Model Comparison

The main experiment compares three models available through OpenRouter using the same controlled developer-facing prompt.

Key metrics include:

API Success Rate
Task Success Rate
Strict Success Rate
Median Task-Success Duration
Observed Output Tokens/s

The experiment demonstrates an important distinction:

API success does not necessarily mean task success.

For the full methodology, data, findings, limitations, and failure analysis, see:

OpenRouter Model Comparison

Tools
Python
OpenRouter
OpenAI-compatible API
Microsoft Excel
Git
GitHub
Notes

This is an exploratory learning project rather than a production benchmark. Results are based on a limited number of requests and should be interpreted within the specific experimental setup.