from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'trains', TrainViewSet)
router.register(r'branding', BrandingViewSet)
router.register(r'jobcards', JobCardViewSet)
router.register(r'induction', InductionListViewSet, basename='induction')

urlpatterns = [
    path('', include(router.urls)),
    path('frontend-data/', FrontendDataView.as_view(), name='frontend-data'),
    path('total-trains/', TotalTrainsAPIView.as_view(), name='total-trains'),  # New endpoint
    path('jobcard-backlog/', JobCardBacklogAPIView.as_view(), name='jobcard-backlog'),  # New endpoint
    path('train-age-distribution/', TrainAgeDistributionAPIView.as_view(), name='train-age-distribution'),  # New endpoint

]
