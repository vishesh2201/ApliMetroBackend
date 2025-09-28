import csv, json, datetime, os

data_dir = os.path.join(os.path.dirname(__file__), 'data')
filename = os.path.join(data_dir, f'synthetic_{datetime.date.today()}.csv')

trains = []
today = datetime.date.today()
with open(filename, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        reasons = []
        category = "Standby"  # default

        # ---- FITNESS CHECK ----
        certs = [row['cert_stock'], row['cert_signal'], row['cert_telecom']]
        expired = [c for c in certs if c and datetime.date.fromisoformat(c) < today]
        if expired:
            category = "IBL"
            reasons.append("Expired fitness certificates")

        # ---- JOB CARD CHECK ----
        job_count = int(row['jobCards_count'])
        if job_count > 0 and "Critical" in row['jobCards_list']:
            category = "IBL"
            reasons.append("Critical job card present")

        # ---- CREW CHECK ----
        if row['crew_assigned'] == "False" or not row['crew_validUntil']:
            category = "IBL"
            reasons.append("No valid crew assigned")

        # ---- BRANDING & CLEANING ----
        branding_ok = row['branding_status'] == "True" and int(row['branding_hoursRemaining']) > 0
        cleaning_ok = row['cleaningSlot'] == "True"

        if category != "IBL":
            if branding_ok or cleaning_ok:
                category = "Revenue Service"
                reasons.append(f"Branding hrs left {row['branding_hoursRemaining']}, Cleaning {row['cleaningSlot']}")
            else:
                category = "Standby"
                reasons.append("Minor pending tasks")

        # ---- OVERRIDES ----
        if row['override_flag'] == "True":
            category = "IBL"
            reasons.append(f"Override: {row['override_category']} - {row['override_reason']} by {row['override_by']}")

        # ---- SCORE ----
        score = 0
        if branding_ok:
            bh = int(row['branding_hoursRemaining'])
            bt = int(row['branding_totalHours']) if row['branding_totalHours'] != "0" else 72
            score += round(bh / bt * 100)
        if cleaning_ok:
            score += 10
        try:
            odo = int(row['odometer'])
        except:
            odo = 0
        score += max(0, 1000000 - odo) // 10000

        trains.append({
            'train_id': row['id'],
            'category': category,
            'reasons': reasons,
            'branding_hours_remaining': row['branding_hoursRemaining'],
            'cleaning_slot': row['cleaningSlot'],
            'odometer_km': row['odometer'],
            'score': score
        })

# ---- SORT ----
order = {"Revenue Service": 0, "Standby": 1, "IBL": 2}
trains_sorted = sorted(trains, key=lambda x: (order[x['category']], -x['score'], int(x['odometer_km'])))

# ---- WRAP FOR N8N ----
output = {"trains": trains_sorted}
print(json.dumps(output, indent=2))