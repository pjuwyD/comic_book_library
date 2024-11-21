# Comicbook library Flask app

This Flask-based web application is designed to manage, display, and explore comic books. It currently supports two comic series: **Dylan Dog** and **Lazarus Ledd**. The app allows users to view comics by edition, manage their library, analyze statistics, and populate the database using a scraping feature.

## Features

### 1. Comic Browser
- **Dylan Dog Editions**:
  - Extra
  - Almanah
  - Gigant
  - Normal
  - Special
- **Lazarus Ledd Editions**:
  - Extra
  - Normal
  - Special

Each edition is displayed with its respective comics, using visually styled buttons and tables for an engaging user experience.

### 2. Library Management
- **Set Ownership**: Allows users to mark comics as part of their collection.
- **Question Ownership**: Provides insights into ownership status for specific comics.
- **Statistics**: Displays detailed statistics on the comic library, including counts, ownership details, and more.

### 3. Scraping Feature
The app includes a scraping tool that can automatically fetch comic details and populate the database (at the moment json structured file -> in the future real DB will be used). 
The scraping process retrieves:
- Comic titles
- Edition
- Numbers
- Publishers
- Additional metadata
- Cover images (stored in a structured directory tree)

### 4. User-Friendly Design
- Custom styles tailored to Dylan Dog and Lazarus Ledd themes:
  - Dylan Dog: Black and yellow theme.
  - Lazarus Ledd: Blue and white theme.
- Responsive layout using **Bootstrap** for optimal viewing on various devices.
- Hover and click effects for buttons to enhance interactivity.

### 5. Easy Navigation
- Each comic series page includes a navigation arrow in the top-left corner to return to the homepage.

## Setup and Installation

### Prerequisites
- Python 3.8 or newer
- Virtual environment (optional but recommended)

### Instalation steps
1. Clone the repo
```bash
git clone https://github.com/pjuwyD/comic_book_library.git
cd comic_book_library
```

2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Start the flask app
```bash
python comic_book_library/app.py
```

5. Open the app in your browser
```bash
http://127.0.0.1:5000
```

## Future Development

- Add more comic series support.
- Integrate advanced search and filtering.
- Rewrite the application as a Flutter app for improved cross-platform compatibility.

## Look and feel

![Screenshot 1](static/images/scr1.png)
![Screenshot 2](static/images/scr2.png)
![Screenshot 3](static/images/scr3.png)
![Screenshot 4](static/images/scr4.png)