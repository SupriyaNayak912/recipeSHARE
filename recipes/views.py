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
import requests
import json

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


@login_required
def ai_recipe_finder_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'}, status=400)
    
    # Check if Groq API Key is configured
    api_key = getattr(settings, 'GROQ_API_KEY', '')
    if not api_key:
        return JsonResponse({
            'error': 'Groq API Key is not configured. Please add GROQ_API_KEY to your .env file.'
        }, status=500)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON request body.'}, status=400)

    ingredients = data.get('ingredients', '').strip()
    dietary_preference = data.get('dietary_preference', '').strip()

    if not ingredients:
        return JsonResponse({'error': 'Ingredients list is required.'}, status=400)

    # Call Groq API
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_instruction = (
        "You are a professional chef. Create 3 recipe suggestions based ONLY on the available ingredients "
        "and the optional dietary preferences provided by the user. "
        "The response MUST be a JSON object matching this schema exactly:\n"
        "{\n"
        "  \"recipes\": [\n"
        "    {\n"
        "      \"title\": \"string (name of the recipe)\",\n"
        "      \"description\": \"string (short appetising description of the dish)\",\n"
        "      \"ingredients\": [\n"
        "        \"string (ingredient 1 with quantity)\",\n"
        "        \"string (ingredient 2 with quantity)\"\n"
        "      ],\n"
        "      \"instructions\": [\n"
        "        \"string (step 1)\",\n"
        "        \"string (step 2)\"\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Ensure your response is raw valid JSON without markdown formatting backticks."
    )

    user_prompt = f"Available ingredients in my kitchen: {ingredients}"
    if dietary_preference:
        user_prompt += f"\nDietary preferences: {dietary_preference}"

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        choices = result.get('choices', [])
        if not choices:
            return JsonResponse({'error': 'No response choices returned from Groq.'}, status=502)
        
        content_str = choices[0].get('message', {}).get('content', '')
        if not content_str:
            return JsonResponse({'error': 'Empty content returned from Groq.'}, status=502)
        
        # Parse the JSON string from Groq content
        recipe_data = json.loads(content_str)
        
        # Validate that we got a list of recipes with expected fields
        recipes_list = recipe_data.get('recipes', [])
        if not isinstance(recipes_list, list) or len(recipes_list) == 0:
            return JsonResponse({'error': 'AI response did not return a valid list of recipes.'}, status=502)

        for rec in recipes_list:
            required_fields = ['title', 'description', 'ingredients', 'instructions']
            if not all(field in rec for field in required_fields):
                return JsonResponse({'error': 'AI response recipes did not match the expected schema.'}, status=502)

        return JsonResponse(recipe_data)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Failed to contact Groq API: {str(e)}'}, status=502)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Failed to parse AI response as JSON.'}, status=502)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)









