# soggy-dl

An image downloader/crawler for the webcomic "Soggy Cardboard."

This comic has a couple challenges to it. But far and away the biggest one is
that it has a 'time reset' where the 'chapter' numbering starts over at 1 again
following chapter 220. And the filename format did not change, so I would have
had to manually rename each file I downloaded if I did it manually.

Also, I hadn't done it before, and I wanted to try writing a scraper in Python.

I didn't even consider searching for existing scrapers; I just made my own.

In the process I wrote some decent argument parsing code (I don't really care
for argparse... it just never made sense to me).

Usage:

    ./soggy-dl.py --many=<depth back in time to traverse> <starting comic page url's>
    
If `--many=<n>` is not provided, no recursion will be performed (only the
current page will be downloaded). Multiple starting points can be provided.
If you provide two URL's, one for chapter 5 and one for chapter 20, and use
`--many=5`, it will download chapters 1 through 5 and 15 through 20.

The filenames are output in the format
`<epoch>.<chapter#> - Title.<file extension>`. Currently, all images save one
appear to be in PNG format.

Have fun! Please don't abuse it!

Licensed under GNU General Public License, Version 3. See `LICENSE` file for
details.
