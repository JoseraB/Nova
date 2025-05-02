from playwright.sync_api import sync_playwright
import json
from datetime import datetime as dt
from pathlib import Path
import requests
import base64
import os
from urllib.parse import quote
from time import sleep

def encode_pdf(file_path):
    with open(file_path, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')
    return encoded_string

def get_file_size(file_path):
    return os.path.getsize(file_path)

def process_pdf(file_path):
    file_size = get_file_size(file_path)

    size_limit = 5 * 1024 * 1024  # 5 MB

    if file_size > size_limit:
        return file_path
    else:
        encoded_pdf = encode_pdf(file_path)
        return encoded_pdf

FILE_PATH = "NeoCity-Data/Neocity_Academy.json"
PDF_PATH = "NeoCity-Data/School_Profile_NEOC.pdf"

if Path(FILE_PATH).exists():
    with open(FILE_PATH, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
else:   
    os.makedirs(os.path.dirname("NeoCity-Data/"), exist_ok=True)
    data = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.osceolaschools.net/neoc")
    sleep(1)

    page.get_by_role("link", name="About").hover()
    sleep(0.5)

    #Mission School and Facts
    page.locator("#navs-835").click()
    sleep(0.5)
    for i in range(2):
        inner_html = page.locator(".Secondary_Color_Box").nth(i).inner_html()
        parts = inner_html.split("<br>")
        statement_t = parts[0].split("<strong>")[-1].split("</strong>")[0]
        statement = parts[1].strip()

        new_entry = {
            "source": {
                "site": "NeoCity Academy",
                "url": "https://www.osceolaschools.net/neoc",  # replace with actual page URL
                "scraped_at": dt.now().isoformat()
            },
            "content": {
                "type": "Mission & Vision Statement",
                "title": statement_t,
                "text": statement
            }
        }

        data.append(new_entry)

    page.get_by_role("link", name="School Profile", exact=True).click()
    sleep(0.5)
    schoolProfile_pdf = page.url

    response = requests.get(schoolProfile_pdf)
    if Path(PDF_PATH).exists():
        os.remove(PDF_PATH)
        with open(PDF_PATH, "wb") as f:
            f.write(response.content)
    else:
        with open(PDF_PATH, "wb") as f:
            f.write(response.content)

    new_entry = {
        "source": {
            "site": "NeoCity Academy",
            "url": "https://www.osceolaschools.net/neoc",
            "scraped_at": dt.now().isoformat()
        },
        "content": [
            {
                "type": "school_profile_pdf",
                "title": "School Profile PDF",
                "pdf_url": "https://www.osceolaschools.net/cms/lib/FL50000609/Centricity/Domain/835/2024-25%20School%20Profile%20NEOC.pdf",
                "pdf_base64": process_pdf(PDF_PATH)
            }
        ]
    }

    data.append(new_entry)

    page.goto("https://www.osceolaschools.net/domain/835")
    sleep(0.5)

    page.get_by_role("link", name="Fast Facts", exact=True).click()
    sleep(0.5)

    items = []
    for i in range(4):
        fast_facts_list = page.locator(".ui-article-description span span li").nth(i)
        fast_facts_text = fast_facts_list.text_content().strip()

        link = None

        a = fast_facts_list.locator("a")
        if a.count() > 0:
            link = a.get_attribute("href")
            try:
                link = fast_facts_list.locator("a").get_attribute("href")
            except:
                pass
        else:
            pass

        if link:
            fast_facts_text += f" (Source: {link})"

        items.append(fast_facts_text)

    new_entry = {
        "source": {
            "site": "NeoCity Academy",
            "url": "https://www.osceolaschools.net/neoc",
            "scraped_at": dt.now().isoformat()
        },
        "content": {
            "type": "Fast Facts",
            "title": "Fast Facts",
            "text": items
        }
    }

    #AI Pathway
    page.get_by_role("link", name="Academics and Clubs").hover()
    sleep(0.5)

    #Ai Department
    page.locator("#navs-5563").click()
    sleep(0.5)
    ai_heading = page.locator(".ui-article-description span span h2").nth(0).text_content()
    ai_paragraph = page.locator(".ui-article-description span span p").nth(0).text_content()

    ai_classes = []
    count = 3

    for i in range(2):
        page.locator(".content-accordion-toggle").nth(i).click()
        sleep(0.5)

        for j in range(count):
            ai_class_name = page.locator(".ui-article.active span").nth(j).text_content()
            ai_class_desc = page.locator(".ui-article.active p").nth(j).text_content()

            ai_classes.append({
                "class": ai_class_name,
                "description": ai_class_desc
            })

        count -= 1
        page.locator(".content-accordion-toggle").nth(i).click()
        sleep(0.5)

    new_entry = {
        "source": {
            "site": "NeoCity Academy",
            "url": "https://www.osceolaschools.net/neoc",
            "scraped_at": dt.now().isoformat()
        },
        "content": {
            "type": "AI Pathway",
            "title": ai_heading,
            "pathway_description": ai_paragraph,
            "classes": ai_classes
        }
    }

    data.append(new_entry)

    #Student Life
    page.get_by_role("link", name="Student Life").hover()
    sleep(0.5)

    #Partnerships and Experential Learning
    page.locator("#navs-6658").click()
    sleep(0.5)
    page.get_by_role("link", name="Partner With Us").click()
    sleep(0.5)

    page.locator(".icon.custom").click()
    sleep(0.5)

    project_data = []
    ai_projects = page.locator(".ui-article-overlay-content-inner").nth(2)
    p_tags = ai_projects.locator("p")
    count = p_tags.count()

    i = 0

    while i < count:
        text = p_tags.nth(i).text_content().strip()

        if not text:
            i += 1
            continue

        if p_tags.nth(i).locator("strong").count() > 0:
            title = text
            i += 1

            while i < count and not p_tags.nth(i).text_content().strip():
                i += 1
            students = p_tags.nth(i).text_content().strip() if i < count else ""
            i += 1

            img = None
            if i < count and p_tags.nth(i).locator("img").count() > 0:
                img = p_tags.nth(i).locator("img").get_attribute("src")
                i += 1

            desc_lines = []
            while i < count:
                line = p_tags.nth(i).text_content().strip()
                if not line:
                    i += 1
                    continue
                if p_tags.nth(i).locator("strong").count() > 0:
                    break
                desc_lines.append(line)
                i += 1
            
            project_data.append({
                "title": title,
                "students": students,
                "description": " ".join(desc_lines),
                "image": img
            })
        else:
            i += 1

        new_entry = {
            "source": {
                "site": "NeoCity Academy",
                "url": "https://www.osceolaschools.net/neoc",
                "scraped_at": dt.now().isoformat()
            },
            "content": {
                "type": "Projects",
                "title": title,
                "project_description": " ".join(desc_lines),
                "students": students,
                "image": "https://www.osceolaschools.net" + quote(img.strip()) if img and isinstance(img, str) else None,
            }
        }

        data.append(new_entry)
    
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    input("Press Enter to close...")