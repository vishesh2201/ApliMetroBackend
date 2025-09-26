from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
from .services import simulate_train_scenario

@csrf_exempt
def run_whatIf(request):
    print("run_whatIf called")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse({'error': 'Invalid JSON', 'details': str(e)}, status=400)
        
        if not isinstance(data, list):
            return JsonResponse({'error': 'Expected a list of scenarios'}, status=400)
        
        # train_data = [item["train_data"] for item in data if "train_data" in item]
        results = []
        for item in data:
            train_id = item.get("train_id") or item.get("trainId")
            scenario = item.get("scenario")
            train_data= item.get("train_data")
            if not train_id or not scenario:
                return JsonResponse({'error': 'Missing train_id or scenario in one of the items'}, status=400)
            print(train_id, scenario, train_data)
            result = simulate_train_scenario(train_id, scenario, train_data)
            print(result)
            results.append(result)
        return JsonResponse(results, safe=False)
    else:
        return JsonResponse({'error': 'POST request required'}, status=405)