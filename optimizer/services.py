import os
import json

from datetime import datetime

import os
import json
import re
from copy import deepcopy
from mistralai import Mistral  # adapt import if needed

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

# def get_train_by_id(train_id: str, all_trains: list) -> dict:
#     """Fetch a deep copy of the train from dataset by ID."""
#     for t in all_trains:
#         if t['id'] == train_id:
#             return deepcopy(t)
#     raise ValueError(f"Train ID {train_id} not found.")

import re
import json

# def apply_what_if(train_data: dict, scenario_text: str) -> dict:
#     """Use Mistral to modify the train JSON based on scenario."""
#     prompt = f"""
# You are an AI that updates a train JSON according to a 'what-if' scenario to output a valid JSON always.

# Train JSON:
# {train_data}

# Scenario:
# "{scenario_text}"

# Instructions:
# - Modify only the fields affected by the scenario.
# - Keep the rest of the train data unchanged.
# - Output valid JSON only, strictly following the schema.
# - Do NOT explain anything.
# - OUTPUT MUST BE STRICT JSON ONLY: no explanations, no markdown, no backticks, no hidden characters.
# - It must not break python's json.loads() function.
# """
#     response = client.chat.complete(
#         model="ministral-3b-latest",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     output_text = response.choices[0].message.content.strip()
#     print("Train data: ", train_data)
#     print("Output text:", output_text)
#     output_text = response.choices[0].message.content.strip()
#     parsed = force_json(output_text)
#     return parsed


# def simulate_train_scenario(train_id: str, scenario_text: str, all_trains: list) -> dict:
#     """Fetch a train by ID, apply a scenario, recompute scores, and generate explanation."""
#     # from scoring.optimizer import compute_scores
#     # from explainability.reason_builder import generate_explanation
    
#     # 2. Apply the scenario via Mistral
#     updated_train = apply_what_if(train_data, scenario_text)

#     print("updates_train: ", updated_train)
#     print(type(updated_train))

#     # 3. Compute scores (single train in list)
#     depot_results = compute_scores([updated_train])
#     depot_id = updated_train['depotId']
#     train_score_list = depot_results[depot_id]['trains']
#     train_score = train_score_list[0]  # extract the dict
#     print("train_score: ", train_score)

#     # 4. Generate explanation
#     explanation = generate_explanation(train_score, [updated_train])


#     return {
#         "updated_train": updated_train,
#         "score": train_score,
#         "explanation": explanation
#     }

def is_expired(cert):
    if not cert:
        return True
    try:
        # Try ISO 8601 format (e.g., 2022-11-25T23:59:00Z)
        cert_date = datetime.fromisoformat(cert.replace('Z', '+00:00'))
    except Exception:
        # Fallback to old format if needed
        try:
            date_part, time_part = cert.split(" ")
            dd, mm, yy = map(int, date_part.split("/"))
            hh = int(time_part[:2])
            mi = int(time_part[2:])
            cert_date = datetime(2000 + yy, mm, dd, hh, mi)
        except Exception:
            return True
    return cert_date < datetime.now(cert_date.tzinfo) if cert_date.tzinfo else cert_date < datetime.utcnow()

