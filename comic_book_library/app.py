import json
import os
from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from comic_backend import scrape_comics, update_ownership_dict, set_ownership_bulk, get_ownership, get_statistics

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = b'\xf8\x95\xf7 Hb\xd5\x01\x07o\xa3\x1c\xef\x14\x1cG\xdb\xbcUpW\x97<\x8f'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of app.py
INFO_JSON_PATH_DOG = os.path.join(BASE_DIR, 'static', 'dylan_dog_comics', 'info.json')
INFO_JSON_PATH_LEDD = os.path.join(BASE_DIR, 'static', 'lazarus_ledd_comics', 'info.json')
COMICS = []

def try_load_dylan_dog_comics():
    """Load data from info.json into global COMICS variable."""
    global COMICS
    if os.path.exists(INFO_JSON_PATH_DOG):
        with open(INFO_JSON_PATH_DOG, 'r', encoding='utf-8') as f:
            COMICS = json.load(f)
    else:
        COMICS = []

def try_load_ledd_comics():
    """Load data from info.json into global COMICS variable."""
    global COMICS
    if os.path.exists(INFO_JSON_PATH_LEDD):
        with open(INFO_JSON_PATH_LEDD, 'r', encoding='utf-8') as f:
            COMICS = json.load(f)
    else:
        COMICS = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dylan_dog')
def dylan_dog():
    try_load_dylan_dog_comics()
    return render_template('dylan_dog.html')

@app.route('/lazarus_ledd')
def lazarus_ledd():
    try_load_ledd_comics()
    return render_template('lazarus_ledd.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    hero = request.form.get('hero')
    # Run the scraping function
    try:
        scrape_comics(hero)  # Call the scraping function
        flash('Scraping completed successfully!', 'success')
    except Exception as e:
        flash(f"Scraping failed: {str(e)}", 'error')
    if hero == "dog":
        return redirect(url_for('dylan_dog'))
    elif hero == "ledd":
        return redirect(url_for('lazarus_ledd'))

@app.route('/comics/<edition>/<hero>')
def comics_by_edition(edition, hero):
    if hero == "dog":
        try_load_dylan_dog_comics()
    elif hero == "ledd":
        try_load_ledd_comics()
    filtered_comics = []
    for comic in COMICS:
        if edition.lower() in comic["image_path"].lower():
            filtered_comics.append(comic)
    return render_template('comics.html', comics=filtered_comics, edition=edition, hero=hero)

@app.route('/update_ownership/<comic_id>', methods=['POST'])
def update_ownership(comic_id):
    data = request.get_json()
    ownership = data.get("owned", False)
    hero = data.get("name", None)
    update_ownership_dict(comic_id, ownership, hero)
    return jsonify({"message": "Ownership updated successfully"}), 200 

# Route to set ownership (form)
@app.route('/set_ownership/<hero>')
def set_ownership(hero):
    return render_template('set_ownership_form.html', hero=hero)

# Route to handle the form submission for bulk setting ownership
@app.route('/bulk_set_ownership', methods=['POST'])
def bulk_set_ownership():
    data = request.get_json()  # Parse the incoming JSON request
    comic_list = data.get('comic_list')
    edition = data.get('edition')
    name = data.get('hero')

    # Validation checks
    if not comic_list or not edition:
        return jsonify({"error": "Invalid data provided"}), 400

    # Process the comic list and edition (your logic goes here)
    # Example of processing
    print(f"Setting ownership for comics: {comic_list} in edition {edition}")
    set_ownership_bulk(comic_list, edition, True, name)
    return jsonify({"message": "Ownership updated successfully"})

# Route to question ownership (form)
@app.route('/question_ownership_form/<hero>')
def question_ownership_form(hero):
    return render_template('question_ownership_form.html', hero=hero)

@app.route('/question_ownership', methods=['POST'])
def question_ownership():
    data = request.get_json()  # Parse the incoming JSON request
    comic_list = data.get('comic_list')
    edition = data.get('edition')
    name = data.get('hero')
    # Validation checks
    if not comic_list or not edition:
        return jsonify({"error": "Invalid data provided"}), 400

    # Process the comic list and edition
    print(f"Checking ownership for comic: {comic_list} in edition {edition}")
    
    # Get the ownership status
    ownership_status = get_ownership(comic_list, edition, name)
    
    # Return the ownership status in the response
    if ownership_status:
        return jsonify({"message": "Ownership verified successfully", "ownership_status": "Owned"})
    else:
        return jsonify({"message": "Ownership not verified", "ownership_status": "Not Owned"})

@app.route('/get_stats/<hero>')
def get_stats_page(hero):
    stats = get_statistics(hero)
    return render_template('stats.html', stats=stats, hero=hero)

@app.template_filter('remove_static')
def remove_static_prefix(path):
    return path.split('static/', 1)[1] if 'static/' in path else path

if __name__ == '__main__':
    app.run(debug=True)
