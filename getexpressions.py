import requests
from bs4 import BeautifulSoup
from resources import dictionary

URL = "https://www.thoughtco.com/glossary-of-mathematics-definitions-4070804?print"
page = requests.get(URL)
# print(page.text)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="mntl-sc-page_1-0")
elements = results.find_all("p", class_="comp mntl-sc-block mntl-sc-block-html")

for element in elements:
    word = element.find("strong")
    
    if word is not None:
        word = word.text.strip()
    else:
        word = ""

    if " " not in word and word not in dictionary:
        print("adding the word " + word + " to the dictionary")
        dictionary[word] = ""
        # print(word, end="\n"*2)