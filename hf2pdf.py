import requests
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import re
import urllib.request
import threading
import json

# Step one get url for HF recipe
parser = argparse.ArgumentParser(
    prog='Hello Fresh To PDF',
    description="Takes Hello Fresh Recipe URL's and converts them to pdfs",
    epilog='The program relies on a argurment passed in: Try python hf2pdf -u https://www.hellofresh.com/recipes/peppercorn-steak-w06-5857fcd16121bb11c124f383')
parser.add_argument("-A", "--all", help="Get all recipes from hello fresh, takes 5 ever, will organize by first letter by default", action='store_true')
parser.add_argument("-do", "--dont_organize", help="Used with A/all param, Don't organize all recipes into sub folders with starting letter (a,b,c...)", action='store_false', default=True)
parser.add_argument("-o", "--download_folder", help="Download folder location, relative path from script EX: ./pdfs or ./downloads/ketorecipes")
parser.add_argument("-a", "--any", help="Get recipes from hello fresh base recipe page", action='store_true')
parser.add_argument("-r", "--recurse",
                    help="used with all or list flags, Get recipe list pages from base page and get recipes from other list pages on that page", action='store_true')
parser.add_argument("-u", "--url", help="A single hello fresh recipe url EX: https://www.hellofresh.com/recipes/squash-asparagus-medley-with-lemon-herb-creme-fraiche-63f62d08851013c088050a34")
parser.add_argument("-l", "--list_url", help="A hello fresh list page url with recipes EX: https://www.hellofresh.com/recipes/chicken-recipes")
parser.add_argument("-f", "--file", help="File path to a txt file with a recipe url per line")
# TODO
# parser.add_argument("-s", "--search", help="Will download pdfs from results of hello fresh search query EX: squash")
args = parser.parse_args()


