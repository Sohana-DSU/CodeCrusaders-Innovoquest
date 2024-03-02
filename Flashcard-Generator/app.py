from flask import Flask, request, render_template
import spacy
import requests
import os
import random
import urllib.parse
import json
import re

# To load dotenv to fix vulnerable security issue of displaying API keys
from dotenv import load_dotenv

app = Flask(__name__)

# To load environment variables from env file
load_dotenv()

# Use os.getenv to get keys from environment variables
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

subjects_data = {
    '1': ['Hindi', 'English', 'Maths', 'Urdu'],
      '2': ['Hindi', 'English', 'Maths', 'Urdu'],
      '3': ['Hindi', 'English', 'Maths', 'Urdu', 'Environmental Studies'],
      '4': ['Hindi', 'English', 'Maths', 'Urdu', 'Environmental Studies'],
      '5': ['Hindi', 'English', 'Maths', 'Urdu', 'Environmental Studies'],
      '6': ['Hindi', 'English', 'Maths', 'Urdu', 'Science', 'Social Science', 'Sanskrit'],
      '7': ['Hindi', 'English', 'Maths', 'Urdu', 'Science', 'Social Science', 'Sanskrit'],
      '8': ['Hindi', 'English', 'Maths', 'Urdu', 'Science', 'Social Science', 'Sanskrit'],
      '9': ['Hindi', 'English', 'Maths', 'Urdu', 'Science', 'Social Science', 'Sanskrit', 'Health and Physical Education', 'ICT'],
      '10': ['Hindi', 'English', 'Maths', 'Urdu', 'Science', 'Social Science', 'Sanskrit', 'Health and Physical Education', 'ICT'],
}

def split_paragraph_into_sentences(paragraph):
    # Use regular expression to split the paragraph into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', paragraph)
    
    return sentences

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
        response = requests.get(search_url, headers=headers, params=params, timeout=180)  # Specify a timeout in seconds (adjust as needed)
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
                    image_data = requests.get(image_url, timeout=180)  # Specify a timeout in seconds (adjust as needed)
                    image_data.raise_for_status()

                    # Save the downloaded image to the "static" folder
                    image_path = os.path.join("static", "images", f"{query}_{i+1}.jpg")
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_data.content)
                    
                    print(f"Downloaded image {i+1}/{num_images} related to '{query}'.")
                except Exception as e:
                    print(f"Error downloading image {i+1}: {e}")
        else:
            for i, photo in enumerate(data):
                image_url = photo["urls"]["regular"]
                try:
                    image_data = requests.get(image_url, timeout=180)  # Specify a timeout in seconds (adjust as needed)
                    image_data.raise_for_status()

                    # Save the downloaded image to the "static" folder
                    image_path = os.path.join("static", "images", f"{query}_{i+1}.jpg")
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
    selected_grade = "1"  # Default value for selected_grade
    selected_subject = "Hindi"  # Default value for selected_subject
    

    if request.method == "POST":
        input_text = request.form["input_text"]
        selected_grade = request.form.get("grade", "1")  # Get the selected grade from the form (if submitted)
        selected_subject = request.form.get("subject", "Hindi")
        # Split the input paragraph into sentences
        paragraph = input_text
        sentences = split_paragraph_into_sentences(paragraph)  # Assuming sentences are separated by periods
        num_sentences = len(sentences)
        use_pixabay = "use_pixabay" in request.form
       
       
        for sentence in sentences:
            # Process each sentence
            nouns = process_input(sentence)

            if len(nouns) < 2:
                continue

            # Randomly select two nouns from the sentence
            # random_nouns = random.sample(nouns, 2)
            # We are removing the randomizing logic
            

            for noun in nouns:
                download_images(noun, num_images=1, use_pixabay=use_pixabay)
                if download_images is None:
                    return render_template("index.html", error_message="There was an issue with image download. Please try again later.", subjects=subjects_data)    
                images_downloaded.append(f"{noun}_1.jpg")
            input_texts.append(sentence)
            
    data = {
        "num_sentences": num_sentences,
        "images_downloaded": images_downloaded,
        "input_texts": input_texts
    }
    
    filename = f"{selected_grade}_{selected_subject}.json"
    json_file_path = os.path.join("static", "database", filename)
    
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file, indent=2)

    return render_template(
        "index.html",
        num_sentences=num_sentences,
        images_downloaded=images_downloaded,
        input_texts=input_texts,
        use_pixabay=use_pixabay,
        subjects=subjects_data,
        selected_grade=selected_grade,  # Pass the selected grade to the template
        selected_subject=selected_subject,# Pass the selected subject to the template
        error_message=None
    )
    #return render_template("index.html", num_sentences=num_sentences, images_downloaded=images_downloaded, input_texts=input_texts, use_pixabay=use_pixabay, subjects=subjects_data)

def process_input(input_text):
    doc = nlp(input_text)
    
    important_words = []
    
    for i in range(len(doc) - 1):  # Adjust the range to stop at the second-to-last token
        # Check if the current token is a noun
        if doc[i].pos_ == "NOUN":
            # Check if the next token is an adjective
            if doc[i + 1].pos_ == "ADJ":
                # Concatenate the adjective and noun
                phrase = f"{doc[i + 1].text.lower()} {doc[i].text.lower()}"
                important_words.append(phrase)
            
            else:
                # If no adjective or verb after the noun, add only the noun
                important_words.append(doc[i].text.lower())
    
    # Include the last token if it is a noun
    if len(doc) > 0 and doc[-1].pos_ == "NOUN":
        important_words.append(doc[-1].text.lower())
                
    # Include verbs
    important_words += [token.text.lower() for token in doc if token.pos_ == "VERB"]
    # Include adjectives
    important_words += [token.text.lower() for token in doc if token.pos_ == "ADJ"]
              
    important_words = [word for word in important_words if word not in ["the", "a", "an", "it", "he", "she"]]
    important_words = important_words[:2]
    
    return important_words


# Add a exception function for nouns and come back later statement for third party APIs

if __name__ == "__main__":
    host = '0.0.0.0'
    port = 5000
    app.run(host=host, port=port, debug=True)
