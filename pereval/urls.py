from django.urls import path
from .views import SubmitDataView, SubmitDataDetailView

urlpatterns = [
    path('submitData/', SubmitDataView.as_view(), name='submit-data'),
    path('submitData/<int:pk>/', SubmitDataDetailView.as_view(), name='submit-data-detail'),
]