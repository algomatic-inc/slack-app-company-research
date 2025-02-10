import os

from pydantic import BaseModel
from openai import OpenAI


MODELS = {
    "sonar-reasoning-pro": {
        "input_cost": 2.00 / 1_000_000,
        "output_cost": 8.00 / 1_000_000,
        "search_cost": 5 / 1_000,
    },
    "sonar-reasoning": {
        "input_cost": 1.00 / 1_000_000,
        "output_cost": 5.00 / 1_000_000,
        "search_cost": 5 / 1_000,
    },
    "sonar-pro": {
        "input_cost": 3.00 / 1_000_000,
        "output_cost": 15.00 / 1_000_000,
        "search_cost": 5 / 1_000,
    },
    "sonar": {
        "input_cost": 1.00 / 1_000_000,
        "output_cost": 1.00 / 1_000_000,
        "search_cost": 5 / 1_000,
    },
}


def generate_response(
    messages: list[dict],
    model: str = "sonar-reasoning-pro",
) -> tuple[str, list[str], float]:
    client = OpenAI(api_key=os.environ["PERPLEXITY_API_KEY"], base_url="https://api.perplexity.ai")
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    cost = 0.0
    if model in MODELS:
        cost = (
            MODELS[model]["input_cost"] * completion.usage.prompt_tokens
            + MODELS[model]["output_cost"] * completion.usage.completion_tokens
            + MODELS[model]["search_cost"] * len(completion.citations)
        )
    return completion.choices[0].message.content, completion.citations, cost
