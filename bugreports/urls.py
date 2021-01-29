from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'bugreports'

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'buggyproject', views.BuggyProjectViewSet)
router.register(r'bug', views.BugViewSet)
router.register(r'occusian', views.OccasionViewSet)
router.register(r'reports', views.ReportsViewSet,
                basename='reports')

urlpatterns = [
    path('api/', include(router.urls)),

]
