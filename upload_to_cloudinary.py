import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myrecipewebsite.settings')
django.setup()

from recipes.models import Recipe
import cloudinary
import cloudinary.uploader

def main():
    # Retrieve credentials from Django settings/environment
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    if not (cloud_name and api_key and api_secret):
        print("Error: Cloudinary credentials not found in environment variables.")
        return

    # Configure Cloudinary SDK
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )

    recipes = Recipe.objects.exclude(image='')
    print(f"Found {recipes.count()} recipes with images in database. Starting upload to Cloudinary...")

    for recipe in recipes:
        if not recipe.image:
            continue
            
        # Get the path of the local file
        local_path = recipe.image.path
        if os.path.exists(local_path):
            # Deriving the public_id that django-cloudinary-storage expects:
            # If recipe.image.name is 'recipes/matar-paneer-1.jpg',
            # the public_id needs to be 'media/recipes/matar-paneer-1' (without extension)
            relative_name = recipe.image.name
            base_name, _ = os.path.splitext(relative_name)
            public_id = f"media/{base_name}"
            
            print(f"\nUploading '{recipe.title}':")
            print(f"  - Local file: {local_path}")
            print(f"  - Cloudinary Public ID: {public_id}")
            
            try:
                result = cloudinary.uploader.upload(
                    local_path,
                    public_id=public_id,
                    overwrite=True,
                    resource_type="image"
                )
                print(f"  -> Uploaded successfully! URL: {result.get('secure_url')}")
            except Exception as e:
                print(f"  -> Error uploading: {e}")
        else:
            print(f"\n[Warning] Local file not found for '{recipe.title}': {local_path}")

    print("\nAll done!")

if __name__ == '__main__':
    main()
