# Chain Of Thought Prompting
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from typing import Optional,Literal
import json
import os
import json

load_dotenv()

from groq import Groq
groq_api_key = os.getenv("GROQ_API_KEY") 

client = Groq(api_key=groq_api_key)

def run_command(cmd: str):
    result = os.system(cmd)
    return result


def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    headers = {
        "User-Agent": "Mozilla/5.0"}
    response = requests.get(url,headers=headers)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    
    return "Something went wrong"

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command
}


SYSTEM_PROMPT = """You are an AI agent that solves user queries using a strict step-by-step state machine.

You MUST follow the rules below exactly.

Your responsibilities:
- Decide what to do next
- Optionally request a tool
- Produce exactly ONE JSON object per response

──────────────── RULES (MANDATORY) ────────────────
- Output ONLY one valid JSON object
- Do NOT output text outside JSON
- Do NOT output multiple JSON objects
- Do NOT use markdown
- Do NOT explain your reasoning outside JSON
- Do NOT invent steps
- Do NOT use START or OBSERVE steps
- NEVER include comments or trailing text
- After OUTPUT, STOP immediately
- If you output ANY text outside the JSON object, it is considered a failure.
If you break any rule, the response is invalid.

──────────────── ALLOWED STEPS ────────────────
- PLAN
- TOOL
- OUTPUT

──────────────── JSON FORMAT (EXACT) ────────────────
{
  "step": "PLAN" | "TOOL" | "OUTPUT",
  "content": string | null,
  "tool": string | null,
  "input": string | null
}

──────────────── STEP BEHAVIOR ────────────────

PLAN:
- Describe the next action briefly
- Do NOT call tools
- Set "tool" and "input" to null

TOOL:
- Request exactly ONE tool
- Set "tool" to the tool name
- Set "input" to a single string
- Set "content" to null

OUTPUT:
- Provide the final answer to the user
- Set "tool" and "input" to null
- STOP immediately after this response

──────────────── AVAILABLE TOOLS ────────────────
- get_weather(city: string)
- run_command(cmd: string)

──────────────── EXAMPLE ────────────────

User: What is the weather in Delhi?

Assistant:
{
  "step": "PLAN",
  "content": "The user wants the current weather, so I should call the get_weather tool",
  "tool": null,
  "input": null
}

Assistant:
{
  "step": "TOOL",
  "content": null,
  "tool": "get_weather",
  "input": "delhi"
}

(System provides OBSERVE)

Assistant:
{
  "step": "OUTPUT",
  "content": "The current weather in Delhi is cloudy with a temperature around 20°C.",
  "tool": null,
  "input": null
}"""

print("\n\n\n")

class MyOutputFormat(BaseModel):
    step: Literal["PLAN", "TOOL", "OUTPUT"] = Field(..., description="The ID of the step. Example: PLAN,  TOOL, OUTPUT,etc")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call.")
    input: Optional[str] = Field(None, description="The input params for the tool")

def safe_parse(raw: str):
    try:
        return MyOutputFormat.model_validate_json(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end != -1:
            return MyOutputFormat.model_validate_json(raw[start:end])
        raise ValueError("Invalid JSON")

message_history = [
    { "role": "system", "content": SYSTEM_PROMPT },
]

while True:
    user_query = input("👉🏻 ")
    message_history.append({"role": "user", "content": user_query})

    while True:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=message_history,
            temperature=0,
            top_p=0.1
        )

        raw = response.choices[0].message.content

        try:
            parsed = safe_parse(raw)
        except Exception:

            message_history.append({
        "role": "system",
        "content": "REMINDER: You must respond with EXACTLY ONE valid JSON object and nothing else."
    })
            continue
            

        # store assistant output
        message_history.append({"role": "assistant", "content": raw})

        if parsed.step == "PLAN":
            print("🧠", parsed.content)
            continue

        if parsed.step == "TOOL":
            tool_name = parsed.tool
            tool_input = parsed.input
            print(f"🛠️ Calling {tool_name}({tool_input})")

            tool_output = available_tools[tool_name](tool_input)

            message_history.append({
                "role": "developer",
                "content": json.dumps({
                    "step": "OBSERVE",
                    "tool": tool_name,
                    "output": tool_output
                })
            })
            continue

        if parsed.step == "OUTPUT":
            print("🤖", parsed.content)
            break
            
            