from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from recipe.views import RecipeView
from order.views import OrderView

from . import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('recipe', RecipeView.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('recipe/<str:pk>', RecipeView.as_view({
        'put': 'update',
        'delete': 'destroy'
    })),
    path('order', OrderView.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('order/<str:pk>', OrderView.as_view({
        'put': 'update',
        'delete': 'destroy'
    })),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
