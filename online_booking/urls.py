from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin interface
    path('', include('reservations.urls')),  
    path('accounts/', include('accounts.urls')), 
]
