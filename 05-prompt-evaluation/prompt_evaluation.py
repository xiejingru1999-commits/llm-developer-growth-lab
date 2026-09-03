import os
import csv
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# =========================
# 1. Environment
# =========================

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError(
        "OPENROUTER_API_KEY not found. "
        "Please add it to your .env file."
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


# =========================
# 2. Experiment Settings
# =========================

# Use ONE model for all prompt variants.
# Replace this with a model ID currently available to you on OpenRouter.
MODEL = "minimax/minimax-m3:free"

RUNS_PER_PROMPT = 5

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / "prompt_evaluation_results.csv"


# =========================
# 3. Prompt Variants
# =========================

PROMPTS = {
    "A_minimal": """
Write a launch post for the following AI model:

Model: Spark-X1
Context window: 128K
Input price: $0.20 / 1M tokens
Output price: $0.80 / 1M tokens
Features:
- Tool calling
- JSON structured output
- OpenAI-compatible API

Target users:
AI application developers
""",

    "B_structured": """
Write an English launch post for developers introducing the following AI model.

Model information:
- Model: Spark-X1
- Context window: 128K
- Input price: $0.20 / 1M tokens
- Output price: $0.80 / 1M tokens
- Tool calling
- JSON structured output
- OpenAI-compatible API

Target audience:
AI application developers

Requirements:
- Write 120–180 words.
- Explain the model's main capabilities.
- Mention the context window and pricing.
- Explain why OpenAI-compatible API support is useful for developers.
- End with a short call to action.
- Do not invent information not provided above.
""",

    "C_constrained": """
You are a developer marketing manager preparing an English model launch post for an international developer community.

Your goal is to communicate the model's practical developer value clearly and accurately.

Model information:
- Model: Spark-X1
- Context window: 128K
- Input price: $0.20 / 1M tokens
- Output price: $0.80 / 1M tokens
- Tool calling
- JSON structured output
- OpenAI-compatible API

Target audience:
AI application developers evaluating models for production applications.

Write a 120–180 word launch post using exactly this structure:

Title:
[one concise title]

Key capabilities:
[2 bullet points]

Developer value:
[one short paragraph]

Pricing:
[input and output pricing]

CTA:
[one sentence]

Constraints:
- Use clear professional English.
- Mention the 128K context window.
- Mention tool calling and JSON structured output.
- Explain the practical value of OpenAI-compatible API support.
- Include both input and output pricing.
- Do not invent benchmarks, performance claims, availability information, or capabilities that are not provided.
"""
}


# =========================
# 4. Evaluation Functions
# =========================

def contains_any(text, terms):
    text_lower = text.lower()
    return any(term.lower() in text_lower for term in terms)


def evaluate_shared_quality(text):
    """
    Shared quality metrics applied to ALL prompt variants.
    Maximum score: 10
    """

    lower = text.lower()

    # 1. Basic factual coverage
    context_correct = "128k" in lower

    input_price_correct = (
        "$0.20" in text
        or "$0.2" in text
    )

    output_price_correct = (
        "$0.80" in text
        or "$0.8" in text
    )

    tool_calling_present = contains_any(
        text,
        [
            "tool calling",
            "tool-calling"
        ]
    )

    json_present = (
        "json" in lower
    )

    openai_compatible_present = (
        "openai" in lower
        and "compatib" in lower
    )

    # 2. Developer value explanation
    #
    # Stronger than simply mentioning "compatible".
    # We look for concrete migration / integration value.
    developer_value_terms = [
        "existing code",
        "existing sdk",
        "existing tools",
        "existing integration",
        "reuse",
        "without rewriting",
        "minimal code changes",
        "reduce migration",
        "easier migration",
        "easy migration",
        "switch models",
        "integrate quickly",
        "faster integration",
    ]

    developer_value_present = contains_any(
        text,
        developer_value_terms
    )

    # Give an additional point if the explanation is relatively explicit.
    developer_value_strong = (
        developer_value_present
        and openai_compatible_present
    )

    # 3. Hallucination / unsupported claims
    #
    # These claims were NOT provided in the source information.
    suspicious_claims = [
        "state-of-the-art",
        "sota",
        "best-in-class",
        "industry-leading",
        "fastest",
        "lowest latency",
        "highest performance",
        "beats",
        "outperforms",
        "benchmark",
        "99.9% uptime",
        "production-proven",
    ]

    hallucination_free = not contains_any(
        text,
        suspicious_claims
    )

    # 4. CTA
    cta_present = contains_any(
        text,
        [
            "try",
            "start building",
            "start testing",
            "build with",
            "explore",
            "test it",
            "get started",
        ]
    )

    checks = {
        "context_correct": context_correct,
        "input_price_correct": input_price_correct,
        "output_price_correct": output_price_correct,
        "tool_calling_present": tool_calling_present,
        "json_present": json_present,
        "openai_compatible_present": openai_compatible_present,
        "developer_value_present": developer_value_present,
        "developer_value_strong": developer_value_strong,
        "hallucination_free": hallucination_free,
        "cta_present": cta_present,
    }

    score = sum(int(value) for value in checks.values())

    return score, checks


def evaluate_prompt_compliance(prompt_name, text):
    """
    Evaluate requirements specific to each prompt.
    """

    word_count = len(text.split())

    if prompt_name == "A_minimal":
        # Prompt A has almost no explicit formatting constraints.
        return 1, 1, {
            "basic_response_present": bool(text.strip())
        }

    if prompt_name == "B_structured":
        checks = {
            "length_120_180": 120 <= word_count <= 180,
            "cta_present": contains_any(
                text,
                ["try", "start", "build", "explore", "test"]
            ),
        }

    elif prompt_name == "C_constrained":
        lower = text.lower()

        checks = {
            "length_120_180": 120 <= word_count <= 180,
            "title_section": "title:" in lower,
            "key_capabilities_section": "key capabilities:" in lower,
            "developer_value_section": "developer value:" in lower,
            "pricing_section": "pricing:" in lower,
            "cta_section": "cta:" in lower,
        }

    else:
        checks = {}

    passed = sum(int(value) for value in checks.values())
    total = len(checks)

    return passed, total, checks


# =========================
# 5. Run Experiment
# =========================

fieldnames = [
    "timestamp",
    "model",
    "prompt_variant",
    "run",
    "status",
    "finish_reason",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "duration_seconds",
    "observed_output_tokens_per_second",
    "word_count",
    "shared_quality_score",
    "shared_quality_max",
    "compliance_score",
    "compliance_max",
    "response",
    "error",
]


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8-sig"
) as csvfile:

    writer = csv.DictWriter(
        csvfile,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for prompt_name, prompt_text in PROMPTS.items():

        for run in range(1, RUNS_PER_PROMPT + 1):

            print(
                f"\nRunning {prompt_name} "
                f"({run}/{RUNS_PER_PROMPT})..."
            )

            start_time = time.perf_counter()

            try:
                completion = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt_text
                        }
                    ],
                    temperature=0.7,
                )

                duration = time.perf_counter() - start_time

                response_text = (
                    completion.choices[0].message.content or ""
                )

                finish_reason = completion.choices[0].finish_reason

                usage = completion.usage

                input_tokens = (
                    usage.prompt_tokens
                    if usage else None
                )

                output_tokens = (
                    usage.completion_tokens
                    if usage else None
                )

                total_tokens = (
                    usage.total_tokens
                    if usage else None
                )

                if output_tokens and duration > 0:
                    observed_tps = output_tokens / duration
                else:
                    observed_tps = None

                word_count = len(response_text.split())

                shared_score, _ = evaluate_shared_quality(
                    response_text
                )

                (
                    compliance_score,
                    compliance_max,
                    _
                ) = evaluate_prompt_compliance(
                    prompt_name,
                    response_text
                )

                writer.writerow({
                    "timestamp": datetime.now().isoformat(),
                    "model": MODEL,
                    "prompt_variant": prompt_name,
                    "run": run,
                    "status": "success",
                    "finish_reason": finish_reason,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "duration_seconds": round(duration, 3),
                    "observed_output_tokens_per_second":
                        round(observed_tps, 3)
                        if observed_tps is not None
                        else "",
                    "word_count": word_count,
                    "shared_quality_score": shared_score,
                    "shared_quality_max": 8,
                    "compliance_score": compliance_score,
                    "compliance_max": compliance_max,
                    "response": response_text,
                    "error": "",
                })

                csvfile.flush()

                print(
                    f"Success | "
                    f"quality={shared_score}/8 | "
                    f"compliance="
                    f"{compliance_score}/{compliance_max} | "
                    f"tokens={total_tokens} | "
                    f"duration={duration:.2f}s"
                )

            except Exception as e:

                duration = time.perf_counter() - start_time

                writer.writerow({
                    "timestamp": datetime.now().isoformat(),
                    "model": MODEL,
                    "prompt_variant": prompt_name,
                    "run": run,
                    "status": "error",
                    "finish_reason": "",
                    "input_tokens": "",
                    "output_tokens": "",
                    "total_tokens": "",
                    "duration_seconds": round(duration, 3),
                    "observed_output_tokens_per_second": "",
                    "word_count": "",
                    "shared_quality_score": "",
                    "shared_quality_max": 8,
                    "compliance_score": "",
                    "compliance_max": "",
                    "response": "",
                    "error": str(e),
                })

                csvfile.flush()

                print(f"ERROR: {e}")


print(f"\nExperiment finished.")
print(f"Results saved to: {OUTPUT_FILE}")