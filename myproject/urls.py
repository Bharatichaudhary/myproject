"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from myapp.views import *
from app1.views import *


# Define a custom test for superuser check
def is_superuser(user):
    return user.is_authenticated and user.is_superuser
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', places, name='places'),
    path('signup/', SignupPage, name='signup'),  # Make sure to add a trailing slash for consistency
    path('login/', LoginPage, name='login'),    # Make sure to add a trailing slash for consistency
    path('logout/', LogoutPage, name='logout'),
    path('rate-destination/<int:destination_id>/', rate_destination, name='rate_destination'),
    path('get-details/<int:destination_id>/', get_details, name='get_details'),

    # Apply the user_passes_test decorator to restrict access to superusers only
    path('create-destination/', user_passes_test(is_superuser)(create_places), name='create_places'),
    path('delete-destination/<id>/', user_passes_test(is_superuser)(delete_destination), name='delete_destination'),
    path('update-destination/<id>/', user_passes_test(is_superuser)(update_destination), name='update_destination'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
