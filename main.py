import os
import requests
from bs4 import BeautifulSoup

TEXT_TAGS = ["p", "h1", "h2", "h3", "h4", "h5", "h6", "code"]
page_links = []


def displayPage(url):
    global page_links

    def parseTagWithoutChildren(tag):
        if tag.name in TEXT_TAGS:
            print(tag.text)
            return tag.content
        elif tag.name == "a":
            print(tag.text)
            page_links.append(tag.get("href"))
            return f"({len(page_links)}) {tag.content}\n\n"
        elif tag.name == "li":
            print(tag.text)
            return f"- {tag.content}\n\n"

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

    body = soup.body  # It's assumed that every website will have this tag
    # contents = body.children

    # print(body.find_all())

    page_content = ""

    # Recursively find all of the page content
    # for tag in contents:
    #     print(tag)
    #     page_content += parseTag(tag)

    for tag in body.find_all():
        # print(tag)
        try:
            page_content += parseTagWithoutChildren(tag)
        except:
            pass

    # print(page_content)


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

    displayPage(url)

# Test URL 1: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#going-down
# Test URL 2: http://motherfuckingwebsite.com
