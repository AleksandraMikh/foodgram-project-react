from django.urls import path, include

app = 'api'

urlpatterns = [
    path('', include('users.urls')),
]
