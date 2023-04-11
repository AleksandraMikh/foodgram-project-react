from django.urls import path, include

app = 'users'


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

# urlpatterns.append(
#     re_path(r'^users\/(?P<user_id>\d+)\/subscribe/',
#             subscribe,
#             name='subscribe')
# )
