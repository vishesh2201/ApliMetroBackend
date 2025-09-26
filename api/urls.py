from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrainViewSet, BrandingViewSet, JobCardViewSet, FrontendDataView, InductionListViewSet

router = DefaultRouter()
router.register(r'trains', TrainViewSet)
router.register(r'branding', BrandingViewSet)
router.register(r'jobcards', JobCardViewSet)
router.register(r'induction', InductionListViewSet, basename='induction')

urlpatterns = [
    path('', include(router.urls)),
    path('frontend-data/', FrontendDataView.as_view(), name='frontend-data'),
]
