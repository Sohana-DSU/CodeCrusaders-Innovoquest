import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['STATIC_URL_PATH'] = '/static'

selected_grade = None
selected_subject = None# Initialize a variable to store the selected grade

# Function to load data from JSON file
def load_data_from_json(selected_grade, selected_subject):
    filename = f"{selected_grade}_{selected_subject}.json"
    json_file_path = os.path.join("static", "database", filename)
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return None  # Return None if the file is not found

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact_page')
def contact_page():
    return render_template('contact_page.html')

@app.route('/about_page')
def about_page():
    return render_template('about_page.html')

@app.route('/genres_page')
def genres_page():
    return render_template('genres_page.html')

@app.route('/grades_page')
def grades_page():
    return render_template('grades_page.html')

@app.route('/subjects/<int:grade>')
def subjects(grade):
    global selected_grade  # Access the global variable
    selected_grade = grade# Update the selected grade
    return render_template('subjects_page.html', grade=grade)


@app.route('/flashcard/')
def flashcards():
    global selected_grade# Access the global variable
    global selected_subject
    selected_subject = request.args.get('subject')
    if selected_subject:
        print(f"Selected Subject: {selected_subject}")
        # Rest of your code handling the selected subject...
    else:
        print("No subject selected")

    print(f"Selected Grade: {selected_grade}")
    #print(f"Selected Subject: {selected_subject}")# For example, print the selected grade
    # Load data from JSON file
    data = load_data_from_json(selected_grade, selected_subject)
    
    # Render the not_updated_yet.html template if data is None
    if data is None:
        return render_template('not_updated_yet.html')

    # Pass data to flashcards.html
    return render_template('flashcard.html', data=data)

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 3000
    app.run(host=host, port=port, debug=False)