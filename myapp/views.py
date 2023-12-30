from django.shortcuts import render, redirect
from .models import destination  # Update the import
from .forms import RatingForm  # Create a form for rating (see next step)
from django.shortcuts import render, get_object_or_404, redirect
from .models import destination, Rating
from django.db import models
from django.db.models import Q

# Create your views here.

def create_places(request):
    if request.method == "POST":
        data = request.POST
        name = data.get('name')
        location = data.get('location')
        description = data.get('description')
        keywords = data.get('keywords')
        image = data.get('image')
        destination.objects.create(  # Update the model name
            name=name,
            location=location,
            description=description,
            keywords=keywords,
            image=image
        )
    return render(request, 'places.html', )
from django.shortcuts import render
from .models import destination
from django.db.models import Avg

def places(request):
    '''query = destination.objects.annotate(avg_rating=Avg('rating__rating'))

    queryset = query.order_by('-ratings')[:10]
    queryset = destination.objects.all()'''
    queryset = destination.objects.all()
    sorted_queryset = quicksort(queryset)
    # Check if the user is logged in
    user = request.user if request.user.is_authenticated else None

    if request.GET.get('search'):
        search_term = request.GET.get('search')
        search_terms = search_term.split()  # Split the search term into separate words
        print(search_terms)
        # Create a Q object for each term and combine them with the | (OR) operator
        query = Q()
        for term in search_terms:
            query |= Q(keywords__icontains=term)

        # Apply the filter to the queryset
        queryset = queryset.filter(query)
        #queryset = queryset.filter(keywords__icontains=request.GET.get('search'))
        sorted_queryset = quicksort(queryset)

    context = {'destinations': sorted_queryset, 'user': user}

    return render(request, 'home.html', context=context)
def quicksort(arr):
    if len(arr) <= 1:
        return arr  # Already sorted

    # Call the method to get the average rating
    pivot = arr[len(arr) // 2].average_rating()
    left = [x for x in arr if x.average_rating() > pivot]
    middle = [x for x in arr if x.average_rating() == pivot]
    right = [x for x in arr if x.average_rating() < pivot]

    return quicksort(left) + middle + quicksort(right)

def delete_destination(request,id):
    queryset = destination.objects.get(id=id)
    queryset.delete()
    return redirect('/create-destination')


def update_destination(request, id):
    queryset = destination.objects.get(id=id)

    if request.method == "POST":
        data = request.POST
        name = data.get('name')
        location = data.get('location')
        description = data.get('description')
        keywords = data.get('keywords')
        image = data.get('image')
        queryset.name = name
        queryset.location = location
        queryset.description = description
        queryset.keywords = keywords
        queryset.image = image
        print(data)
        queryset.save()
        return redirect('/')

    context = {'destinations': queryset, 'user': request.user}
    print(queryset.description)
    return render(request, 'update_place.html', context=context)

def register_user(request):
    return render(request, 'register.html')



def rate_destination(request, destination_id):
    destination_instance = get_object_or_404(destination, id=destination_id)
    user = request.user

    # Check if the user has already rated the destination
    existing_rating = Rating.objects.filter(user=user, location=destination_instance).first()

    if existing_rating:
        # If the user has already rated, you might want to handle this case
        # For now, let's redirect them back to the destination page
        already_rated = True
        return render(request, 'rate_destination.html', {'destination': destination_instance, 'already_rated': already_rated})


    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            Rating.objects.create(user=user, location=destination_instance, rating=rating)
            return redirect('places')  # Redirect to the destination list after successful rating
    else:
        form = RatingForm()

    context = {'destination': destination_instance, 'form': form}
    return render(request, 'rate_destination.html', context)


def get_details(request,destination_id):
    queryset = destination.objects.get(id=destination_id)
    user = request.user if request.user.is_authenticated else None

    if user:
        recommended_destinations = collaborative_filtering(user)
    else:
        recommended_destinations = destination.objects.all()

    context = {'destination': queryset, 'recommends': recommended_destinations, 'user': user}
    return render(request, 'details.html', context)

def collaborative_filtering(user):
    # Get user's rated destinations
    user_ratings = Rating.objects.filter(user=user)

    # Find users who have rated the same destinations
    similar_users = Rating.objects.filter(location__in=user_ratings.values('location')).exclude(user=user)

    # Calculate similarity scores (e.g., using Pearson correlation)
    user_avg_rating = user_ratings.aggregate(Avg('rating'))['rating__avg']
    similar_users_avg_ratings = similar_users.values('user').annotate(avg_rating=Avg('rating'))

    # Fetch all ratings for destinations in a single query
    destination_ratings = Rating.objects.filter(location__in=user_ratings.values('location'))

    similarity_scores = {}

    # Recommend destinations based on collaborative filtering
    recommended_destinations = destination.objects.exclude(ratings__user=user)
    recommended_destinations = recommended_destinations.annotate(similarity=models.Value(0.0, models.FloatField()))

    for dest in recommended_destinations:
        # Extract ratings for the current destination
        destination_ratings_for_destination = destination_ratings.filter(location=dest)

        numerator = sum(
            [(rating.rating - user_avg_rating) * (similarity_scores[rating.user.id] - user_avg_rating)
             for rating in destination_ratings_for_destination]
        )
        denominator = sum([(similarity_scores[rating.user.id] - user_avg_rating) ** 2 for rating in destination_ratings_for_destination])

        # Calculate similarity
        similarity = numerator / (denominator + 1e-9) if denominator != 0 else 0  # Avoid division by zero
        dest.similarity = similarity
        similarity_scores[dest.id] = similarity

    # Order destinations by similarity in descending order
    recommended_destinations = recommended_destinations.order_by('-similarity')

    return recommended_destinations