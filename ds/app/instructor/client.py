import instructor
from openai import OpenAI
import os


def get_instructor_client():
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")

    base_client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    return instructor.from_openai(
        base_client,
        mode=instructor.Mode.TOOLS
    )