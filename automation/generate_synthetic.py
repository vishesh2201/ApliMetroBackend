import os, csv, random, datetime

data_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_dir, exist_ok=True)
filename = os.path.join(data_dir, f'synthetic_{datetime.date.today()}.csv')

trains = [f'KM{str(i+1).zfill(3)}' for i in range(25)]

with open(filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # Header row
    writer.writerow([
        'id', 'depotId',
        'cert_stock', 'cert_signal', 'cert_telecom',
        'jobCards_count', 'jobCards_list',
        'odometer', 'lastService',
        'branding_status', 'branding_hoursRemaining',
        'branding_totalHours', 'branding_endDate',
        'cleaningSlot',
        'crew_assigned', 'crew_driverId', 'crew_validUntil',
        'override_flag', 'override_category', 'override_reason', 'override_by',
        'serviceStatus', 'arrivalTime'
    ])

    today = datetime.date.today()
    for idx, t in enumerate(trains):
        depot = "Muttom"
        # --- Certificates ---
        if idx < 6:
            cert_stock = today + datetime.timedelta(days=random.randint(30, 365))
            cert_signal = today + datetime.timedelta(days=random.randint(30, 365))
            cert_telecom = today + datetime.timedelta(days=random.randint(30, 365))
        else:
            cert_stock = today + datetime.timedelta(days=random.randint(-500, 800))
            cert_signal = today + datetime.timedelta(days=random.randint(-500, 800))
            cert_telecom = today + datetime.timedelta(days=random.randint(-500, 800))
        # --- Job cards ---
        if idx < 6:
            job_count = random.randint(0, 2)
            jobs = []
        else:
            job_count = random.randint(0, 6)
            priorities = ["Low", "Medium", "High", "Critical"]
            job_titles = [
                "Brake pad inspection", "Seat repairs", "Passenger display malfunction",
                "HVAC failure", "Lighting faults", "Pantograph wear",
                "Battery replacement", "Door sensor fault", "CCTV fault",
                "Traction motor failure", "Emergency braking system fault"
            ]
            jobs = []
            for _ in range(job_count):
                jobs.append({
                    "title": random.choice(job_titles),
                    "priority": random.choice(priorities)
                })
        job_list = str(jobs) if jobs else "[]"
        # --- Mileage ---
        odo = random.randint(120000, 155000)
        last_service = today - datetime.timedelta(days=random.randint(200, 800))
        # --- Branding ---
        brand_status = random.choice([True, False])
        bh_remaining = random.randint(10, 50) if (brand_status and idx < 6) else random.randint(0, 20)
        bh_total = bh_remaining + random.randint(40, 200) if brand_status else 0
        bh_end = today + datetime.timedelta(days=random.randint(30, 365)) if brand_status else "None"
        # --- Cleaning ---
        cleaning = True if idx < 6 else random.choice([True, False])
        # --- Crew ---
        if idx < 6:
            crew_assigned = True
            crew_driver = f"CR{random.randint(1,30):03d}"
            crew_valid = (today + datetime.timedelta(days=random.randint(90, 365))).strftime("%d/%m/%y %H%M")
        else:
            crew_assigned = random.choice([True, False])
            crew_driver = f"CR{random.randint(1,30):03d}" if crew_assigned else None
            crew_valid = (today + datetime.timedelta(days=random.randint(30, 365))).strftime("%d/%m/%y %H%M") if crew_assigned else None
        # --- Overrides ---
        override_flag = random.choice([False, False, True])
        override_cats = ["Maintenance", "Safety", "Operational"]
        override_category = random.choice(override_cats) if override_flag else "None"
        override_reason = {
            "Maintenance": "Pre-Emptive Maintenance",
            "Safety": "Emergency Recall",
            "Operational": "Special Event Demand"
        }.get(override_category, "None") if override_flag else "None"
        override_by = random.choice(["Workshop Staff", "Control Room", "Operations Manager"]) if override_flag else "None"
        # --- Service status ---
        statuses = ["inService", "standby", "maintenance", "outOfService"]
        service_status = random.choice(statuses)
        arrival = f"{random.randint(10,11)}:{random.randint(10,59)} PM" if service_status == "inService" else "None"
        # --- Write row ---
        writer.writerow([
            t, depot,
            cert_stock.isoformat(), cert_signal.isoformat(), cert_telecom.isoformat(),
            job_count, job_list,
            odo, last_service.isoformat(),
            brand_status, bh_remaining, bh_total, bh_end if isinstance(bh_end, str) else bh_end.isoformat(),
            cleaning,
            crew_assigned, crew_driver, crew_valid,
            override_flag, override_category, override_reason, override_by,
            service_status, arrival
        ])

print(f"Synthetic CSV generated: {filename}")