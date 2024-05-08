import os
from PIL import Image
import torch
from clip import clip

# Load the CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def search_images(query, image_directory, top_n=5):
    print(query)
    print(image_directory)
    
    # Implement your image search logic using the CLIP model
    images = load_images_from_directory(image_directory)
    results = []
    text_encoded = model.encode_text(clip.tokenize(query).to(device))
    
    for image_path, image_tensor in images:
        image_encoded = model.encode_image(image_tensor.unsqueeze(0).to(device))
        similarity = (image_encoded.squeeze(1) @ text_encoded.T).detach().cpu().numpy()[0]
        results.append({'path': image_path, 'similarity': float(similarity)})
    
    # Sort the results by similarity score in descending order
    sorted_results = sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    # Return the top `n` results
    return sorted_results

def load_images_from_directory(directory):
    images = []
    for filename in os.listdir(directory):
        if filename.endswith(('.jpg', '.png', '.jpeg', '.webp', '.gif', '.tiff', '.bmp', '.svg', '.raw')):
            image_path = os.path.join(directory, filename)
            image_tensor = preprocess(Image.open(image_path))
            images.append((image_path, image_tensor))
    return images

''' 
# Example usage
directory_path = os.getcwd()
results = search_images("a photo of a dog", directory_path)
print(results)
'''
