import os
import time
import csv
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY not found.")


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


model_name = "liquid/lfm-2.5-2.6b:free"


prompts = [
    {
        "prompt_id": "A",
        "use_case": "short_explanation",
        "prompt": "Explain API latency in one sentence."
    },
    {
        "prompt_id": "B",
        "use_case": "medium_explanation",
        "prompt": "Explain API latency to a junior developer in about 200 words."
    },
    {
        "prompt_id": "C",
        "use_case": "long_technical_explanation",
        "prompt": """
Explain API latency, TTFT, TPOT and throughput
for an AI developer in about 500 words.
"""
    }
]


csv_file = "experiment_results.csv"


file_exists = os.path.isfile(csv_file)

with open(csv_file, "a", newline="", encoding="utf-8-sig") as f:

    writer = csv.writer(f)

    if not file_exists:
        writer.writerow([
            "timestamp",
            "model",
            "prompt_id",
            "use_case",
            "run",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "duration_seconds",
            "status",
            "error"
        ])


    for item in prompts:

        for run in range(1, 4):

            print(
                f"\nRunning Prompt {item['prompt_id']} "
                f"- Run {run}"
            )

            start_time = time.perf_counter()

            try:

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": item["prompt"]
                        }
                    ],
                )

                duration = time.perf_counter() - start_time

                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens

                status = "success"
                error_message = ""

            except Exception as e:

                duration = time.perf_counter() - start_time

                input_tokens = 0
                output_tokens = 0
                total_tokens = 0

                status = "error"
                error_message = str(e)


            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                model_name,
                item["prompt_id"],
                item["use_case"],
                run,
                input_tokens,
                output_tokens,
                total_tokens,
                round(duration, 3),
                status,
                error_message
            ])

            f.flush()

            print(
                "Status:", status,
                "| Tokens:", total_tokens,
                "| Duration:", round(duration, 3), "s"
            )