from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from functools import wraps
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta
import os


# Load environment variables
load_dotenv()

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')


# ------------------------------------------
# Utility functions
# ------------------------------------------

def generate_jwt_token(user_id):
    """Generates a JWT token with user ID and 24-hour expiry."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token if isinstance(token, str) else token.decode('utf-8')


def token_required(view_func):
    """Decorator that ensures the view is accessed with a valid JWT token in cookies."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        token = request.COOKIES.get('token')
        if not token:
            return JsonResponse({'error': 'Authentication token missing.'}, status=401)

        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            request.payload = payload
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expired. Please log in again.'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': 'Invalid token. Please log in again.'}, status=401)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=401)

        return view_func(request, *args, **kwargs)
    return wrapped_view


# ------------------------------------------
# Views
# ------------------------------------------

def welcome_page(request):
    """Renders the welcome page using the template."""
    template = loader.get_template('home.html')
    return HttpResponse(template.render({}, request))

@csrf_exempt
@require_http_methods(["GET", "POST"])
def login_page(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('reservations:booking')
        else:
            # Return an 'invalid login' error message.
            ...
            messages.success(request, "There Was An Error!")
            return redirect('login')
    else:
        return render(request, 'login.html', {})


def logout_page(request):
    logout(request)
    messages.success(request, "Sign Out Successful")
    return redirect('base')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def signup_page(request):
    """Handles user signup, logs them in immediately, and redirects to profile page."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return render(request, 'signup.html')

        # Create new user
        user = User.objects.create_user(username=username, password=password)
        login(request, user)  
        token = generate_jwt_token(user.id)
        response = redirect('index')  
        response.set_cookie('token', token, httponly=True, samesite='Lax')

        messages.success(request, 'Signup successful! Welcome.')
        return response

    # If GET request → render the signup page
    return render(request, 'signup.html')










