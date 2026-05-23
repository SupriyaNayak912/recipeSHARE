from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Recipe, Comment, Rating
from .forms import RecipeForm, CommentForm, RatingForm
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from .forms import CustomUserCreationForm
from django.core.files.storage import FileSystemStorage
from .forms import UploadFileForm
from django.contrib.auth.decorators import login_required
from .models import Recipe, SavedRecipe
from django.contrib import messages
from django.http import JsonResponse

@login_required
def save_recipe(request, recipe_id):
    recipe = Recipe.objects.get(pk=recipe_id)
    saved_recipe, created = SavedRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    if created:
        messages.success(request, 'Recipe saved successfully!')
    else:
        messages.info(request, 'Recipe is already saved.')

    return redirect('recipe_list')

@login_required
def saved_recipes(request):
    saved_recipes = SavedRecipe.objects.filter(user=request.user)
    return render(request, 'recipes/saved_recipes.html', {'saved_recipes': saved_recipes})

@login_required
def profile_view(request):
    user = request.user
    recipes = Recipe.objects.filter(author=user)
    return render(request, 'recipes/profile.html', {'user': user, 'recipes': recipes})


def recipe_create_view(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('recipe_list')  # Redirect after successful form submission
    else:
        form = RecipeForm()

    context = {
        'form': form,
    }
    return render(request, 'recipe_form.html', context)

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            # Save the file using default storage (FileSystemStorage)
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            return render(request, 'upload_success.html', {'filename': filename})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user  # Assign the current user as the author
            recipe.save()
            messages.success(request, 'Recipe created successfully!')
            return redirect('recipe_list')
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_new.html', {'form': form})

def home(request):
    return render(request, 'recipes/home.html')


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()

            # Specify the backend explicitly
            backend = 'django.contrib.auth.backends.ModelBackend'
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password1'), backend=backend)
            
            if user is not None:
                login(request, user, backend=backend)
                return redirect('recipe_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('recipe_list')
    else:
        form = AuthenticationForm()
    return render(request, 'recipes/login.html', {'form': form})


def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    comments = recipe.comments.all()
    ratings = recipe.ratings.all()
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe, 'comments': comments, 'ratings': ratings})

@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user  # Assign the current user as the author
            recipe.save()
            messages.success(request, 'Recipe created successfully!')
            return redirect('recipe_list')
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_new.html', {'form': form})

@login_required
def recipe_edit(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.user != recipe.author:
        messages.error(request, "You are not authorized to edit this recipe.")
        return redirect('recipe_detail', pk=recipe.pk)
    if request.method == "POST":
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.save()
            messages.success(request, "Recipe updated successfully!")
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipes/recipe_form.html', {'form': form})

@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.user == recipe.author:
        recipe.delete()
        messages.success(request, "Recipe deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this recipe.")
    return redirect('recipe_list')

@login_required
def add_comment_to_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.save()
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = CommentForm()
    return render(request, 'recipes/add_comment_to_recipe.html', {'form': form, 'recipe': recipe})

@login_required
def add_rating_to_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == "POST":
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.recipe = recipe
            rating.user = request.user
            rating.save()
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RatingForm()
    return render(request, 'recipes/add_rating_to_recipe.html', {'form': form, 'recipe': recipe})

def search_recipes(request):
    query = request.GET.get('q')
    recipes = Recipe.objects.filter(title__icontains=query) | Recipe.objects.filter(description__icontains=query)
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes, 'query': query})

def about_us(request):
    return render(request, 'recipes/about_us.html')

def contact_us(request):
    return render(request, 'recipes/contact_us.html')

def privacy_policy(request):
    return render(request, 'recipes/privacy_policy.html')







