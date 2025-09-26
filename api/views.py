from rest_framework import viewsets, views
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from django.db.models import Count

# InductionList API ViewSet
class InductionListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InductionList.objects.all()
    serializer_class = InductionListSerializer

class FrontendDataView(views.APIView):
	def get(self, request):
		trains = []
		train_qs = Train.objects.all()
		for train in train_qs:
			jobcards = train.jobcards.all()
			trains.append({
				"id": train.train_id,
				# ...existing code...
			})
		# Example metrics (static, can be replaced with real logic)
		metrics = {
			"dashboard": {
				"totalSelected": 8,
				"brandingSLA": 87.5,
				"mileageVariance": 12.3,
				"cleaningSlotsUsed": 5,
				"totalCleaningSlots": 6,
				"shuntingCost": 245,
				"alertsCount": 3,
			},
			"baseline": {
				"brandingSLA": 87.5,
				"mileageVariance": 12.3,
				"cleaningSlots": 5,
				"shuntingCost": 245,
			},
			"scenario": {
				"brandingSLA": 92.1,
				"mileageVariance": 8.7,
				"cleaningSlots": 6,
				"shuntingCost": 267,
			},
		}
		return Response({"trains": trains, "metrics": metrics})

class TrainViewSet(viewsets.ModelViewSet):
	queryset = Train.objects.all()
	serializer_class = TrainSerializer

	def list(self, request, *args, **kwargs):
		trains = []
		train_qs = Train.objects.all()
		for train in train_qs:
			jobcards = train.jobcards.all()
			trains.append({
				"id": train.train_id,
				"depotId": train.depot_id,
				"certificates": {
					"stock": train.certificates.stock,
					"signal": train.certificates.signal,
					"telecom": train.certificates.telecom,
				},
				"jobCards": {
					"count": jobcards.count(),
					"all": [
						{"title": j.title, "priority": j.priority} for j in jobcards
					],
				},
				"mileage": {
					"odometer": train.mileage_odometer,
					"lastService": train.mileage_last_service.strftime("%Y-%m-%d") if train.mileage_last_service else None,
				},
				"branding": {
					"status": train.branding.status,
					"hoursRemaining": train.branding.hours_remaining,
					"totalHours": train.branding.total_hours,
				},
				"cleaningSlot": train.cleaning_slot,
				"crew": {
					"assigned": train.crew.assigned,
					"driverId": train.crew.driver_id,
					"validUntil": train.crew.valid_until,
				},
				"override": {
					"flag": train.override.flag,
					"category": train.override.category,
					"reason": train.override.reason,
					"by": train.override.by,
				},
			})
		return Response(trains)



class BrandingViewSet(viewsets.ModelViewSet):
	queryset = Branding.objects.all()
	serializer_class = BrandingSerializer

class JobCardViewSet(viewsets.ModelViewSet):
	queryset = JobCard.objects.all()
	serializer_class = JobCardSerializer

class TotalTrainsAPIView(APIView):
	def get(self, request):
		total_trains = Train.objects.count()
		return Response({"total_trains": total_trains})
	
class JobCardBacklogAPIView(APIView):
    def get(self, request):
        # Total job cards
        total_jobcards = JobCard.objects.count()
        # Severity breakdown
        severity_counts = (
            JobCard.objects.values('priority')
            .annotate(count=Count('id'))
            .order_by('priority')
        )
        severity_dict = {item['priority']: item['count'] for item in severity_counts}
        return Response({
            "total_jobcards": total_jobcards,
            "severity_breakdown": severity_dict
        })
	
class TrainAgeDistributionAPIView(APIView):
    def get(self, request):
        odometers = list(Train.objects.values_list('mileage_odometer', flat=True))
        return Response({"odometers": odometers})