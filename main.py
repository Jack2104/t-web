import os
import requests
import rich
from bs4 import BeautifulSoup

TEXT_TAGS = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "code"]
page_links = []


def display_page(url):
    global page_links

    def parseTagWithoutChildren(tag):
        if tag.name in TEXT_TAGS:
            return f"{tag.text}\n\n"
        elif tag.name == "a":
            page_links.append(tag.get("href"))
            return f"({len(page_links)}) {tag.text}\n\n"
        elif tag.name == "li":
            return f"  - {tag.text}\n\n"

        return ""

    def parseTag(tag):
        tag_contents = ""

        try:
            tag_children = tag.children
            child_count = len(tag_children)
        except:
            tag_contents = parseTagWithoutChildren(tag)
            return tag_contents

        for index in range(child_count):
            tag = tag_children[index]

            if (child_text := parseTagWithoutChildren(tag)) != "":
                tag_contents += child_text
            elif tag.name == "li":
                list_item = f"- {tag.content}\n" if index < child_count else f"- {tag.content}\n\n"
                tag_contents += list_item
            elif tag.children:
                tag_contents += parseTag(tag)

        return tag_contents

    os.system("clear")

    try:
        request = requests.get(url)
        soup = BeautifulSoup(request.text, "lxml")
    except:
        print("This page cannot be displayed.")
        return

    body = soup.body  # Every website should have this tag
    page_content = ""

    for tag in body.find_all():
        try:
            page_content += parseTagWithoutChildren(tag)
        except:
            pass

    print(page_content)


if __name__ == "__main__":
    os.system("clear")

    query = input("Search: ")
    search_terms = query.split()
    search_term_count = len(search_terms)

    url = ""

    if query.startswith("http"):
        url = query.join(search_terms)
    else:
        url = "https://www.google.com/search?q="

        for index in range(search_term_count):
            word = search_terms[index]

            url += word + "+" if index < (search_term_count - 1) else word

        url

    display_page(url)

# Test URL 1: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#going-down
# Test URL 2: http://motherfuckingwebsite.com
# Test URL 3: https://perfectmotherfuckingwebsite.com
