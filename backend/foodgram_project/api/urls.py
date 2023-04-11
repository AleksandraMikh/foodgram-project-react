from django.urls import path, include, re_path

from .views import TagViewSet, IngredientViewSet, RecipeViewSet, subscribe, SubscriptionsListView
from rest_framework.routers import DefaultRouter

app = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    re_path(r'^users/subscriptions/',
            SubscriptionsListView.as_view(),
            name='subscribtions'
            ),
    path('', include('users.urls'))

]

urlpatterns.extend(router.urls)

urlpatterns.append(
    re_path(r'^users\/(?P<user_id>\d+)\/subscribe/',
            subscribe,
            name='subscribe'))

# urlpatterns.append(
#     re_path(r'^users/subscriptions/',
#             SubscriptionsListView.as_view(),
#             name='subscribtions'
#             ))
