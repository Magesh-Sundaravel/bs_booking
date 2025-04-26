from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from .models import *
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, "home.html",{})

@login_required
def booking(request):
    weekdays = valid_weekday(22)
    valid_days = is_weekday_valid(weekdays)

    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')
        if service is None:
            messages.error(request, "Please Select A Service!")
            return redirect('reservations:booking')

        request.session['day'] = day
        request.session['service'] = service

        return redirect('reservations:bookingsubmit')

    return render(request, 'booking.html', {
            'weekdays':weekdays,
            'valid_days':valid_days,
        })
@login_required
def booking_submit(request):
    user = request.user
    times = [
        "8 AM", "9 AM", "10 AM", "11 AM", "12 PM",
    "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM",
    ]
    today = timezone.now().date()  # Use timezone-aware date
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    maxDate = deltatime.strftime('%Y-%m-%d')

    #Get stored data from django session:
    day_str = request.session.get('day')
    service = request.session.get('service')

    if day_str:
        day = datetime.strptime(day_str, '%Y-%m-%d').date()
    else:
        day = None

    #Only show the time of the day that has not been selected before:
    available_times = check_time(times, day_str)
    if request.method == 'POST':
        time = request.POST.get("time")
        date = day_to_weekday(day_str)

        # Constants
        ALLOWED_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        if service is not None:
            if day and minDate <= day.strftime('%Y-%m-%d') <= maxDate:
                if date in ALLOWED_DAYS:
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1:
                            Appointment.objects.create(
                                user = user,
                                service = service,
                                day = day,
                                time = time,
                                time_ordered = timezone.now() # Set timezone-aware creation time
                            )
                            messages.success(request, "Appointment Saved!")
                            return render(request, 'userpanel.html')
                        else:
                            messages.error(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.error(request, "The Selected Day Is Full!")
                else:
                    messages.error(request, "The Selected Date Is Incorrect")
            else:
                    messages.error(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.error(request, "Please Select A Service!")

    return render(request, 'bookingsubmit.html', {
        'times': available_times,
    })

@login_required
def user_panel(request):
    user = request.user
    appointments = Appointment.objects.filter(user=user).order_by('day', 'time')
    return render(request, 'userpanel.html', {
        'user': user,
        'appointments': appointments,
    })

@login_required
def user_update(request, id):
    appointment = Appointment.objects.get(pk=id)
    userdatepicked = appointment.day
    #Copy  booking:
    today = timezone.now().date()
    minDate = today.strftime('%Y-%m-%d')

    #24h if statement in template:
    delta24 = userdatepicked >= (today + timedelta(days=1)).date()
    #Calling 'valid_weekday' Function to Loop days you want in the next 21 days:
    weekdays = valid_weekday(22)

    #Only show the days that are not full:
    valid_days = is_weekday_valid(weekdays)


    if request.method == 'POST':
        service = request.POST.get('service')
        day = request.POST.get('day')

        #Store day and service in django session:
        request.session['day'] = day
        request.session['service'] = service

        return redirect('reservations:userupdatesubmit', id=id)


    return render(request, 'userupdate.html', {
            'weekdays':weekdays,
            'valid_days':valid_days,
            'delta24': delta24,
            'id': id,
        })

@login_required
def user_update_submit(request, id):
    user = request.user
    times = [
        "8 AM", "9 AM", "10 AM", "11 AM", "12 PM",
    "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM",
    ]
    today = timezone.now().date()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    maxDate = deltatime.strftime('%Y-%m-%d')

    day_str = request.session.get('day')
    service = request.session.get('service')

    if day_str:
        day = datetime.strptime(day_str, '%Y-%m-%d').date()
    else:
        day = None

    #Only show the time of the day that has not been selected before and the time he is editing:
    available_times = check_edit_time(times, day_str, id)
    appointment = Appointment.objects.get(pk=id)
    userSelectedTime = appointment.time
    if request.method == 'POST':
        time = request.POST.get("time")
        date = day_to_weekday(day_str)

        ALLOWED_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        if service is not None:
            if day and minDate <= day.strftime('%Y-%m-%d') <= maxDate:
                if date in ALLOWED_DAYS:
                    if Appointment.objects.filter(day=day).count() < 11:
                        if Appointment.objects.filter(day=day, time=time).count() < 1 or userSelectedTime == time:
                            Appointment.objects.filter(pk=id).update(
                                user = user,
                                service = service,
                                day = day,
                                time = time,
                            )
                            messages.success(request, "Appointment Edited!")
                            return redirect('accounts:home')
                        else:
                            messages.error(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.error(request, "The Selected Day Is Full!")
                else:
                    messages.error(request, "The Selected Date Is Incorrect")
            else:
                    messages.error(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.error(request, "Please Select A Service!")
        return redirect('userpanel')

    return render(request, 'userupdatesubmit.html', {
        'times': available_times,
        'id': id,
    })

def staff_panel(request):
    today = timezone.now().date()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    maxDate = deltatime.strftime('%Y-%m-%d')
    #Only show the Appointments 21 days from today
    items = Appointment.objects.filter(day__range=[minDate, maxDate]).order_by('day', 'time')

    return render(request, 'staffpanel.html', {
        'items':items,
    })

###-----------------------------------------------------------------

def day_to_weekday(x):
    if x:
        z = datetime.strptime(x, "%Y-%m-%d").date()
        y = z.strftime('%A')
        return y
    return None

def valid_weekday(days):
    #Loop days you want in the next 21 days:
    today = timezone.now().date()
    weekdays = []
    for i in range (0, days):
        current_date = today + timedelta(days=i)
        y = current_date.strftime('%A')
        ALLOWED_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        if y in ALLOWED_DAYS:
            weekdays.append(current_date.strftime('%Y-%m-%d'))
    return weekdays

def is_weekday_valid(x):
    valid_days = []
    for j in x:
        if Appointment.objects.filter(day=j).count() < 11:
            valid_days.append(j)
    return valid_days

def check_time(times, day_str):
    #Only show the time of the day that has not been selected before:
    x = []
    if day_str:
        for k in times:
            if Appointment.objects.filter(day=day_str, time=k).count() < 1:
                x.append(k)
    return x

def check_edit_time(times, day_str, id):
    #Only show the time of the day that has not been selected before:
    x = []
    try:
        appointment = Appointment.objects.get(pk=id)
        time = appointment.time
        if day_str:
            for k in times:
                if Appointment.objects.filter(day=day_str, time=k).count() < 1 or time == k:
                    x.append(k)
    except Appointment.DoesNotExist:
        pass  # Handle the case where the appointment doesn't exist
    return x