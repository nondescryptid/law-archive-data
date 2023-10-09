import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io
import json 
import hashlib
import os

BASE_URL = "https://www.stratatb.gov.sg"
URL = "https://www.stratatb.gov.sg/news-and-judgments/judgments/"

def hash_page_contents(url):
    contents = requests.get(url).text
    return hashlib.sha256(contents.encode('utf-8')).hexdigest()

def get_and_parse_html(url): 
    html_text = requests.get(url).text
    parsed_html = BeautifulSoup(html_text, 'html.parser')
    return parsed_html

def extract_pdf_pages(url):
    res = requests.get(url)
    pdf_text = []
    with io.BytesIO(res.content) as data:
        reader = PdfReader(data)
        num_pages = len(reader.pages)
        for page in range(num_pages):
            page_content = reader.pages[page].extract_text()
            pdf_text.append(page_content)
    return ''.join(pdf_text)

def main(): 
    cur_hash = hash_page_contents(URL)
    hash_path = "data/stb-judgments.txt"
    # Checks whether the previous hash is the same as the current hash. Writes the current hash to a text file if there is no previous hash.
    if os.path.exists(hash_path):
        with open(hash_path, 'r') as file:
            prev_hash = file.read().strip()
        if prev_hash == cur_hash: 
            print("No change in website. Exiting...")
            exit(1)
    else:
        with open(hash_path, "w") as file:
            file.write(cur_hash)

    parsed_html = get_and_parse_html(URL)
    judgments = parsed_html.find_all("div", class_="resource-card-element")
    judgment_arr = []
    json_path = "data/stb-judgments.json"

    for judgment in judgments: 
        judgment_dict = {}
        title = judgment.select("h5")[0].get_text().replace('â\x80\x93', '-').strip("...")
        # Concatenation with base URL is needed because the site uses relative links
        judgment_dict["title"] = title
        pdf_url = BASE_URL + judgment.find("a", href=True)["href"]
        judgment_dict["pdf-url"] = pdf_url
        date = judgment.find("small", class_="is-inline").get_text()
        judgment_dict["date"] = date
        try: 
            pdf_content = extract_pdf_pages(pdf_url)
        except: 
            pdf_content = "Could not extract PDF"
            print(title, "Could not extract")
        judgment_dict["pdf-content"] = pdf_content
        judgment_arr.append(judgment_dict)

    with open(json_path, "w") as file: 
        json.dump(judgment_arr, file, indent=4)

if __name__ == "__main__":
    main()