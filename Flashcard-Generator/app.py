from flask import Flask, request, render_template
import spacy
import requests
import os
import random
import urllib.parse

app = Flask(__name__)

# API keys
UNSPLASH_API_KEY = 'fv5JSNTdfdFOkT5WhKmH0EOagEq70F5LnOCHWMQbKXU'
PIXABAY_API_KEY = '39714185-83d1db31ff8ee42b19f76d98a'

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

def download_images(query, num_images=1, use_pixabay=False):
    if use_pixabay:
        # Use Pixabay API
        search_url = "https://pixabay.com/api/"
        params = {
            "key": PIXABAY_API_KEY,
            "q": urllib.parse.quote(query),
            "per_page": 3,
            "image_type": "illustration"
        }
        headers = {}  # Define an empty headers dictionary for Pixabay (not used)
    else:
        # Use Unsplash API
        search_url = "https://api.unsplash.com/photos/random"
        headers = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
        params = {
            "query": query,
            "count": num_images,
        }

    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=60)  # Specify a timeout in seconds (adjust as needed)
        response.raise_for_status()
        data = response.json()

        if use_pixabay:
            hits = data.get("hits", [])
            if not hits:
                print(f"No images found for '{query}' on Pixabay.")
                return

            for i, photo in enumerate(hits):
                image_url = photo.get("webformatURL")
                try:
                    image_data = requests.get(image_url, timeout=60)  # Specify a timeout in seconds (adjust as needed)
                    image_data.raise_for_status()

                    # Save the downloaded image to the "static" folder
                    image_path = os.path.join("static", f"{query}_{i+1}.jpg")
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_data.content)
                    
                    print(f"Downloaded image {i+1}/{num_images} related to '{query}'.")
                except Exception as e:
                    print(f"Error downloading image {i+1}: {e}")
        else:
            for i, photo in enumerate(data):
                image_url = photo["urls"]["regular"]
                try:
                    image_data = requests.get(image_url, timeout=60)  # Specify a timeout in seconds (adjust as needed)
                    image_data.raise_for_status()

                    # Save the downloaded image to the "static" folder
                    image_path = os.path.join("static", f"{query}_{i+1}.jpg")
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_data.content)
                    
                    print(f"Downloaded image {i+1}/{num_images} related to '{query}'.")
                except Exception as e:
                    print(f"Error downloading image {i+1}: {e}")

    except requests.exceptions.RequestException as e:
        print("Error:", e)

@app.route("/", methods=["GET", "POST"])
def index():
    sentences = []
    images_downloaded = []
    input_texts = []
    use_pixabay = False
    num_sentences = 0  # Initialize num_sentences to 0

    if request.method == "POST":
        input_text = request.form["input_text"]
        # Split the input paragraph into sentences
        sentences = input_text.split(". ")  # Assuming sentences are separated by periods
        num_sentences = len(sentences)

        for sentence in sentences:
            # Process each sentence
            nouns = process_input(sentence)

            if len(nouns) < 2:
                continue

            # Randomly select two nouns from the sentence
            random_nouns = random.sample(nouns, 2)

            for noun in random_nouns:
                download_images(noun, num_images=1, use_pixabay=use_pixabay)
                images_downloaded.append(f"{noun}_1.jpg")
            input_texts.append(sentence)

    return render_template("index.html", num_sentences=num_sentences, images_downloaded=images_downloaded, input_texts=input_texts, use_pixabay=use_pixabay)

def process_input(input_text):
    doc = nlp(input_text)
    nouns = [token.text for token in doc if token.pos_ == "NOUN"]
    return nouns

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 3000
    app.run(host=host, port=port, debug=False)
