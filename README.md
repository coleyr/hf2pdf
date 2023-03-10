# HF2PDF
A python script for downloading hello fresh recipe pdfs

## Script flags
Takes Hello Fresh Recipe URL's and converts them to pdfs

  -h, --help            show this help message and exit

  -A, --all             Get all recipes from hello fresh, takes 5 ever, will organize by first letter by default

  -do, --dont_organize  Used with A/all param, Don't organize all recipes into sub folders with starting letter (a,b,c...)

  -o DOWNLOAD_FOLDER, --download_folder DOWNLOAD_FOLDER
                        Download folder location, relative path from script EX: ./pdfs or ./downloads/ketorecipes

  -a, --any             Get recipes from hello fresh base recipe page

  -r, --recurse         used with all or list flags, Get recipe list pages from base page and get recipes from other list pages on that page

  -u URL, --url URL     A single hello fresh recipe url EX: https://www.hellofresh.com/recipes/squash-asparagus-medley-with-lemon-herb-creme-fraiche-63f62d08851013c088050a34

  -l LIST_URL, --list_url LIST_URL
                        A hello fresh list page url with recipes EX: https://www.hellofresh.com/recipes/chicken-recipes

  -f FILE, --file FILE  File path to a txt file with a recipe url per line

The program relies on a argurment passed in: Try python hf2pdf -u
https://www.hellofresh.com/recipes/peppercorn-steak-w06-5857fcd16121bb11c124f383

## Example uses
Get all recipes from HF `python hf2pdf.py -A`

Get recipes from a list page and save them to unique folder `python .\hf2pdf.py -l https://www.hellofresh.com/recipes/chicken-recipes -o ./mychicken_recipes`

Get some recipes from HF recipe page `python hf2pdf.py -a`

Get some recipes from HF recipe page and all the listed category pages `python hf2pdf.py -a -r`

Get a single pdf from HF `python hf2pdf -u https://www.hellofresh.com/recipes/peppercorn-steak-w06-5857fcd16121bb11c124f383`

Get all recipes from a category page default listing ~ 15-20 `python hf2pdf -l https://www.hellofresh.com/recipes/american`
