import json
import os
import re
import requests
import sys

from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from rich.console import Console

list_tags = ["li", "dt", "dd"]
TAG_STYLES = {
    "p": "%s\n\n",
    "h1": "[#ffffff bold underline]## %s ##[/]\n",
    "h2": "[#ffffff bold underline]%s[/]\n",
    "h3": "[#ffffff bold]%s[/]\n",
    "h4": "[#ffffff italic underline]%s[/]\n",
    "h5": "[#ffffff italic]%s[/]\n",
    "h6": "%s\n",
    "aside": "[dim]%s[/]\n\n",
    "li": " [yellow]• %s[/]\n",
    "code": "%s\n\n",
    "a": "[#3b9dff underline](%i) %s[/]",
}
console = Console(highlight=False)

page_links = []
history = []


def construct_url(query):
    query_list = query.split()

    if not query.startswith("https://"):
        url = "http://www.google.com/search?q="

        for query_item in query_list:
            url += f"{query_item}+"

        return url

    return "".join(query_list)


def get_bookmarks():
    if not os.path.exists("./bookmarks.json"):
        with open("bookmarks.json", "w+") as json_file:
            json.dump([], json_file)
            return []

    with open("bookmarks.json") as json_file:
        return json.load(json_file)


def add_bookmark(arguments):
    # Check to see that no unaccepted arguments have been entered
    for argument in arguments:
        if argument not in COMMANDS["--search"]["accepted arguments"]:
            console.print(f"[red]{argument} is not a valid argument[/]")
            return

    # Check that every required argument has been passed
    for required_argument in COMMANDS["--search"]["required arguments"]:
        if required_argument not in arguments:
            console.print(
                f"[red]{required_argument} is a required argument[/]")
            return

    bookmark_url = arguments["-l"]
    bookmark_name = arguments["-n"]

    bookmark = {
        "url": bookmark_url,
        "name": bookmark_name
    }

    bookmarks.append(bookmark)

    with open("bookmarks.json", "w+") as json_file:
        json.dump(bookmarks, json_file)


def show_bookmarks(arguments):
    # Check to see that no unaccepted arguments have been entered
    for argument in arguments:
        if argument not in COMMANDS["--search"]["accepted arguments"]:
            console.print(f"[red]{argument} is not a valid argument[/]")
            return

    bookmarks_page = BookmarksPage()
    bookmarks_page.display_page()
    print()


def show_history(arguments):
    # Check to see that no unaccepted arguments have been entered
    for argument in arguments:
        if argument not in COMMANDS["--search"]["accepted arguments"]:
            console.print(f"[red]{argument} is not a valid argument[/]")
            return

    bookmarks_page = BookmarksPage()
    bookmarks_page.display_page()
    print()


def search(arguments):
    # Check to see that no unaccepted arguments have been entered
    for argument in arguments:
        if argument not in COMMANDS["--search"]["accepted arguments"]:
            console.print(f"[red]{argument} is not a valid argument[/]")
            return

    # Check that every required argument has been passed
    for required_argument in COMMANDS["--search"]["required arguments"]:
        if required_argument not in arguments:
            console.print(
                f"[red]{required_argument} is a required argument[/]")
            return

    url = arguments["-q"]

    text_only = "-to" in arguments

    web_page = WebPage(url, text_only)
    web_page.display_page()
    print()


class Page(ABC):  # Create an abstract class
    @abstractmethod
    def __init__(self):
        self.page_links = []

    @abstractmethod
    def get_page_content(self):
        pass

    def display_page(self):
        os.system("clear")

        page_content = self.get_page_content()
        console.print(page_content)


