from typing import List


def explain(key: str, model: str, messages: List[str]) -> str:
    if not key:
        return "Set OPENAI_API_KEY to enable explanations."
    try:
        from openai import OpenAI

        client = OpenAI(api_key=key)
        prompt = (
            "Даны аномальные лог-сообщения. Кратко опиши проблему, причины и шаги проверки.\n\n"
            + "\n".join(f"- {m}" for m in messages[:20])
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Ты лаконично объясняешь инциденты."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI error: {e}"