def compute_scores(trains, depot_cleaning_slots=5):
    from datetime import datetime

    def is_expired(cert):
        if not cert:
            return True
        try:
            # Try ISO 8601 format (e.g., 2022-11-25T23:59:00Z)
            cert_date = datetime.fromisoformat(cert.replace('Z', '+00:00'))
        except Exception:
            # Fallback to old format if needed
            try:
                date_part, time_part = cert.split(" ")
                dd, mm, yy = map(int, date_part.split("/"))
                hh = int(time_part[:2])
                mi = int(time_part[2:])
                cert_date = datetime(2000 + yy, mm, dd, hh, mi)
            except Exception:
                return True
        return cert_date < datetime.now(cert_date.tzinfo) if cert_date.tzinfo else cert_date < datetime.utcnow()

    depots = {}
    for t in trains:
        depots.setdefault(t['depotId'], []).append(t)

    depot_results = {}

    for depot_id, depot_trains in depots.items():
        # Normalize mileage within depot
        odometers = [t['mileage']['odometer'] for t in depot_trains]
        min_odo, max_odo = min(odometers), max(odometers)

        preliminary_scores = []

        for train in depot_trains:
            violations = []
            rs = {
                'fitness': 100,
                'jobCards': 100,
                'branding': 0,
                'mileage': 0,
                'cleaning': 0,
                'crew': 100
            }
            eligible = True

            # --- Fitness ---
            if any(is_expired(c) for c in train['certificates'].values()):
                rs['fitness'] = 0
                violations.append("Fitness certificate expired")
                eligible = False

            jc_all = train['jobCards']['all']

            # Count by priority/severity
            num_critical = sum(1 for j in jc_all if j['priority'] == "Critical")
            num_high     = sum(1 for j in jc_all if j['priority'] == "High")
            num_medium   = sum(1 for j in jc_all if j['priority'] == "Medium")
            num_low      = sum(1 for j in jc_all if j['priority'] == "Low")

            total_jc = len(jc_all)

            if num_critical > 0:
                # Any critical job card → score 0
                rs['jobCards'] = 0
                violations.append("Critical job card present")
                eligible = False
            elif total_jc > 0:
                # Weighted score: High=0.7, Medium=0.4, Low=0.1 (adjustable)
                score = 100 - ((num_high*0.7 + num_medium*0.4 + num_low*0.1) / total_jc * 100)
                rs['jobCards'] = max(0, round(score))
            else:
                rs['jobCards'] = 100


            # --- Crew ---
            if not train['crew']['assigned'] or is_expired(train['crew']['validUntil']):
                rs['crew'] = 0
                violations.append("No valid crew assigned")
                eligible = False

            # --- Branding ---
            hrs_left = train['branding']['hoursRemaining']
            target_hours = train['branding']['totalHours']
            rs['branding'] = 0
            if target_hours != 0:
                rs['branding'] = max(0, min(100, ((target_hours - hrs_left) / target_hours) * 100))

            # --- Mileage ---
            rs['mileage'] = 100 - ((train['mileage']['odometer'] - min_odo)/(max_odo - min_odo)*100) \
                            if max_odo != min_odo else 100

            preliminary_scores.append({
                'train': train,
                'totalScore': 0 if not eligible else sum(
                    [rs[k] * w / 100 for k, w in {'fitness':25,'jobCards':20,'branding':15,'mileage':15,'cleaning':10,'crew':5}.items()]
                ),
                'eligible': eligible,
                'rs': rs,
                'violations': violations
            })

        # --- Allocate cleaning slots ---
        preliminary_scores.sort(key=lambda x: x['totalScore'], reverse=True)
        slots_remaining = depot_cleaning_slots
        for entry in preliminary_scores:
            if entry['eligible'] and entry['train']['cleaningSlot'] and slots_remaining > 0:
                entry['rs']['cleaning'] = 100
                slots_remaining -= 1
            else:
                entry['rs']['cleaning'] = 0

            # Weighted total score (no stabling)
            weights = {'fitness':25,'jobCards':20,'branding':15,'mileage':15,'cleaning':10,'crew':5}
            entry['totalScore'] = 0 if not entry['eligible'] else sum(entry['rs'][k] * weights[k] / 100 for k in weights)

        # --- Build reasons ---
        depot_results[depot_id] = {'trains': []}
        for entry in preliminary_scores:
            train = entry['train']
            reason = []
            rs = entry['rs']

            if rs['fitness'] == 0:
                reason.append("Fitness certificate expired, train is ineligible")
            if rs['jobCards'] < 100:
                reason.append(f"Job card score: {rs['jobCards']}/100 is affected by number/severity of job cards")
            if rs['branding'] < 100:
                reason.append(f"Branding score: {rs['branding']}/100 (hours remaining: {train['branding']['hoursRemaining']})")
            if rs['mileage'] < 100:
                reason.append(f"Mileage score: {rs['mileage']}/100 (higher odometer reduces score)")
            if rs['cleaning'] == 0:
                reason.append("No cleaning slot allocated")
            if rs['crew'] == 0:
                reason.append("No valid crew assigned")

            ov = train.get('override', {})
            if ov.get('flag'):
                reason.append(f"Override applied: by {ov.get('by')}, category {ov.get('category')}, reason {ov.get('reason')}")

            depot_results[depot_id]['trains'].append({
                'trainId': train['id'],
                'totalScore': round(entry['totalScore']),
                'eligible': entry['eligible'],
                'relativeScores': {k: round(v) for k,v in rs.items()},
                'reason': reason,
                'violations': entry['violations']
            })

        depot_results[depot_id]['trains'].sort(key=lambda x: x['totalScore'], reverse=True)

    return depot_results


import os
from mistralai import Mistral  # adapt as needed

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

def generate_explanation(train_score, dataset):
    """
    Generates a natural-language explanation for a train's ranking using Mistral.
    Returns JSON: {"Explanation": "..."}
    """
    train_id = train_score['trainId']

    # find the full train object from dataset
    full_train = next((t for t in dataset if t['id'] == train_id), None)

    eligible = train_score['eligible']
    rs = train_score['relativeScores']
    violations = train_score['violations']

    prompt = f"""
    You are writing a performance summary for a train dashboard.

    Train ID: {train_id}
    Eligible: {eligible}
    Relative scores: {rs}
    Reasoning details: {train_score['reason']}
    Violations: {violations}
    Train data: {full_train}

    Instructions:
    - Provide a concise explanation of why this train received its scores.
    - Mention only categories that are not perfect (NOT equal to 100) or where additional context is meaningful.
    - For mileage, explicitly state the score out of 100 and explain:
        * If the score is high, the train has traveled a low distance relative to other trains, giving it a higher score and higher selection priority.
        * If the score is low, the train has traveled a lot compared to other trains, resulting in a lower score and reduced priority.
    - For branding, show the score out of 100 and emphasize whether the train is near completion (few hours remaining) or far from completion (many hours remaining).
    - If Fitness score is 0 → explicitly mention that the fitness certificate is expired.
    - If JobCards score is 0 → explicitly mention that a job card of severity "Critical" is open and unattended for this train.
    - If Cleaning or Crew score is 0 → explicitly mention absence.
    - Ignore categories with perfect scores (scores= 100) unless they provide meaningful insight.
    - If an override is present, explicitly mention: "Override applied: by {full_train.get('override', {}).get('by')}, category {full_train.get('override', {}).get('category')}, reason {full_train.get('override', {}).get('reason')}".
    - Keep the explanation 3–5 sentences, clear, actionable, and suitable for a dashboard.
    - Output should be a JSON object with this exact format: {{"Explanation": "..."}}, nothing else.
    """



    response = client.chat.complete(
        model="ministral-3b-latest",
        messages=[{"role": "user", "content": prompt}]
    )

    # extract LLM output
    explanation_text = response.choices[0].message.content.strip()

    # ensure JSON format
    return explanation_text

def process_train_dataset(train_dataset, depot_cleaning_slots=5):
    # Run optimizer
    depot_ranked = compute_scores(train_dataset, depot_cleaning_slots=depot_cleaning_slots)

    # Add explanations
    for depot_id, depot_data in depot_ranked.items():
        for train in depot_data['trains']:
            train['explanation'] = generate_explanation(train, train_dataset)

    return depot_ranked