class WebPage(Page):
    def __init__(self, url, text_only):
        super().__init__()

        self.url = url
        self.text_only = text_only

        if len(history) == 0 or history[-1] != url:
            history.append(url)

    def parse_tag(self, tag):
        # This will occur if the link is standalone (i.e. not in-line)
        if tag.name == "a":
            self.page_links.append(tag.get("href"))
            return TAG_STYLES["a"] % (len(self.page_links), tag.text) + "\n\n"

        tag_content = ""
        hypertext = []
        # We only want the top-level children
        children = tag.find_all(recusive=False)

        # Get all of the in-line links (<a> tags)
        if tag.name in TAG_STYLES and children:
            # tag.find_all is used because we want this to get every child using recursive=True
            for child_tag in tag.find_all():
                if child_tag.name == "a":
                    hypertext.append(child_tag.text)
                    self.page_links.append(child_tag.get("href"))

        if tag.name in TAG_STYLES:
            tag_content = TAG_STYLES[tag.name] % tag.text

            # Loop through every in-line link, re-format it, then add it back in to the content
            for index in range(len(hypertext)):
                # Get the number of the current link (note: not the index in page_links)
                link_number = len(self.page_links) - len(hypertext) + index + 1
                new_link = TAG_STYLES["a"] % (link_number, hypertext[index])

                tag_content = tag_content.replace(hypertext[index], new_link)
        elif children:
            # Recursively call this function to parse all of the children
            for index in range(len(children)):
                child_tag = children[index]
                tag_content += self.parse_tag(child_tag)

                # Add two newlines if the child is the final list item
                if child_tag.name in list_tags and index == len(children) - 1:
                    tag_content += "\n"

        return tag_content

    def get_page_content(self):
        try:
            request = requests.get(self.url)
            soup = BeautifulSoup(request.text, "lxml")
        except:
            return "[red]This page cannot be displayed.[/]"

        body = soup.body  # Every website should have this tag
        content = ""

        for tag in body.find_all(recursive=False):
            try:
                content += self.parse_tag(tag)
            except:
                pass

        return content


class BookmarksPage(Page):
    def __init__(self):
        super().__init__()

        for bookmark in bookmarks:
            self.page_links = bookmark["url"]

    def format_bookmark(self, bookmark, bookmark_number):
        return f"[green]({bookmark_number}) {bookmark['name']}[/] [#3b9dff]\n{bookmark['url']}[/]"

    def get_page_content(self):
        content = TAG_STYLES["h1"] % "Bookmarks"

        for index in range(len(bookmarks)):
            bookmark = bookmarks[index]
            content += self.format_bookmark(bookmark, index + 1)

            if index < len(bookmarks) - 1:
                content += "\n\n"

        if len(bookmarks) == 0:
            content = "[green]You don't have any bookmarks yet! Try adding one with the -nb command[/]"

        return content


class HistoryPage(Page):
    def __init__(self):
        super().__init__()
        self.page_links = history

    def get_page_content(self):
        content = TAG_STYLES["h1"] % "History"

        for index in range(len(history)):
            link = history[index]
            content += f"[#3b9dff]({index + 1}) {link}[/]"

            if index < len(history) - 1:
                content += "\n\n"

        return content


class SearchBar:
    def parse_input(self):
        query = console.input(
            "[#5185EC]S[/][#D85040]e[/][[#5185EC]a[/][#D8BE42]r[/][#58A55C]c[/][#D85040]h[/]: ")

        if query in ["-q", "--quit"]:
            os.system("clear")
            sys.exit()

        # Replace all of the link references with the actual
        for link_reference in re.findall(r"\*\d+", query):
            link_number = int(link_reference[1:])
            query.replace(link_reference, page_links[link_number])

        # Use regex to get the command and arguments as a list
        query_list = re.split(r'\s(-\w+)', query)
        argument_list = query_list.insert(0, "-q")
        requested_function = search

        # The user is not searching without using the --search command
        if query_list[0] in COMMANDS:
            argument_list = query_list[1:]
            requested_function = COMMANDS[query_list[0]]["function"]

        # Key/value pairs for every argument
        arguments = {argument_list[index]: argument_list[index + 1]
                     for index in range(len(argument_list), 2)}

        # This is possible because python functions are first-class objects
        requested_function(arguments)


if __name__ == "__main__":
    COMMANDS = {
        "--search": {
            "function": search,
            "accepted arguments": ["-q", "-to"],
            "required arguments": ["-q"]
        },
        "--add-bookmark": {
            "function": add_bookmark,
            "accepted arguments": ["-l", "-n"],
            "required arguments": ["-l", "-n"]
        },
        "--show-bookmarks": {
            "function": show_bookmarks,
            "accepted arguments": [],
            "required arguments": []
        },
        "--show-history": {
            "function": show_history,
            "accepted arguments": [],
            "required arguments": []
        }
    }

    bookmarks = get_bookmarks()

    os.system("clear")

    search_bar = SearchBar()

    # Create an event loop, of sorts
    while True:
        search_bar.parse_input()

# Test URL 1: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#going-down
# Test URL 2: http://motherfuckingwebsite.com
# Test URL 3: https://perfectmotherfuckingwebsite.com
# Test URL 4: http://txti.es/dj8g2 (edit with code fml13)
