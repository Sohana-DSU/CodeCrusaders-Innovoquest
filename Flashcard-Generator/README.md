# Flashlearn Flask Application

This Flask application generates flashcards based on input text, downloading images related to nouns in the sentences provided. It utilizes APIs to fetch images and processes text using Spacy for natural language processing.

## Overview

The application works by taking input text, splitting it into sentences, and extracting nouns from each sentence. It then randomly selects two nouns from each sentence and downloads images related to those nouns. The downloaded images are displayed along with the input sentences as flashcards on the web page.

## Dependencies

- Flask: Web framework for Python.
- Spacy: Library for natural language processing.
- Requests: Library for making HTTP requests.
- os: Module for interacting with the operating system.
- random: Module for generating random numbers.
- urllib.parse: Module for parsing URLs.

## API Keys

Ensure you have API keys for Unsplash and Pixabay APIs. Replace `UNSPLASH_API_KEY` and `PIXABAY_API_KEY` variables with your actual API keys.

## Installation

1. Install the required Python packages
2. Download the English language model for Spacy
## Usage
Run the Flask application

## Access the application in your web browser
http://127.0.0.1:3000/

Enter a paragraph or sentences into the input field and submit. The application will generate flashcards with images related to the nouns in the sentences.
