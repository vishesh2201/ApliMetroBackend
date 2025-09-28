import os
import json
import re
import sys
from copy import deepcopy
from mistralai import Mistral  # adapt import if needed

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from optimizer.services import compute_scores, generate_explanation, generate_explanation_sync

def force_json(text: str) -> dict:
    # Replace Python booleans/None with JSON equivalents
    fixed = re.sub(r'\bTrue\b', 'true', text)
    fixed = re.sub(r'\bFalse\b', 'false', fixed)
    fixed = re.sub(r'\bNone\b', 'null', fixed)

    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print("❌ Still broken JSON:", e)
        print("Raw output:", fixed)
        raise
    
# Initialize Mistral client
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])


import re
import json
import sys

def apply_what_if(train_data: dict, scenario_text: str) -> dict:
    """Use Mistral to modify the train JSON based on scenario."""
    prompt = f"""
You are an AI that updates a train JSON according to a 'what-if' scenario to output a valid JSON always.

Train JSON:
{train_data}

Scenario:
"{scenario_text}"

Instructions:
- Modify only the fields affected by the scenario.
- Keep the rest of the train data unchanged.
- Output valid JSON only, strictly following the schema.
- Do NOT explain anything.
- OUTPUT MUST BE STRICT JSON ONLY: no explanations, no markdown, no backticks, no hidden characters.
- It must not break python's json.loads() function.
"""
    response = client.chat.complete(
        model="ministral-3b-latest",
        messages=[{"role": "user", "content": prompt}]
    )

    output_text = response.choices[0].message.content.strip()
    print("Train data: ", train_data)
    print("Output text:", output_text)
    output_text = response.choices[0].message.content.strip()
    parsed = force_json(output_text)
    return parsed


def simulate_train_scenario(train_id: str, scenario_text: str, train_data: list) -> dict:
    """Fetch a train by ID, apply a scenario, recompute scores, and generate explanation."""


    # 2. Apply the scenario via Mistral
    updated_train = apply_what_if(train_data, scenario_text)

    print("updated_train: ", updated_train)
    print(type(updated_train))

    # 3. Compute scores (single train in list)
    depot_results = compute_scores([updated_train])
    depot_id = updated_train['depotId']
    train_score_list = depot_results[depot_id]['trains']
    train_score = train_score_list[0]  # extract the dict
    print("train_score: ", train_score)

    # 4. Generate explanation
    for depot_id, depot_data in depot_results.items():
        for train in depot_data['trains']:
            try:
                explanation_result = generate_explanation_sync(train, [train_data])
                print(f"    English: {explanation_result.get('english', 'N/A')}")
                print(f"    Malayalam: {explanation_result.get('malayalam', 'N/A')}")
                print(f"    Timestamp: {explanation_result.get('timestamp', 'N/A')}")
                train['explanation'] = f"{explanation_result.get('english', 'N/A')}\n{explanation_result.get('malayalam', 'N/A')}"
            except Exception as e:
                print(f"    Explanation Error: {e}")
                print("explanation result:" , explanation_result)
            print()


    return {
        "updated_train": updated_train,
        "score": train_score,
        "explanation": f"{explanation_result['english']} + { explanation_result['malayalam']}"
    }