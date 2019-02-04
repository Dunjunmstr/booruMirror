# booruMirror
A utility written in Python 2.7 utilizing Flask, HTML, and Javascript to mirrors imageboards locally, allowing for users to customize their searches and execute searches based on their own computing power, not through subscription-based throttling. Currently only supports Danbooru; a WIP.

# Usage
The directory structure is still a WIP, and tests don't quite work yet, but for now the basic functionality should work. From the booruMirror directory, run:

```
python booruMirror.py
```

There may be several dependencies; please use pip to install them, with python -m pip install <packageName>. 
  
# Searching
Searching works as it does on most booru instances, and spaces in between elements defaults to "and", so:

```
scenery snow
```

...but at the moment it is only possible to search for tags. However, common unary and binary operations are supported by using backticks (\`) to escape the operations. For example:

```
`(`(scenery `| `!snow `) `^ potato `)
```

finds all images with (either "scenery" or no "snow" or both) or "potato", but not both.

(For those wondering why escaping is necessary, apparently some image tags use these characters, like ":)" or "!!". Backticks seem to be unused so far.

# Options
It is possible to specify several parameters: the safety-rating, tags, images displayed per page, and page are all standard options from booru-based imageboards (though the first of these is not as easily accessible). It is also possible to permit direct links--that is, all links to images will take the user to the full-sized image, not the default booru page. This is convenient for downloading or opening images en masse, in case the user is trying to select an image out of several choices and wants to keep a record of what they have seen.

# To do:

1. Figure out how to use Javascript, clean up the code, and figure out what Flask vs Javascript ratio should be. Some of the hard-coding is particularly nasty styling.
2. Fix up the caching. At the moment, this program caches everything rather inefficiently (It seems to thrash a bit after only a few searches), and searches inefficiently too. Search times can be cut down to at least half.
3. Attempt reworking the tag parser to fetch from a sql database as opposed to a pandas dataframe. 
4. Refactor to potentially support other imageboards.
5. Fix up the tests and figure out how to write the tests so that they're actually runnable according to industry standard.
