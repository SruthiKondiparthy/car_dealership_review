from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import CarModel, CarDealer
from .restapis import get_dealers_from_cf, get_dealers_by_id,get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/user_registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/user_registration.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            print("logged in ....")
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')
    
# Create your views here.
def my_home_view(request):
    return render(request, 'djangoapp/home.html')

# Create an `about` view to render a static about page
def about(request):
    return render(request, 'djangoapp/about.html')

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    company_address = "2150 Ogden Ave,Downers Grove,IL 60515"
    telephone_number = "+1234567890"

    context = {
        'company_address': company_address,
        'telephone_number': telephone_number,
    }
    return render(request, 'djangoapp/contact.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}    
    if request.method == "GET":       
        url = "https://sruthiravuru-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        if not url:
            return render(request, 'djangoapp/index.html')

        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        print(dealerships)
        # Add the dealerships list to the context
        context['dealership_list'] = dealerships        
        # Return an HTTP response rendering the 'djangoapp/index.html' template with the context
        return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://sruthiravuru-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealer = get_dealers_by_id(url=dealer_url, dealerId=dealer_id)
        context["dealer"] = dealer

        review_url = "https://sruthiravuru-5000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
        reviews = get_dealer_reviews_from_cf(url=review_url, dealer_id=dealer_id)
        print(reviews)
        context["reviews"] = reviews        
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}   
    dealer_url = "https://sruthiravuru-3000.theiadockernext-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
  
    # Get dealer information
    dealer = get_dealers_by_id(dealer_url, dealer_id)
    context["dealer"] = dealer

    if request.method == 'POST':
        # Check if the user is authenticated
        if request.user.is_authenticated:
            username = request.user.username
            
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            payload = {
                "dealership": dealer_id,
                "name": username,
                "purchase": request.POST.get("purchasecheck") == 'on',
                "review": request.POST.get("content"),
                "purchase_date": request.POST.get("purchasedate"),
                "car_make": car.car_make.name,
                "car_model": car.name,
                "car_year": int(car.year.strftime("%Y")),
                "id": dealer_id,
                "time": datetime.utcnow().isoformat()
            }
            '''user_review = {}
            user_review["time"] = datetime.utcnow().isoformat()
            user_review["name"] = username
            user_review["dealership"] = dealer_id
            user_review["id"] = dealer_id            
            user_review['review'] = request.POST['content']
            user_review['purchase'] = False  
        
        if 'purchasecheck' in request.POST:
            if request.POST['purchasecheck'] == 'on':
                user_review['purchase'] = True
                user_review['purchase_date'] = request.POST['purchasedate']
                user_review['car_make'] = car.car_make.name
                user_review['car_model'] = car.name
                user_review['car_year'] = int(car.year.strftime("%Y"))'''           
            
        review_post_url = ""             
        post_request(review_post_url, payload, id=dealer_id)  
        
        return redirect('djangoapp:dealer_details', dealer_id=dealer_id)
    else:
        if request.method == 'GET':
            cars = CarModel.objects.all()                                     
            context["cars"] = cars
            return render(request, 'djangoapp/add_review.html', context)        