from datetime import datetime

import os
import asyncio
from mistralai import Mistral  # adapt as needed
from googletrans import Translator

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
translator = Translator()

# Global event loop for all translations
_translation_loop = None

def get_or_create_loop():
    """Get or create a single event loop for all translations"""
    global _translation_loop
    if _translation_loop is None or _translation_loop.is_closed():
        _translation_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_translation_loop)
    return _translation_loop

async def generate_explanation(train_score, dataset):
    """Async version with proper event loop handling"""
    train_id = train_score['trainId']
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
        * If the score is high, the train has traveled a low distance relative to other trains in the same depot, giving it a higher score and higher selection priority.
        * If the score is low, the train has traveled a lot compared to other trains in the same depot, resulting in a lower score and reduced priority.
    - For branding, show the score out of 100 and explain:
        * If score is -1: "Branding criterion cannot be met - requires more daily hours than available (16.5 hrs max)"
        * If score is 0: "Branding score is 0 - no branding contractual obligations"
        * If score is 0-99: "Branding score indicates urgency - needs X hours per day to meet deadline"
        * If score is 100: "Branding contract is fulfilled"
    - If Fitness score is 0 -> explicitly mention that one or more fitness certificates are expired.
    - For JobCards score:
        * If score is 0 -> explicitly mention that one or more job cards of severity "Critical" are open and unattended for this train.
        * If score is 1-99 -> mention the weighted impact of High/Medium/Low priority job cards on the score.
        * If score is 100 -> no job cards or only Low priority cards present.
    - If Crew score is 0 -> explicitly mention that no valid crew is assigned or crew certification is expired.
    - Ignore categories with perfect scores (scores= 100) unless they provide meaningful insight.
    - If an override is present, explicitly mention: "Override applied: by {full_train.get('override', {}).get('by')}, category {full_train.get('override', {}).get('category')}, reason {full_train.get('override', {}).get('reason')}".
    - Keep the explanation 3–5 sentences, clear, actionable, and suitable for a dashboard.
    - Output should be a JSON object with this exact format: {{"Explanation": "..."}}, nothing else.
    """

    response = client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}]
    )

    explanation_text = response.choices[0].message.content.strip()
    
    import json
    try:
        explanation_data = json.loads(explanation_text)
        english_explanation = explanation_data.get("Explanation", explanation_text)
    except json.JSONDecodeError:
        english_explanation = explanation_text
    
    # Translate to Malayalam with proper error handling
    try:
        translation_result = await translator.translate(english_explanation, dest='ml')
        malayalam_translation = translation_result.text
    except Exception as e:
        print(f"Translation error: {e}")
        malayalam_translation = "Translation not available"
    
    # Return formatted JSON with separate keys
    return {
        "trainId": train_id,
        "english": english_explanation,
        "malayalam": malayalam_translation,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

def generate_explanation_sync(train_score, dataset):
    """Synchronous wrapper that reuses the same event loop"""
    import asyncio
    try:
        coro = generate_explanation(train_score, dataset)
        try:
            # Try to get the running event loop (ASGI, Jupyter, etc.)
            loop = asyncio.get_running_loop()
            # If we're already in an event loop, use asyncio.run_coroutine_threadsafe if possible
            # But in main thread, this will fail, so fallback to create_task and wait
            fut = asyncio.ensure_future(coro)
            # If in main thread, run_until_complete will fail, so use add_done_callback and wait
            # But in most cases, just await fut (not possible in sync context), so use loop.run_until_complete if possible
            # Instead, use asyncio.run if available (Python 3.7+)
            # But since we're in sync context, safest is to raise error and fallback
            raise RuntimeError("Event loop is already running")
        except RuntimeError:
            # No event loop running, safe to use run_until_complete
            loop = get_or_create_loop()
            result = loop.run_until_complete(coro)
            return result
    except Exception as e:
        print(f"Explanation error: {e}")
        return {
            "trainId": train_score.get('trainId', 'Unknown'),
            "english": "Error generating explanation",
            "malayalam": "Translation not available",
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }

def generate_bilingual_explanation(train_score, dataset):
    """
    Alternative function that returns structured bilingual explanation
    """
    train_id = train_score['trainId']
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
    - For branding, show the score out of 100 and emphasize whether the train is near completion (few hours remaining) or far from completion (many hours remaining). Also iterate the fact that low score== less branding hours left to fullfil, high score== comparatively more brandiing hours left to be completed.
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

    explanation_text = response.choices[0].message.content.strip()
    
    # Parse the JSON to get the English explanation
    import json
    try:
        explanation_data = json.loads(explanation_text)
        english_explanation = explanation_data.get("Explanation", explanation_text)
    except json.JSONDecodeError:
        english_explanation = explanation_text
    
    # Translate to Malayalam
    try:
        malayalam_translation = translator.translate(english_explanation, dest='ml').text
    except Exception as e:
        print(f"Translation error: {e}")
        malayalam_translation = "Translation not available"
    
    return {
        "trainId": train_id,
        "english": english_explanation,
        "malayalam": malayalam_translation,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

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
    
    # Handle timezone-aware comparison
    if cert_date.tzinfo:
        return cert_date < datetime.now(cert_date.tzinfo)
    else:
        # Assume UTC if no timezone info
        return cert_date < datetime.utcnow()

def generate_muttom_bays():
    """
    Generate bays according to the specific track structure:
    Tracks 1-3: Inspection Bay (IBL) - 2 positions each
    Tracks 4-5: Cleaning Bay - 2 positions each
    Tracks 6-13: Revenue Service - 2 positions each
    """
    bays = []
    
    # Tracks 1-3: Inspection Bay (IBL) - 2 positions each
    for track in range(1, 4):
        for pos in [1, 2]:
            bays.append({
                'track': track,
                'position': pos,
                'type': 'inspection',
                'name': f'Inspection Bay {track} Pos {pos}'
            })
    
    # Tracks 4-5: Cleaning Bay - 2 positions each
    for track in range(4, 6):
        for pos in [1, 2]:
            bays.append({
                'track': track,
                'position': pos,
                'type': 'cleaning',
                'name': f'Cleaning Bay {track-3} Pos {pos}'
            })
    
    # Tracks 6-13: Revenue Service - 2 positions each
    for track in range(6, 14):
        for pos in [1, 2]:
            bays.append({
                'track': track,
                'position': pos,
                'type': 'revenue_primary' if track <= 9 else 'revenue_backup',
                'name': f'Revenue Track {track} Pos {pos}'
            })
    
    return bays

def determine_maintenance_needs(train_data):
    """
    Determine if maintenance is needed based on job card score.
    Returns: True if maintenance needed, False otherwise
    """
    job_cards = train_data.get('jobCards', {})
    all_jobs = job_cards.get('all', [])
    
    if not all_jobs:
        return False
    
    # Count job cards by priority
    critical_count = sum(1 for job in all_jobs if job.get('priority') == 'Critical')
    high_count = sum(1 for job in all_jobs if job.get('priority') == 'High')
    medium_count = sum(1 for job in all_jobs if job.get('priority') == 'Medium')
    
    # Determine if maintenance is needed
    if critical_count > 0 or high_count > 0 or medium_count >= 2:
        return True
    else:
        return False

def assign_bays_with_lanes(depot_results, bays_per_depot, original_dataset):
    """
    Dynamic rule-based flow for assigning tasks as trains arrive.
    Returns the same format as compute_scores() but with added bay and task information.
    """
    for depot_id, data in depot_results.items():
        bays = bays_per_depot.get(depot_id, [])
        trains = data.get('trains', [])

        # Keep the original ranking order (don't re-sort by arrival time)
        # The trains are already ranked by score from compute_scores()
        
        used_bays = set()
        
        for train in trains:
            train_id = train.get('trainId')
            # Get original train data
            original_train = next((t for t in original_dataset if t['id'] == train_id), None)
            print("Processing Train ID:", train_id, "Original Train Data:", original_train, "train data:", train)
            if not original_train:
                continue
                
            service_status = original_train.get('serviceStatus', 'unknown')
            
            # Determine train needs from ORIGINAL data
            needs_cleaning = original_train.get('cleaningSlot', False)
            needs_maintenance = determine_maintenance_needs(original_train)
            
            score=train.get('totalScore', 0)
            # Check for violations that require maintenance
            has_fitness_violations = any(is_expired(cert) for cert in original_train.get('certificates', {}).values())
            has_crew_violations = (not original_train.get('crew', {}).get('assigned', False) or 
                                 is_expired(original_train.get('crew', {}).get('validUntil', '')))
            job_cards = original_train.get('jobCards', {}).get('all', [])
            has_critical_jobs = any(job.get('priority') == 'Critical' for job in job_cards)
            
            # Update maintenance needs based on violations
            needs_maintenance = needs_maintenance or has_fitness_violations or has_crew_violations or has_critical_jobs
            
            bay_found = False
            assigned_bay = None
            task_flow = []

            print("service_status:", service_status, "score:", score)
            
            # Special handling for outOfService trains
            if service_status == 'outOfService' or score==0:
                print("Out of service or zero score train:", train_id)
                
                # Try backside tracks (10-13), position 2 first
                for bay in bays:
                    bay_id = f"{bay['track']}_{bay['position']}"
                    if (bay['track'] >= 10 and bay['position'] == 2 and bay_id not in used_bays):
                        assigned_bay = bay
                        task_flow = ['out_of_service_stabling']
                        used_bays.add(bay_id)
                        bay_found = True
                        break
                
                # If no backside pos 2, try any revenue track
                if not bay_found:
                    for bay in bays:
                        bay_id = f"{bay['track']}_{bay['position']}"
                        if (bay['type'] in ['revenue_primary', 'revenue_backup'] and bay_id not in used_bays):
                            assigned_bay = bay
                            task_flow = ['out_of_service_stabling']
                            used_bays.add(bay_id)
                            bay_found = True
                            break
                
                # If still no bay, mark as no bay available
                if not bay_found:
                    task_flow = ['no_bays_available']
            
            # For active trains, assign based on needs
            elif service_status == 'inService' and score>0 and needs_cleaning:
                # Try cleaning bays first (Tracks 4-5)
                for bay in bays:
                    bay_id = f"{bay['track']}_{bay['position']}"
                    if (bay['type'] == 'cleaning' and bay_id not in used_bays):
                        assigned_bay = bay
                        task_flow = ['cleaning']
                        used_bays.add(bay_id)
                        bay_found = True
                        break
                
                # If no cleaning bay and also needs maintenance, try inspection bay
                if not bay_found and needs_maintenance:
                    for bay in bays:
                        bay_id = f"{bay['track']}_{bay['position']}"
                        if (bay['type'] == 'inspection' and bay_id not in used_bays):
                            assigned_bay = bay
                            task_flow = ['maintenance_and_cleaning']
                            used_bays.add(bay_id)
                            bay_found = True
                            break
                
                # If only cleaning needed, try nearby revenue tracks (6-13)
                if not bay_found:
                    for bay in bays:
                        bay_id = f"{bay['track']}_{bay['position']}"
                        if (bay['track'] in range(6, 14) and bay_id not in used_bays):
                            assigned_bay = bay
                            task_flow = ['stabling_near_cleaning']
                            used_bays.add(bay_id)
                            bay_found = True
                            break
            
            # If no cleaning needed, check maintenance only
            elif service_status == 'inService' and score>0 and needs_maintenance:
                # Try inspection bays (Tracks 1-3)
                for bay in bays:
                    bay_id = f"{bay['track']}_{bay['position']}"
                    if (bay['type'] == 'inspection' and bay_id not in used_bays):
                        assigned_bay = bay
                        task_flow = ['maintenance']
                        used_bays.add(bay_id)
                        bay_found = True
                        break
            
            # If still no bay, assign to revenue service
            if not bay_found:
                # Try revenue tracks (6-13)
                for bay in bays:
                    bay_id = f"{bay['track']}_{bay['position']}"
                    if (bay['type'] in ['revenue_primary', 'revenue_backup'] and bay_id not in used_bays):
                        assigned_bay = bay
                        task_flow = ['stabling']
                        used_bays.add(bay_id)
                        bay_found = True
                        break
            
            # Emergency fallback - any available bay
            if not bay_found:
                for bay in bays:
                    bay_id = f"{bay['track']}_{bay['position']}"
                    if bay_id not in used_bays:
                        # Set appropriate task based on bay type
                        if bay['type'] == 'cleaning' and needs_cleaning and score>0:
                            task_flow = ['cleaning']
                        elif bay['type'] == 'inspection' and needs_maintenance and score>0:
                            task_flow = ['maintenance']
                        elif score>0:
                            task_flow = ['stabling']
                        
                        assigned_bay = bay
                        used_bays.add(bay_id)
                        bay_found = True
                        break
            
            # If absolutely no bay available
            if not bay_found:
                task_flow = ['no_bays_available']
            
            # Update the train data with bay and task information
            train['assignedBay'] = assigned_bay
            train['taskFlow'] = task_flow
            duration = ('15-30 minutes' if 'cleaning' in task_flow else 
                       '15-60 minutes' if 'maintenance' in task_flow else 
                       'overnight' if 'out_of_service_stabling' in task_flow else 
                       '30-45 minutes' if 'stabling_near_cleaning' in task_flow else 
                       'ready_to_go' if 'stabling' in task_flow else
                       '60-90 minutes' if 'maintenance_and_cleaning' in task_flow else
                       'unknown')
            train['taskDuration'] = duration

        # Don't replace the trains list - it's already ranked by score
        # depot_results[depot_id]['trains'] = trains  # REMOVE THIS LINE

    return depot_results

                        # Assign the updated train dict back to the trains list
                        # This is only needed if train is not a reference, but a copy
                        # If trains is a list of dicts, this will update in place
                        # If not, update the trains list explicitly
                        # (No action needed if trains is a list of dict references)
def compute_scores(trains):
    depots = {}
    for t in trains:
        depots.setdefault(t['depotId'], []).append(t)
        print(" Depot ID: ", t['depotId'], "Train ID: ", t['id'])

    depot_results = {}

    for depot_id, depot_trains in depots.items():
        # Normalize mileage within depot
        odometers = [t['mileage']['odometer'] for t in depot_trains]
        min_odo, max_odo = min(odometers), max(odometers)
        scored_trains = []
        daily_required=0

        for train in depot_trains:
            violations = []
            eligible = True
            rs = {
                'fitness': 100,
                'jobCards': 100,
                'branding': 0,
                'mileage': 0,
                'crew': 100
            }

            # --- Fitness certificate check (HARD constraint) ---
            for c in train['certificates'].values():
                if is_expired(c):
                    rs['fitness'] = 0
                    violations.append(f"Fitness Certificate expired: {c}")
                    eligible = False

            # --- Crew check (HARD constraint) ---
            if not train['crew']['assigned'] or is_expired(train['crew']['validUntil']):
                rs['crew'] = 0
                violations.append("No valid crew assigned")
                eligible = False

            # --- Job cards ---
            jc_all = train['jobCards']['all']
            num_critical = sum(1 for j in jc_all if j['priority'] == "Critical")

            if num_critical > 0:
                rs['jobCards'] = 0
                violations.append(f"{num_critical} Critical job card present")
                eligible = False
            elif jc_all:
                num_high   = sum(1 for j in jc_all if j['priority'] == "High")
                num_medium = sum(1 for j in jc_all if j['priority'] == "Medium")
                num_low    = sum(1 for j in jc_all if j['priority'] == "Low")
                total_jc   = len(jc_all)
                # Weighted score
                score = 100 - ((num_high*0.7 + num_medium*0.4 + num_low*0.1) / total_jc * 100)
                rs['jobCards'] = max(0, round(score))

            # --- Branding score ---
            branding_data = train.get('branding', {})
            branding_status = branding_data.get('status', False)
            print("Branding data: ", branding_data)
            daily_required = 0
            
            if not branding_status:
                # No branding obligations
                rs['branding'] = 0
                daily_required = 0
            else:
                # Has branding obligations - calculate urgency
                hrs_left = branding_data.get('hoursRemaining', 0)
                end_date_str = branding_data.get('endDate', None)
                days_left= 0
                if end_date_str and end_date_str != "None":
                    try:
                        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                        days_left = (end_date - datetime.today()).days
                        # print("Days left: ", days_left)
                    except ValueError:
                        # If format is invalid, treat as expired
                        days_left = 0

                if days_left > 0:
                    print("Hrs left: ", hrs_left)
                    print("Days left: ", days_left)
                    daily_required = hrs_left / days_left
                    print("Daily required: ", daily_required)
                else:
                    daily_required = float('inf')  # already expired

                EXPOSURE_CAPACITY = 16.5  # kochi metro runs from 6am to 10:30pm
                score = 0
                if daily_required > EXPOSURE_CAPACITY:
                    score = -1  # Cannot meet goal
                else:
                    # Normalize urgency: higher daily_required → higher score, capped at 100
                    score = max(0, min(100, (daily_required / EXPOSURE_CAPACITY) * 100))

                rs['branding'] = score

            # --- Mileage score ---
            rs['mileage'] = 100 - ((train['mileage']['odometer'] - min_odo)/(max_odo - min_odo)*100) if max_odo != min_odo else 100

            # --- Calculate total score ---
            total_score = 0
            if eligible:
                weights = {'jobCards': 50, 'branding': 30, 'mileage': 20}
                total_score = sum(rs[k] * weights[k] / 100 for k in weights)

            scored_trains.append({
                'train': train,
                'eligible': eligible,
                'totalScore': total_score,
                'rs': rs,
                'violations': violations,
                'daily_required': daily_required
            })

        # --- Build output ---
        depot_results[depot_id] = {'trains': []}
        for entry in scored_trains:
            train = entry['train']
            rs = entry['rs']
            reason = []

            if not entry['eligible']:
                for v in entry['violations']:
                    reason.append(f"{v} -> ineligible")
            else:
                if rs['jobCards'] < 100:
                    reason.append(f"Job card score: {rs['jobCards']}/100 (no criticals)")
                if rs['branding'] == -1:
                    reason.append(f"Branding criterion cannot be met for this train. Requires {entry.get('daily_required', 0)} hrs per day but only {EXPOSURE_CAPACITY} hrs are permissible.")
                elif rs['branding'] == 0:
                    reason.append(f"Branding score: {rs['branding']}/100. No branding contractual obligations.")
                elif rs['branding'] < 100:
                    reason.append(f"Branding score: {rs['branding']}/100. Needs {entry.get('daily_required', 0)} hrs per day.")
                if rs['mileage'] < 100:
                    reason.append(f"Mileage score: {rs['mileage']}/100")

            # Include override if present
            ov = train.get('override', {})
            if ov.get('flag'):
                reason.append(f"Override applied: by {ov.get('by')}, category {ov.get('category')}, reason {ov.get('reason')}")

            depot_results[depot_id]['trains'].append({
                'trainId': train['id'],
                'totalScore': round(entry['totalScore']),
                'eligible': entry['eligible'],
                'relativeScores': {k: round(v) for k, v in rs.items()},
                'reason': reason,
                'violations': entry['violations']
            })

        depot_results[depot_id]['trains'].sort(key=lambda x: x['totalScore'], reverse=True)

    return depot_results

def process_train_dataset(train_dataset):
    # Run optimizer
    depot_ranked = compute_scores(train_dataset)

    bays_per_depot = {
        "Muttom": generate_muttom_bays(),
        # Add more depots if needed
        #"Palarivottam": generate_palarivottam_bays(),
    }
    # print("Bays per depot:", bays_per_depot)
    # print("Depot ranked before bay assignment:", depot_ranked)
    # print("Dataset: 0", train_dataset)
    depot_ranked = assign_bays_with_lanes(depot_ranked, bays_per_depot, train_dataset)
    # print("Final depot ranked data:", depot_ranked)

    # Print all fields in depot ranked
    for depot_id, data in depot_ranked.items():
        print(f"Depot: {depot_id}")
        for t in data['trains']:
            print(t)
        print()
    

    # Add explanations
    # for depot_id, depot_data in depot_ranked.items():
    #     for train in depot_data['trains']:
    #         train['explanation'] = generate_explanation(train, train_dataset)

    for depot_id, depot_data in depot_ranked.items():
        for train in depot_data['trains']:
            try:
                explanation_result = generate_explanation_sync(train, train_dataset)
                print(f"    English: {explanation_result.get('english', 'N/A')}")
                print(f"    Malayalam: {explanation_result.get('malayalam', 'N/A')}")
                print(f"    Timestamp: {explanation_result.get('timestamp', 'N/A')}")
                train['explanation'] = f"{explanation_result.get('english', 'N/A')}\n{explanation_result.get('malayalam', 'N/A')}"
            except Exception as e:
                print(f"    Explanation Error: {e}")
                print("explanation result:" , explanation_result)
            print()

    return depot_ranked
