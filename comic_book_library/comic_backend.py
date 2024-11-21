import os
import requests
import re
import json
from bs4 import BeautifulSoup

# Constants
search_urls_dog = {
    "extra": "https://www.stripovi.com/index.asp?page=search&header=0&Name=&Heroes=DD&What=HR&Publisher=LEX&ITPublisher=All&Author=All&list=on&sort=Publisher%2CNum%2CHero&cnt=All&submit=Tra%9Ei", 
    "normal": "https://www.stripovi.com/index.asp?page=search&header=0&Name=&Heroes=DD&What=HR&Publisher=LU&ITPublisher=All&Author=All&list=on&sort=Publisher%2CNum%2CHero&cnt=All&submit=Tra%9Ei",
    "gigant": "https://www.stripovi.com/index.asp?page=search&header=0&Name=&Heroes=DD&What=HR&Publisher=LUGG&ITPublisher=All&Author=All&list=on&sort=Publisher%2CNum%2CHero&cnt=All&submit=Tra%9Ei",
    "special": "https://www.stripovi.com/index.asp?page=search&header=0&Name=&Heroes=DD&What=HR&Publisher=LUSP&ITPublisher=All&Author=All&list=on&sort=Publisher%2CNum%2CHero&cnt=All&submit=Tra%9Ei",
    "almanah": "https://www.stripovi.com/index.asp?page=search&header=0&Name=&Heroes=DD&What=HR&Publisher=ALM&ITPublisher=All&Author=All&list=on&sort=Publisher%2CNum%2CHero&cnt=All&submit=Tra%9Ei"
}
search_urls_ledd = {
    "extra": "https://www.stripovi.com/index.asp?page=search&header=0&Name=&Heroes=LL&What=HR&Publisher=EXT&ITPublisher=All&Author=All&list=on&sort=Publisher%2CNum%2CHero&cnt=All&submit=Tra%9Ei", 
    "normal": "https://www.stripovi.com/index.asp?page=search&header=0&Name=&Heroes=LL&What=HR&Publisher=SD&ITPublisher=All&Author=All&list=on&sort=Publisher%2CNum%2CHero&cnt=All&submit=Tra%9Ei",
    "special": "https://www.stripovi.com/index.asp?page=search&header=0&Author=All&Name=&Heroes=ll&What=HR&Publisher=LU&ITPublisher=LU&list=on&sort=Publisher,Num,Hero&cnt=100&PageCount=1"
}
base_url = "https://www.stripovi.com/"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of app.py
output_dir_dog = os.path.join(BASE_DIR, 'static', 'dylan_dog_comics')
output_dir_ledd = os.path.join(BASE_DIR, 'static', 'lazarus_ledd_comics')
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def scrape_comics(hero = "ledd"):
    data_to_write = []
    if hero == "ledd":
        search_urls = search_urls_ledd
        output_dir = output_dir_ledd
    else:
        search_urls = search_urls_dog
        output_dir = output_dir_dog
    for type, search_url in search_urls.items():
        # Fetch search results
        response = requests.get(search_url, headers=headers)
        response.encoding = 'utf-8'
        response.raise_for_status()

        # Extract comic URLs from the search results
        if hero=="ledd":
            pattern = re.compile(r'<a href="(enciklopedija/strip/lazarus-ledd[^"]+/0/)"><img src="/im')
        else:
            pattern = re.compile(r'<a href="(enciklopedija/strip/dylan-dog[^"]+/0/)"><img src="/im')
        hrefs = re.findall(pattern, response.text)
        comic_urls = [base_url + href for href in hrefs]

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        def scrape_comic_details(url):
            # Request the comic page
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response.encoding = 'windows-1250'
            soup = BeautifulSoup(response.text, 'html.parser')

            # Scrape the comic details
            comic_info = {"url": url}

            # Get image URL
            img_tag = soup.select_one("#advanced-search-container p.pseudo-lead img")
            if img_tag:
                comic_info["image_url"] = img_tag['src']
                comic_info["title"] = img_tag['alt']
            else:
                comic_info["image_url"] = None
                comic_info["title"] = None

            # Extract comic details from the structured part of the page
            info_section = soup.select_one("#team-info")
            if info_section:
                def extract_info(tag_name):
                    tag_name = tag_name.replace("ž", "\u017E")
                    tag = info_section.find("h3", string=tag_name)
                    if tag:
                        value = tag.find_next("ul").li
                        if value and value.a:
                            return value.a.get_text(strip=True)
                        elif value:
                            return value.get_text(strip=True)
                    return None
                
                # Scrape fields
                comic_info["junak"] = extract_info("Junak")
                comic_info["izdavač"] = extract_info("Izdavač")
                comic_info["edicija"] = extract_info("Edicija/biblioteka")
                comic_info["broj"] = extract_info("Broj")
                comic_info["šifra"] = extract_info("Šifra")
                comic_info["scenarij"] = extract_info("Scenarij")
                comic_info["crtež"] = extract_info("Crtež")
                comic_info["naslovnica"] = extract_info("Naslovnica")
                comic_info["broj_stranica"] = extract_info("Broj stranica")
                comic_info["originalni_naslov"] = extract_info("Originalni naslov")
                comic_info["originalni_broj"] = extract_info("Originalni broj")

            return comic_info

        # Process each comic URL
        for comic_url in comic_urls:
            print(f"Scraping {comic_url}")
            try:
                comic_data = scrape_comic_details(comic_url)
                # Save image if it exists
                if comic_data.get("image_url"):
                    image_url = comic_data["image_url"]
                    image_filename = os.path.basename(image_url)
                    image_path = os.path.join(output_dir, type, comic_data["broj"] or "unknown", image_filename)
                    
                    if os.path.exists(image_path):
                        print("Already scraped, skipping")
                        continue
                    
                    os.makedirs(os.path.dirname(image_path), exist_ok=True)
                    img_response = requests.get(image_url, headers=headers)
                    with open(image_path, 'wb') as img_file:
                        img_file.write(img_response.content)
                    comic_data["image_path"] = image_path
                    print(f"Image saved to {image_path}")
                data_to_write.append(comic_data)
            except Exception as e:
                print(f"Failed to scrape {comic_url}: {e}")

    # Save the comic information as JSON
    json_path = os.path.join(output_dir, "info.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    if data_to_write:
        existing_data.extend(data_to_write)
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

    print(f"Data saved to {json_path}")
    print("Scraping completed.")
    
def update_ownership_dict(comic_id, owned, hero = "ledd"):
    if hero == "ledd":
        output_dir = output_dir_ledd
    else:
        output_dir = output_dir_dog
    json_path = os.path.join(output_dir, "info.json")
    new_data = []
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []
    if existing_data:
        for comic in existing_data:
            if comic["šifra"] == comic_id:
                comic["owned"] = owned
            elif comic.get("owned", None):
                pass
            else:
                comic["owned"] = False
            new_data.append(comic)
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(new_data, json_file, ensure_ascii=False, indent=4)
        
def set_ownership_bulk(comic_list, edition, owned = True, hero = "ledd"):
    if hero == "ledd":
        output_dir = output_dir_ledd
    elif hero == "dog":
        output_dir = output_dir_dog
    new_list = [f"{edition} {comic}" for comic in comic_list]
    json_path = os.path.join(output_dir, "info.json")
    new_data = []
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []
    #print("Trying to update ownership for: ", new_list)
    if existing_data:
        for comic in existing_data:
            if comic["šifra"] in new_list:
                comic["owned"] = owned
            elif comic.get("owned", None):
                pass
            else:
                comic["owned"] = False
            new_data.append(comic)
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(new_data, json_file, ensure_ascii=False, indent=4)

def get_ownership(comic_num, edition, hero="ledd"):
    if hero == "ledd":
        output_dir = output_dir_ledd
    else:
        output_dir = output_dir_dog
    comic_name = f"{edition} {comic_num[0]}"
    print("Checking ownership for comic ", comic_name)
    json_path = os.path.join(output_dir, "info.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []
    if existing_data:
        for comic in existing_data:
            if comic["šifra"] == comic_name:
                if comic.get("owned", False):
                    return True
    return False

def get_statistics(hero):
    if hero == "ledd":
        output_dir = output_dir_ledd
    else:
        output_dir = output_dir_dog
    json_path = os.path.join(output_dir, "info.json")
    data = {
        "normal":{
            "total": 0,
            "owned": 0,
            "missing": 0,
            "missing_numbers": []
        },
        "extra":{
            "total": 0,
            "owned": 0,
            "missing": 0,
            "missing_numbers": []
        },
        "almanah":{
            "total": 0,
            "owned": 0,
            "missing": 0,
            "missing_numbers": []
        },
        "special":{
            "total": 0,
            "owned": 0,
            "missing": 0,
            "missing_numbers": []
        },
        "gigant":{
            "total": 0,
            "owned": 0,
            "missing": 0,
            "missing_numbers": []
        }
    }
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []
    if existing_data:
        for comic in existing_data:
            if "LL SD" in comic["šifra"] or "DD LU" in comic["šifra"]:
                if comic.get("owned", False):
                    data["normal"]["owned"] = data["normal"]["owned"] + 1
                else:
                    data["normal"]["missing"] = data["normal"]["missing"] + 1
                    data["normal"]["missing_numbers"].append(comic["broj"])
                data["normal"]["total"] = data["normal"]["total"] + 1
            if "DD LEX" in comic["šifra"] or "LL EXT" in comic["šifra"]:
                if comic.get("owned", False):
                    data["extra"]["owned"] = data["extra"]["owned"] + 1
                else:
                    data["extra"]["missing"] = data["extra"]["missing"] + 1
                    data["extra"]["missing_numbers"].append(comic["broj"])
                data["extra"]["total"] = data["extra"]["total"] + 1
            if "DD ALM" in comic["šifra"]:
                if comic.get("owned", False):
                    data["almanah"]["owned"] = data["almanah"]["owned"] + 1
                else:
                    data["almanah"]["missing"] = data["almanah"]["missing"] + 1
                    data["almanah"]["missing_numbers"].append(comic["broj"])
                data["almanah"]["total"] = data["almanah"]["total"] + 1
            if "DD LUSP" in comic["šifra"] or "LL LU" in comic["šifra"]:
                if comic.get("owned", False):
                    data["special"]["owned"] = data["special"]["owned"] + 1
                else:
                    data["special"]["missing"] = data["special"]["missing"] + 1
                    data["special"]["missing_numbers"].append(comic["broj"])
                data["special"]["total"] = data["special"]["total"] + 1
            if "DD LUGG" in comic["šifra"]:
                if comic.get("owned", False):
                    data["gigant"]["owned"] = data["gigant"]["owned"] + 1
                else:
                    data["gigant"]["missing"] = data["gigant"]["missing"] + 1
                    data["gigant"]["missing_numbers"].append(comic["broj"])
                data["gigant"]["total"] = data["gigant"]["total"] + 1
    return data