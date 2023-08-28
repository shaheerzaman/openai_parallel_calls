import asyncio
import openai
import json
import os

from tenacity import retry, stop_after_attempt, wait_random_exponential

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "openain_key"

general_purpose = [
    "scraping a website",
    "writing a fibonacci series",
    "predicting house prices",
]


def save_to_json(results, filename):
    with open(filename, "w") as f:
        json.dump(results, f)


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
async def python_function_generator_async(purpose):
    global total_tokens_used

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "you are a python programmer who write excellent functons",
            },
            {
                "role": "user",
                "content": f"""write a single python function for the purpose: {purpose}""",
            },
        ],
    )

    tokens = response["usage"]["total_tokens"]
    response = response["choices"][0]["message"]["content"]

    return {"purpose": purpose, "code": response, "tokens_used": tokens}


async def make_async_calls_full():
    print("async calls started")
    results = await asyncio.gather(
        *[python_function_generator_async(purpose) for purpose in general_purpose]
    )
    print("async calls finished")
    save_to_json(results, "async.json")


async def main():
    total_tokens_used = 0
    await make_async_calls_full()
    try:
        with open("async.json", "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print("Error decoding JSON")

    else:
        for item in data:
            for key, value in item.items():
                if key == "tokens_used":
                    print(f"Tokens used")
                    total_tokens_used += value

    print("Total tokens used")


if __name__ == "__main__":
    asyncio.run(main())
