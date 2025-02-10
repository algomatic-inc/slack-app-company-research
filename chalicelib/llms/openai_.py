from pydantic import BaseModel
from openai import OpenAI


MODELS = {
    "gpt-4o-2024-08-06": {
        "input_cost": 2.50 / 1_000_000,
        "output_cost": 10.00 / 1_000_000,
    },
    "gpt-4o-mini": {
        "input_cost": 0.15 / 1_000_000,
        "output_cost": 0.60 / 1_000_000,
    },
}


def generate_structured_response(
    messages: list[dict],
    response_format: BaseModel,
    model: str = "gpt-4o-2024-08-06",
) -> tuple[BaseModel, float]:
    client = OpenAI()
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=response_format,
    )
    cost = 0.0
    if model in MODELS:
        cost = (
            MODELS[model]["input_cost"] * completion.usage.prompt_tokens
            + MODELS[model]["output_cost"] * completion.usage.completion_tokens
        )
    return completion.choices[0].message.parsed, cost
