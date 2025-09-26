from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
from .services import process_train_dataset

@csrf_exempt
def run_optimizer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse({'error': 'Invalid JSON', 'details': str(e)}, status=400)
        # Run optimizer on the received data
        result = process_train_dataset(data)
        # TODO: Save result to the database as needed
        return JsonResponse(result, safe=False)
    else:
        return JsonResponse({'error': 'POST request required'}, status=405)