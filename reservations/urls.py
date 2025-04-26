from django.urls import path 
from . import views

app_name = 'reservations'

urlpatterns = [
    path('',views.index, name='base'),
    path('booking', views.booking, name='booking'),
    path('booking-submit', views.booking_submit, name='bookingsubmit'),
    path('user-panel', views.user_panel, name='userpanel'),
    path('user-update/<int:id>', views.user_update, name='userupdate'),
    path('user-update-submit/<int:id>', views.user_update_submit, name='userupdatesubmit'),
    path('staff-panel', views.staff_panel, name='staffpanel'),

]