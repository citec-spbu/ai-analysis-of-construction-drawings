from app.prompts.instructor import SYSTEM_INSTRUCTOR
from app.instructor.builder import build_instructor_input


def run_instructor(client, state, schema):
    input_text = build_instructor_input(state)

    return client.chat.completions.create(
        model="qwen/qwen3.6-plus:free",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_INSTRUCTOR
            },
            {
                "role": "user",
                "content": input_text
            }
        ],
        response_model=schema,
        temperature=0
    )