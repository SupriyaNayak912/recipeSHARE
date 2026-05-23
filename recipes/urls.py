from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.recipe_list, name='recipe_list'),
    path('add/', views.add_recipe, name='add_recipe'),
    path('', views.home, name='home'),
    path('recipe/<int:recipe_id>/save/', views.save_recipe, name='save_recipe'),
    path('saved_recipes/', views.saved_recipes, name='saved_recipes'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/new/', views.recipe_create, name='recipe_create'),
    path('recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('recipe/<int:pk>/comment/', views.add_comment_to_recipe, name='add_comment_to_recipe'),
    path('recipe/<int:pk>/rating/', views.add_rating_to_recipe, name='add_rating_to_recipe'),
    path('search/', views.search_recipes, name='search_recipes'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('about-us/', views.about_us, name='about_us'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('profile/', views.profile_view, name='profile')
    



]
