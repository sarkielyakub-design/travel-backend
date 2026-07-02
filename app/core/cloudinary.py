import os
import cloudinary

print("Cloud Name:", os.getenv("CLOUDINARY_CLOUD_NAME"))
print("API Key:", os.getenv("CLOUDINARY_API_KEY"))
print("API Secret Exists:", bool(os.getenv("CLOUDINARY_API_SECRET")))

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)