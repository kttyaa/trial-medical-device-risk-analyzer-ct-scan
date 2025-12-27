from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32
)

model = model.to("cpu")
model.eval()


def ask_qwen_about_component(component: str) -> str:
    prompt = f"""
Component: {component}

Generate FMEA suggestions using the format below.
Output ONLY the filled content.

Failure Modes:
- 

Effects of Failure:
- 

Potential Causes (mechanical, electrical, thermal, operational):
- 

Current Controls:
- 
"""

    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to("cpu") for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=600,
            temperature=0.4,
            do_sample=True
        )

    text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    for marker in ["###", "####"]:
        text = text.replace(marker, "")

    if "Failure Modes:" in text:
        text = text[text.index("Failure Modes:"):]

    return text.strip()