import os
import pandas as pd
import openai


def analyze_latest_trade():
    """Use GPT-4 to summarize the most recent trade."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Missing OpenAI API key.")
        return

    if not os.path.exists("trade_log.csv"):
        print("trade_log.csv not found.")
        return

    openai.api_key = api_key

    df = pd.read_csv(
        "trade_log.csv",
        header=None,
        names=["timestamp", "symbol", "price", "action", "strategy"],
    )
    latest = df.iloc[-1].to_dict()
    prompt = (
        f"Here is the most recent trade: {latest}. "
        "Summarize what happened and suggest one improvement."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You analyze trading logs."},
                {"role": "user", "content": prompt},
            ],
        )
        message = response.choices[0].message["content"].strip()
        print(message)
    except Exception as e:
        print(f"OpenAI request failed: {e}")


if __name__ == "__main__":
    analyze_latest_trade()
