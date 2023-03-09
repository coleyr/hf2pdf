# HF2PDF
A python script for downloading hello fresh recipe pdfs

## Script flags
  -A, --all             Get all recipes from hello fresh, takes 5 ever
  -o, --organize        Save all recipes in sub folders with starting letter
  -a, --any             Get recipes from hello fresh base recipe page
  -r, --recurse         Get recipe list pages from base page and get recipes from those pages
  -u URL, --url URL     A single hello fresh recipe url
  -l LIST_URL, --list_url LIST_URL
                        A hello fresh list page url with recipes EX: pasta, american, mexican, keto       
  -f FILE, --file FILE  File path to a txt file with a recipe url per line

The program relies on a argurment passed in: Try python hf2pdf -u
https://www.hellofresh.com/recipes/peppercorn-steak-w06-5857fcd16121bb11c124f383

## Example uses
Get all recipes from HF `python hf2pdf.py -A`

Get some recipes from HF recipe page `python hf2pdf.py -a`

Get some recipes from HF recipe page and all the listed category pages `python hf2pdf.py -a -r`

Get a single pdf from HF `python hf2pdf -u https://www.hellofresh.com/recipes/peppercorn-steak-w06-5857fcd16121bb11c124f383`

Get all recipes from a category page default listing ~ 15-20 `python hf2pdf -l https://www.hellofresh.com/recipes/american`
