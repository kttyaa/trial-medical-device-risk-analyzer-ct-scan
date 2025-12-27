from openai import OpenAI, OpenAIError

client = OpenAI()

def generate_fmea_with_llm(component: str) -> str:
    """
    Generate FMEA description using LLM.
    If API quota is exceeded, return a fallback response.
    """
    prompt = f"""
You are a biomedical engineer assisting with Failure Mode and Effects Analysis (FMEA)
for a CT Scan medical device.

Component: {component}

Generate:
Failure Mode:
Effect of Failure:
Potential Cause:
Current Controls:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert in medical device risk management."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        return response.choices[0].message.content.strip()

    except OpenAIError:
        # Fallback (mock AI output)
        return f"""
Failure Mode: abnormal operation of {component}
Effect of Failure: degraded image quality or system interruption
Potential Cause: component wear, improper calibration, or thermal stress
Current Controls: routine maintenance, system monitoring, and safety interlocks
""".strip()