class HF2PDF():
    recipe_link_regex = re.compile(r"^https:\/\/www.hellofresh.com\/recipes\/([a-z-]+?\S+\d\S*)", re.IGNORECASE)
    recipe_group_regex = re.compile(r"^https:\/\/www.hellofresh.com\/recipes\/((?!d)|[a-z-])+$", re.IGNORECASE)
    site_map_directory_a_z_regex = re.compile(r"^https:\/\/www.hellofresh.com\/pages\/sitemap\/recipes-[a-z]$", re.IGNORECASE)
    weird_name_regex = re.compile(r"(\d[a-z]*\d[a-z]*\d)", re.IGNORECASE)

    def __init__(self, state_path="state.json", threads: int=10, download_folder="./pdfs",):
        self.state_path = Path(state_path)
        self.threads = threads
        self.download_folder = self.make_download_folder(download_folder)
        self.recipe_group_pages_checked = set()
        self.load_state()
    def __str__(self):
        return f"{self.__class__.__name__}({self.state_path}, {self.threads}, {self.download_folder})"
    
    def __repr__(self):
        return self.__str__()

    @staticmethod
    def make_download_folder(download_folder, update_path=False):
        p = download_folder if update_path else Path(download_folder)
        p.mkdir(parents=True, exist_ok=True)
        return p
    
    @staticmethod
    def random_name():
        return str(object().__hash__())
    
    def download_link_check(self, link, file_type=".pdf"):
        return bool(link and len(link) > 5 and link[-4:] == file_type)

    def recipe_link_check(self, link):
        return bool(link and self.recipe_link_regex.search(link) and link not in self.previous_downloaded_url)

    def recipe_category_check(self, link):
        return bool(link and self.recipe_group_regex.search(link))
    
    def recipe_letter_page(self, link):
        return bool(link and self.site_map_directory_a_z_regex.search(link))
    
    def load_state(self):
        if not self.state_path.exists():
            self.previous_downloaded_url = set()
            return
        text = self.state_path.read_text()
        self.previous_downloaded_url = set(json.loads(text)['recipe_links'])

    def _get_urls_from_file(self, filepath: str):
        p = Path(filepath)
        if not p.exists():
            print(f"No file found for path: {filepath}")
            return []
        filetext = p.read_text()
        return filetext.splitlines()

    def _get_html(self, url: str,  html_returned=None, params={},):
        header = {
            'User-Agent': 'Python hf2pdf',
            'Accept': '*/*'
        }
        r = requests.get(url, params=params, headers=header)
        print(f"Getting html from page -> link url: {r.url}")
        if r.status_code != 200:
            print(f"The following url could not be reached: {url} \nError Code {r.status_code}")
            return ""
        if html_returned is None:
            return r.text
        html_returned.append(r.text)

    def split_list(self, my_list: list, start=None, end=None, step=None):
        start = start or 0
        end = end or len(my_list)
        step = step or 10
        for i in range(start, end, step):
            x = i
            yield my_list[x:x+step]

    def single_function_thread(self, urls, funct, funct_args=(), funct_kwargs={}, return_type=list, return_kwarg=None, start=None, end=None):
        '''Must use a function with kwargs, the first arg must be the item in the list'''
        chunked_list = self.split_list(list(urls), start=start, end=end, step=self.threads)
        returned_values = []
        for chunk in chunked_list:
            threads = []
            returned_value = return_type()
            kwarg = {return_kwarg: returned_value} if return_kwarg else {}
            kwarg.update(funct_kwargs)
            for url in chunk:
                t = threading.Thread(target=funct, args=(url, *funct_args), kwargs=kwarg,)
                threads.append(t)
                t.start()
            for thread in threads:
                thread.join()
            returned_values.extend(returned_value)
        yield from returned_values

    def _get_download_link(self, html_list):
        for html in html_list:
            print("Getting Download Link")
            soup = BeautifulSoup(html, 'html.parser')
            yield from self._get_links(soup, self.download_link_check)

    def _get_links(self, soup, link_check) -> str:
        links = soup.find_all('a')
        for link in links:
            link = link.get('href')
            if link_check(link):
                yield link

    def get_links_from_page(self, list_url, check_type):
        html = self._get_html(list_url)
        soup = BeautifulSoup(html, 'html.parser')
        yield from self._get_links(soup, check_type)

    def make_name(self, url:str):
        # Removes Url up to recipe name
        name = url.split("/")[-1]
        # Remove weird numbers
        name = [name for name in name.split('-') if not self.weird_name_regex.search(name)]
        name = name or [self.random_name()]
        name = "_".join(name)
        return f"{name}.pdf"

    def download_by_url(self, url):
        name = self.make_name(url)
        print(f"Downloading recipe: {name}")
        fp = self.download_folder / name
        urllib.request.urlretrieve(url, fp)

    def _execute_gen_with_no_return(self, gen):
        try:
            next(gen)
        except StopIteration:
            return
        self._execute_gen_with_no_return(gen)
    def _update_state(self):
        hf.state_path.write_text(json.dumps({'recipe_links': list(self.previous_downloaded_url)}))

    def download_from_links(self, recipe_links):
        recipe_page_html = self.single_function_thread(
        recipe_links, self._get_html, return_kwarg="html_returned",  funct_kwargs={'params': {}})
        dl_links = set(self._get_download_link(recipe_page_html))
        gen = self.single_function_thread(dl_links, self.download_by_url)
        self._execute_gen_with_no_return(gen)
        self.previous_downloaded_url.update(recipe_links)
        self._update_state()

    def get_recipe_links_from_page(self, recipe_url: str="https://www.hellofresh.com/recipes", recurse_list_pages=False):
        print(f"Getting recipes from page {recipe_url}")
        recipe_links = self.get_links_from_page(recipe_url, self.recipe_link_check)
        list_pages = set(self.get_links_from_page(recipe_url, self.recipe_category_check))
        for recipe_link_chunks in self.split_list(list(recipe_links), step=self.threads):
            self.download_from_links(recipe_link_chunks)
        if not recurse_list_pages:
            return
        for list_page in list_pages - self.recipe_group_pages_checked:
            self.recipe_group_pages_checked.add(list_page)
            self.get_recipe_links_from_page(list_page)

    # def get_recipes_from_search(self, search_query:str):
    #     print(f"Fetching recipes from search {search_query}")
    #     self.get_recipe_links_from_page(f"https://www.hellofresh.com/recipes/search?q={search_query}")

    def get_all_recipes(self, organize):
        print(f"Getting all recipes")
        list_pages = set(self.get_links_from_page('https://www.hellofresh.com/pages/sitemap', self.recipe_letter_page))
        top_path = self.download_folder
        for list_page in list_pages - self.recipe_group_pages_checked:
            if organize:
                self.download_folder = self.make_download_folder(top_path / list_page[-1], update_path=True)
            self.recipe_group_pages_checked.add(list_page)
            self.get_recipe_links_from_page(list_page)

if __name__ == "__main__":
    hf = HF2PDF(download_folder=args.download_folder) if  args.download_folder else HF2PDF()
    if args.any:
        hf.get_recipe_links_from_page()
    urls = []
    if args.file:
        urls.extend(hf._get_urls_from_file(args.file))
    if args.url:
        urls.append(args.url)
    if urls:
        hf.download_from_links(urls)
    if args.list_url:
        hf.get_recipe_links_from_page(args.list_url, args.recurse)
    if args.all:
        hf.get_all_recipes(args.dont_organize)
    #TODO
    # if args.search:
    #     hf.get_recipes_from_search(args.search)

