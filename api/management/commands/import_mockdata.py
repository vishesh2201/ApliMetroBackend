from django.core.management.base import BaseCommand
from api.models import Train, Certificates, Branding, JobCard, Crew, Override, InductionList
from datetime import datetime


mock_trains = [
  {
    "id": "KM001",
    "depotId": "Muttom",
    "certificates": { "stock": "2026-01-01T10:00:00", "signal": "2026-02-01T12:00:00", "telecom": "2026-03-01T08:00:00" },
    "jobCards": { "count": 3, "all": [ { "title": "Brake pad inspection", "priority": "High" }, { "title": "Seat repairs", "priority": "Low" }, { "title": "Passenger display malfunction", "priority": "Medium" } ] },
    "mileage": { "odometer": 132450, "lastService": "2024-01-15" },
    "branding": {
      "status": True,
      "hoursRemaining": 24,
      "totalHours": 130,
      "endDate": "2025-10-11"
    },
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR001", "validUntil": "2026-01-01T10:00:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:25 PM"
  },
  {
    "id": "KM002",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-09-25T22:00:00", "signal": "2025-11-25T23:59:00", "telecom": "2025-11-25T23:59:00" },
    "jobCards": { "count": 0, "all": [] },
    "mileage": { "odometer": 140120, "lastService": "2024-01-12" },
    "branding": { "status": False, "hoursRemaining": 0 , "totalHours": 0, "endDate": "None"},
    "cleaningSlot": False,
    "crew": { "assigned": False, "driverId": "None", "validUntil": "None" },
    "override": { "flag": True, "category": "inService", "reason": "Pre-Emptive inService", "by": "Workshop Staff" },
    "serviceStatus": "inService",
    "arrivalTime": "None"
  },
  {
    "id": "KM003",
    "depotId": "Muttom",
    "certificates": { "stock": "2026-05-10T18:00:00", "signal": "2026-12-25T23:59:00", "telecom": "2026-11-25T20:00:00" },
    "jobCards": { "count": 2, "all": [ { "title": "HVAC partial failure", "priority": "Medium" }, { "title": "Lighting faults", "priority": "Low" } ] },
    "mileage": { "odometer": 125500, "lastService": "2024-01-18" },
    "branding": {
      "status": True,
      "hoursRemaining": 12,
      "totalHours": 110,
      "endDate": "2025-10-02"
    },
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR003", "validUntil": "2025-11-10T18:00:00"},
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:35 PM"
  },
  {
    "id": "KM004",
    "depotId": "Muttom",
    "certificates": { "stock": "2026-11-25T23:59:00", "signal": "2026-11-25T23:59:00", "telecom": "2026-12-25T23:59:00" },
    "jobCards": { "count": 1, "all": [ { "title": "Minor cosmetic touch-up", "priority": "Low" } ] },
    "mileage": { "odometer": 138000, "lastService": "2024-01-20" },
    "branding": {
      "status": True,
      "hoursRemaining": 15,
      "totalHours": 90,
      "endDate": "2025-10-01"
    },
    "cleaningSlot": False,
    "crew": { "assigned": True, "driverId": "CR004", "validUntil": "2026-12-25T23:59:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:20 PM"
  },
  {
    "id": "KM005",
    "depotId": "Muttom",
    "certificates": { "stock": "2026-10-25T18:00:00", "signal": "2026-12-25T23:59:00", "telecom": "2026-11-25T20:00:00" },
    "jobCards": { "count": 3, "all": [ { "title": "Battery replacement", "priority": "High" }, { "title": "Pantograph wear", "priority": "High" }, { "title": "Door sensor fault", "priority": "Medium" } ] },
    "mileage": { "odometer": 149000, "lastService": "2024-01-12" },
    "branding": { "status": False, "hoursRemaining": 0 , "totalHours": 0, "endDate": "None"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR005", "validUntil": "2026-12-25T23:59:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:30 PM"
  },
  {
    "id": "KM006",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-11-25T23:59:00", "signal": "2025-11-25T23:59:00", "telecom": "2025-11-25T23:59:00" },
    "jobCards": { "count": 1, "all": [ { "title": "Seat repairs / broken handles", "priority": "Low" } ] },
    "mileage": { "odometer": 135500, "lastService": "2024-01-16" },
    "branding": {
      "status": True,
      "hoursRemaining": 6,
      "totalHours": 80,
      "endDate": "2025-09-28"
    },
    "cleaningSlot": False,
    "crew": { "assigned": True, "driverId": "CR006", "validUntil": "2026-12-25T23:59:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "None"
  },
  {
    "id": "KM007",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-09-25T23:59:00", "signal": "2025-11-25T23:59:00", "telecom": "2025-11-25T23:59:00" },
    "jobCards": { "count": 2, "all": [ { "title": "Lighting failures in cars", "priority": "Medium" }, { "title": "Passenger display malfunction", "priority": "Medium" } ] },
    "mileage": { "odometer": 147200, "lastService": "2024-01-14" },
    "branding": {
      "status": True,
      "hoursRemaining": 4,
      "totalHours": 60,
      "endDate": "2025-09-28"
    },
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR007", "validUntil": "2025-012-25T23:59:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:40 PM"
  },
  {
    "id": "KM008",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-12-25T23:59:00", "signal": "2025-12-25T23:59:00", "telecom": "2025-12-25T23:59:00" },
    "jobCards": { "count": 0, "all": [] },
    "mileage": { "odometer": 140100, "lastService": "2024-01-19" },
    "branding": { "status": False, "hoursRemaining": 0 , "totalHours": 0, "endDate": "None"},
    "cleaningSlot": False,
    "crew": { "assigned": True, "driverId": "CR008", "validUntil": "2025-12-25T08:00:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "None"
  },
  {
    "id": "KM009",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-11-25T23:59:00", "signal": "2025-11-25T23:59:00", "telecom": "2025-09-25T23:59:00" },
    "jobCards": { "count": 4, "all": [ { "title": "Bogie abnormal noise", "priority": "High" }, { "title": "Pantograph wear", "priority": "High" }, { "title": "CCTV failure", "priority": "High" }, { "title": "Battery near EOL", "priority": "High" } ] },
    "mileage": { "odometer": 151600, "lastService": "2024-01-11" },
    "branding": { "status": True, "hoursRemaining": 20 , "totalHours": 20, "endDate": "2025-12-20"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR009", "validUntil": "2025-10-25T06:00:00"  },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:15 PM"
  },
  {
    "id": "KM010",
    "depotId": "Muttom",
    "certificates": { "stock": "2022-11-25T23:59:00", "signal": "2022-11-25T23:59:00", "telecom": "2022-11-25T23:59:00" },
    "jobCards": { "count": 1, "all": [ { "title": "Minor branding wrap tear", "priority": "Low" } ] },
    "mileage": { "odometer": 142800, "lastService": "2024-01-17" },
    "branding": { "status": True, "hoursRemaining": 10 , "totalHours": 80, "endDate": "2026-02-02"},
    "cleaningSlot": False,
    "crew": { "assigned": False, "driverId": "None", "validUntil": "None" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "None"
  },
  {
    "id": "KM011",
    "depotId": "Muttom",
    "certificates": { "stock": "2015-09-25T21:00:00", "signal": "2022-11-25T23:59:00", "telecom": "2022-11-25T23:59:00" },
    "jobCards": { "count": 6, "all": [ { "title": "Brake system fault", "priority": "Critical" }, { "title": "Traction motor failure", "priority": "Critical" }, { "title": "Signalling ATP fault", "priority": "Critical" }, { "title": "Door interlock failure", "priority": "High" }, { "title": "Emergency braking system fault", "priority": "Critical" }, { "title": "Fire suppression fault", "priority": "Critical" } ] },
    "mileage": { "odometer": 154200, "lastService": "2024-01-08" },
    "branding": { "status": False, "hoursRemaining": 0 , "totalHours": 0, "endDate": "None"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR011", "validUntil": "2026-09-30T23:59:00" },
    "override": { "flag": True, "category": "Safety", "reason": "Emergency Recall", "by": "Control Room" },
    "serviceStatus": "outOfService",
    "arrivalTime": "None"
  },
  {
    "id": "KM012",
    "depotId": "Muttom",
    "certificates": { "stock": "2022-11-25T23:59:00", "signal": "2022-12-25T23:59:00", "telecom": "2022-12-25T08:00:00" },
    "jobCards": { "count": 0, "all": [] },
    "mileage": { "odometer": 137500, "lastService": "2024-01-21" },
    "branding": { "status": True, "hoursRemaining": 18 , "totalHours": 40, "endDate": "2025-11-01"},
    "cleaningSlot": False,
    "crew": { "assigned": True, "driverId": "CR012", "validUntil": "2026-12-01T23:59:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:45 PM"
  },
  {
    "id": "KM013",
    "depotId": "Muttom",
    "certificates": { "stock": "2022-11-25T18:00:00", "signal": "2022-12-25T12:00:00", "telecom": "2022-11-25T22:00:00" },
    "jobCards": { "count": 2, "all": [ { "title": "HVAC service", "priority": "Medium" }, { "title": "Door sensor repair", "priority": "High" } ] },
    "mileage": { "odometer": 131200, "lastService": "2024-01-18" },
    "branding": { "status": False, "hoursRemaining": 0 , "totalHours": 0, "endDate": "None"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR013", "validUntil": "2025-12-08T18:00:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:22 PM"
  },
  {
    "id": "KM014",
    "depotId": "Muttom",
    "certificates": { "stock": "2026-05-14T21:00:00", "signal": "2026-05-14T23:59:00", "telecom": "2026-05-14T06:00:00" },
    "jobCards": { "count": 1, "all": [ { "title": "Wheel alignment check", "priority": "High" } ] },
    "mileage": { "odometer": 128900, "lastService": "2024-01-15" },
    "branding": { "status": True, "hoursRemaining": 20 , "totalHours": 200, "endDate": "2025-11-07"},
    "cleaningSlot": False,
    "crew": { "assigned": False, "driverId": "None", "validUntil": "None" },
    "override": { "flag": True, "category": "inService", "reason": "Deferred inService", "by": "Workshop Staff" },
    "serviceStatus": "inService",
    "arrivalTime": "None"
  },
  {
    "id": "KM015",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-11-25T23:59:00", "signal": "2025-11-25T23:59:00", "telecom": "2025-12-25T18:00:00" },
    "jobCards": { "count": 0, "all": [] },
    "mileage": { "odometer": 136400, "lastService": "2024-01-16" },
    "branding": { "status": False, "hoursRemaining": 0 , "totalHours": 0, "endDate": "None"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR015", "validUntil": "2025-11-25T08:00:00"  },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "None"
  },
  {
    "id": "KM016",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-11-25T23:59:00", "signal": "2025-11-25T23:59:00", "telecom": "2025-12-25T23:59:00" },
    "jobCards": { "count": 2, "all": [ { "title": "Brake calibration", "priority": "Medium" }, { "title": "HVAC inService", "priority": "Low" } ] },
    "mileage": { "odometer": 142000, "lastService": "2024-01-19" },
    "branding": { "status": True, "hoursRemaining": 12 , "totalHours": 90, "endDate": "2025-10-30"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR016", "validUntil": "2025-11-25T22:00:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:28 PM"
  },
  {
    "id": "KM017",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-11-25T08:00:00", "signal": "2025-12-25T23:59:00", "telecom": "2025-11-25T22:00:00" },
    "jobCards": { "count": 1, "all": [ { "title": "Door interlock inspection", "priority": "High" } ] },
    "mileage": { "odometer": 150500, "lastService": "2024-01-14" },
    "branding": { "status": False, "hoursRemaining": 0 , "totalHours": 0, "endDate": "None"},
    "cleaningSlot": False,
    "crew": { "assigned": False, "driverId": "None", "validUntil": "None" },
    "override": { "flag": True, "category": "Operational", "reason": "Special Event Demand", "by": "Operations Manager" },
    "serviceStatus": "inService",
    "arrivalTime": "None"
  },
  {
    "id": "KM018",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-11-25T23:59:00", "signal": "2025-11-25T23:59:00", "telecom": "2025-12-25T23:59:00" },
    "jobCards": { "count": 0, "all": [] },
    "mileage": { "odometer": 124800, "lastService": "2024-01-21" },
    "branding": { "status": False, "hoursRemaining": 0 , "totalHours": 0, "endDate": "None"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR018", "validUntil": "2025-10-25T23:59:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "None"
  },
  {
    "id": "KM019",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-11-25T18:00:00", "signal": "2025-11-25T23:59:00", "telecom": "2025-12-25T18:00:00" },
    "jobCards": { "count": 2, "all": [ { "title": "Pantograph inspection", "priority": "High" }, { "title": "Seat repair", "priority": "Low" } ] },
    "mileage": { "odometer": 133500, "lastService": "2024-01-15" },
    "branding": { "status": True, "hoursRemaining": 10 , "totalHours": 100, "endDate": "2025-09-30"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR019", "validUntil": "2025-11-25T23:59:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:33 PM"
  },
  {
    "id": "KM020",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-11-25T23:59:00", "signal": "2025-11-25T23:59:00", "telecom": "2025-11-25T23:59:00" },
    "jobCards": { "count": 1, "all": [ { "title": "Minor electrical fault", "priority": "Low" } ] },
    "mileage": { "odometer": 145000, "lastService": "2024-01-17" },
    "branding": { "status": True, "hoursRemaining": 8 , "totalHours": 50, "endDate": "2025-10-09"},
    "cleaningSlot": False,
    "crew": { "assigned": False, "driverId": "None", "validUntil": "None" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "None"
  },
  {
    "id": "KM021",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-12-25T23:59:00", "signal": "2025-11-25T23:59:00", "telecom": "2025-12-25T23:59:00" },
    "jobCards": { "count": 3, "all": [ { "title": "Brake pad replacement", "priority": "High" }, { "title": "HVAC check", "priority": "Medium" }, { "title": "Lighting repair", "priority": "Low" } ] },
    "mileage": { "odometer": 139000, "lastService": "2024-01-18" },
    "branding": { "status": True, "hoursRemaining": 16 , "totalHours": 150, "endDate": "2026-04-20"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR021", "validUntil":"2025-11-01T23:59:00"},
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:38 PM"
  },
  {
    "id": "KM022",
    "depotId": "Muttom",
    "certificates": { "stock": "2022-11-25T23:59:00", "signal": "2022-11-25T23:59:00", "telecom": "2022-11-25T23:59:00" },
    "jobCards": { "count": 0, "all": [] },
    "mileage": { "odometer": 128500, "lastService": "2024-01-19" },
    "branding": { "status": False, "hoursRemaining": 0 , "totalHours": 0, "endDate": "None"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR022", "validUntil":"2025-11-01T23:59:00"},
    "override": { "flag": True, "category": "Operational", "reason": "Service Pattern Change", "by": "Operations Manager" },
    "serviceStatus": "inService",
    "arrivalTime": "None"
  },
  {
    "id": "KM023",
    "depotId": "Muttom",
    "certificates": { "stock": "2022-11-25T08:00:00", "signal": "2022-12-25T23:59:00", "telecom": "2022-12-25T18:00:00" },
    "jobCards": { "count": 2, "all": [ { "title": "HVAC filter replacement", "priority": "Medium" }, { "title": "Pantograph lubrication", "priority": "High" } ] },
    "mileage": { "odometer": 136200, "lastService": "2024-01-14" },
    "branding": { "status": True, "hoursRemaining": 12 , "totalHours": 20, "endDate": "2026-11-29"},
    "cleaningSlot": False,
    "crew": { "assigned": True, "driverId": "CR023", "validUntil": "2025-12-08T23:59:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:17 PM"
  },
  {
    "id": "KM024",
    "depotId": "Muttom",
    "certificates": { "stock": "2025-01-25T23:59:00", "signal": "2025-01-25T23:59:00", "telecom": "2025-02-25T23:59:00" },
    "jobCards": { "count": 1, "all": [ { "title": "Minor door alignment", "priority": "Low" } ] },
    "mileage": { "odometer": 130400, "lastService": "2024-01-16" },
    "branding": { "status": True, "hoursRemaining": 8 , "totalHours": 180, "endDate": "2026-07-01"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR024", "validUntil": "2025-12-25T23:59:00"},
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None"},
    "serviceStatus": "inService",
    "arrivalTime": "10:42 PM"
  },
  {
    "id": "KM025",
    "depotId": "Muttom",
    "certificates": {
      "stock": "2022-10-25T23:59:00",
      "signal": "2022-11-25T08:00:00",
      "telecom": "2022-12-25T06:00:00"
    },
    "jobCards": {
      "count": 2,
      "all": [
        { "title": "HVAC system check", "priority": "Medium" },
        { "title": "Door interlock inspection", "priority": "Low" }
      ]
    },
    "mileage": { "odometer": 148200, "lastService": "2024-01-10" },
    "branding": { "status": True, "hoursRemaining": 18 , "totalHours": 110, "endDate": "2026-01-22"},
    "cleaningSlot": True,
    "crew": { "assigned": True, "driverId": "CR125", "validUntil": "2025-11-25T23:59:00" },
    "override": { "flag": False, "category": "None", "reason": "None", "by": "None" },
    "serviceStatus": "inService",
    "arrivalTime": "10:19 PM"
  }
]

mock_induction_list = [
    {
        'trainId': 'KM004',
        'score': 95,
        'reason': 'Perfect fitness, optimal mileage, active branding',
        'override': False,
        'violations': [],
    },
    {
        'trainId': 'KM012',
        'score': 92,
        'reason': 'No job cards, recent service, good branding hours',
        'override': False,
        'violations': [],
    },
    {
        'trainId': 'KM006',
        'score': 88,
        'reason': 'Good overall status, minor job card',
        'override': False,
        'violations': ['Branding expires in 6 hours'],
    },
    {
        'trainId': 'KM010',
        'score': 85,
        'reason': 'Stable performance, adequate branding',
        'override': False,
        'violations': [],
    },
    {
        'trainId': 'KM001',
        'score': 78,
        'reason': 'Telecom certificate expires today',
        'override': False,
        'violations': ['Telecom certificate expires today'],
    },
    {
        'trainId': 'KM003',
        'score': 75,
        'reason': 'Signal certificate expires today',
        'override': False,
        'violations': ['Signal certificate expires today'],
    },
    {
        'trainId': 'KM007',
        'score': 72,
        'reason': 'Stock certificate expires today, short branding',
        'override': False,
        'violations': ['Stock certificate expires today', 'Branding expires in 4 hours'],
    },
    {
        'trainId': 'KM009',
        'score': 65,
        'reason': 'High severity job cards, telecom expires',
        'override': False,
        'violations': ['High severity job cards', 'Telecom certificate expires today'],
    },

    # === Extended induction list for new trains ===
    {
        'trainId': 'KM013',
        'score': 96,
        'reason': 'Excellent readiness, clean mileage distribution',
        'override': False,
        'violations': [],
    },
    {
        'trainId': 'KM014',
        'score': 73,
        'reason': 'Medium job cards, signal certificate expires',
        'override': False,
        'violations': ['Signal certificate expires today'],
    },
    {
        'trainId': 'KM016',
        'score': 89,
        'reason': 'Minor issues, solid readiness',
        'override': False,
        'violations': [],
    },
    {
        'trainId': 'KM017',
        'score': 68,
        'reason': 'High severity issues + telecom expiry',
        'override': False,
        'violations': ['Telecom certificate expires today', 'High severity job cards'],
    },
    {
        'trainId': 'KM018',
        'score': 94,
        'reason': 'Freshly serviced, no violations',
        'override': False,
        'violations': [],
    },
    {
        'trainId': 'KM019',
        'score': 70,
        'reason': 'Stock expires today, minor issue',
        'override': False,
        'violations': ['Stock certificate expires today'],
    },
    {
        'trainId': 'KM020',
        'score': 66,
        'reason': 'High severity job cards, limited branding',
        'override': False,
        'violations': ['High severity job cards'],
    },
    {
        'trainId': 'KM021',
        'score': 93,
        'reason': 'Optimal mileage, good branding availability',
        'override': False,
        'violations': [],
    },
    {
        'trainId': 'KM023',
        'score': 86,
        'reason': 'Low severity cosmetic job card',
        'override': False,
        'violations': [],
    },
    {
        'trainId': 'KM024',
        'score': 71,
        'reason': 'Medium job cards, signal expiry',
        'override': False,
        'violations': ['Signal certificate expires today'],
    },
    {
        'trainId': 'KM025',
        'score': 97,
        'reason': 'Ideal induction candidate',
        'override': False,
        'violations': [],
    },
]

class Command(BaseCommand):
  help = 'Import mock train data into the database.'

  def handle(self, *args, **options):
    self.stdout.write(self.style.WARNING('Starting mock data import...'))
    # Delete all existing data
    JobCard.objects.all().delete()
    Train.objects.all().delete()
    Certificates.objects.all().delete()
    Branding.objects.all().delete()
    Crew.objects.all().delete()
    Override.objects.all().delete()
    InductionList.objects.all().delete()

    def parse_cert_date(date_str):
      if not date_str:
        self.stdout.write(f"parse_cert_date: got empty string")
        return None
      try:
        date_str = date_str.strip()
        self.stdout.write(f"parse_cert_date: parsing '{date_str}'")
        # Try ISO 8601 first
        dt = datetime.fromisoformat(date_str)
        self.stdout.write(f"parse_cert_date: parsed datetime {dt}")
        return dt
      except Exception as e_iso:
        self.stdout.write(f"parse_cert_date: ISO parse failed for '{date_str}' with error: {e_iso}")
        # Fallback to old logic
        try:
          date_part, time_part = date_str.split()
          if '/' in date_part:
            yy, mm, dd = map(int, date_part.split('/'))
          elif '-' in date_part:
            yy, mm, dd = map(int, date_part.split('-'))
          else:
            raise ValueError('Unknown date separator')
          hh = int(time_part[:2])
          mi = int(time_part[2:])
          year = 2000 + yy if yy < 100 else yy
          dt = datetime(year, mm, dd, hh, mi)
          self.stdout.write(f"parse_cert_date: parsed datetime {dt}")
          return dt
        except Exception as e_old:
          self.stdout.write(f"parse_cert_date: failed to parse '{date_str}' with error: {e_old}")
          return None


    for train in mock_trains:
      self.stdout.write(self.style.NOTICE(f"Processing train {train['id']}"))
      cert = train['certificates']
      self.stdout.write(f"  stock raw: {cert.get('stock')}")
      self.stdout.write(f"  signal raw: {cert.get('signal')}")
      self.stdout.write(f"  telecom raw: {cert.get('telecom')}")
      stock_dt = parse_cert_date(cert.get('stock'))
      signal_dt = parse_cert_date(cert.get('signal'))
      telecom_dt = parse_cert_date(cert.get('telecom'))
      self.stdout.write(f"  stock parsed: {stock_dt}")
      self.stdout.write(f"  signal parsed: {signal_dt}")
      self.stdout.write(f"  telecom parsed: {telecom_dt}")
      certificates = Certificates.objects.create(
        stock=stock_dt,
        signal=signal_dt,
        telecom=telecom_dt,
      )

      branding = Branding.objects.create(
        status=train['branding']['status'],
        hours_remaining=train['branding']['hoursRemaining'],
        total_hours=train['branding']['totalHours'],
      )

      crew_data = train['crew']
      crew = Crew.objects.create(
        assigned=crew_data['assigned'],
        driver_id=crew_data.get('driverId'),
        valid_until=parse_cert_date(crew_data.get('validUntil')) if crew_data.get('validUntil') else None,
      )

      override_data = train['override']
      override = Override.objects.create(
        flag=override_data['flag'],
        category=override_data['category'],
        reason=override_data['reason'],
        by=override_data['by'],
      )

      t = Train.objects.create(
          train_id=train['id'],
          depot_id=train['depotId'],
          certificates=certificates,
          branding=branding,
          cleaning_slot=train['cleaningSlot'],
          crew=crew,
          override=override,
          mileage_odometer=train['mileage']['odometer'],
          mileage_last_service=datetime.strptime(train['mileage']['lastService'], '%Y-%m-%d').date(),
          service_status=train.get('serviceStatus'),
          arrival_time=train.get('arrivalTime'),
      )

      for job in train['jobCards']['all']:
        JobCard.objects.create(
          train=t,
          title=job['title'],
          priority=job['priority'],
        )

    # Import induction list (after all trains are created)
    for entry in mock_induction_list:
      train = Train.objects.filter(train_id=entry['trainId']).first()
      if train:
        InductionList.objects.create(
          train=train,
          score=entry['score'],
          reason=entry['reason'],
          override=entry['override'],
          violations=entry['violations'],
        )

    self.stdout.write(self.style.SUCCESS('Mock data imported successfully.'))
