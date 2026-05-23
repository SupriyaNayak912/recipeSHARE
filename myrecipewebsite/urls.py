from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from recipes import views as recipe_views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(), name='account_login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='account_logout'),
    path('accounts/signup/', recipe_views.signup, name='account_signup'),
    path('', include('recipes.urls')),


    
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
