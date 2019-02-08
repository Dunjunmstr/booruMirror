# booruMirror
A utility written in Python 2.7 utilizing Flask, HTML, and Javascript to mirrors imageboards locally by iterating through their entire database and grabbing everything it sees. This allows for users to customize their searches and execute searches based on their own computing power, not through subscription-based throttling. Currently only supports Danbooru (The API seems positively worthless, which makes this approach perfect); a WIP.

# Usage
The directory structure is still a WIP, and tests don't quite work yet, but for now the basic functionality should work. From the booruMirror directory, run:

```
python booruMirror.py
```

# Dependencies
So far, dependencies include mega (https://pypi.org/project/mega.py/), numpy/scipy, and Flask. Please use pip to install them, with python -m pip install <packageName>. 
 
Note that, with the most recent upgrade to pip 19.0.1, mega no longer seems to be hosted as a repository. Until this issue gets resolved, please download the zip from https://puu.sh/CIUCN/37c4933f60.zip and place it into your python installation's Lib/site-packages directory. There may be some more packages to install, though they should be readily available via pip.
  
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

# Notes
The future of this repo's still a bit unclear: it can either support just Danbooru, expand to other imageboards, or both.

# Immediate goals

1. Figure out how to use Javascript, clean up the code, and figure out what Flask vs Javascript ratio should be. Some of the HTML/Java hard-coding has some particularly nasty styling.
2. <s>Fix up the caching. At the moment, this program caches everything rather inefficiently (It seems to thrash a bit after only a few searches), and searches inefficiently too. Search times can be cut down to at least half.</s> Mostly done; search times are probably still at least half as slow as Danbooru, but there's no network overhead or potential timeouts from cache misses.
3. <s>Attempt reworking the tag parser to fetch from a sql database as opposed to a pandas dataframe.</s> Complete, but apparently there isn't all that much of a speedup. Tentatively using both methods until I figure out which one's faster.

# General goals

1. Refactor to potentially support other imageboards if there's enough interest. Ideas include SankakuComplex (4 tag limit), Behoimi (2 tag limit), and Pixiv (because apparently they actually do index their images, but it might be a bit challenging to go through 80 million images). Ideas do NOT include Gelbooru (because it's just Danbooru with more smut and surprisingly no tag limit, rendering support semi-pointless), Safebooru (because it's supposedly just danbooru with a safe wrapper on it but it doesn't actually filter out any of the smut because safe is a useless classification), and most smut boorus (because oof).
2. Just refactoring in general. Testing things informally's made this repo laden with technical debt; starting to have trouble finding where everything is.
3. Fix up the tests and figure out how to write the tests so that they're actually runnable according to industry standard.

# Danbooru-specific goals

1. Add in support for pools. On one hand, there are currently less than 20000 pools, which makes an indexing compilable in a reasonable amount of time. On the other hand, they're quite worthless and there's no convenient updating scheme for them since they don't update linearly.
2. Add in support for user uploads and favorites. As of this writing, there are 600k users, half of which are empty, but analysis of the user pool could be interesting: it might be possible to generate a user similarity graph, where you can specify your username and find users with similar favorite pools as you do, or have an "other users also liked" feature a la SankakuChannel. Again, this is theoretically parsable, but may dozens of times more time to parse compared to parsing the entire database (which takes 5 hours at the time of this writing) due to the sheer number of page visits required (120 million users, each with a list of favorites; there's a 1-1 relation with the number of uploads, but the favorites is probably more interesting as a whole). 
