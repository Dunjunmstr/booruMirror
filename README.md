# booruMirror
A utility written in Python 3.7 (Originally in 2.7 and hastily migrated to 3.7) utilizing Flask, HTML, and Javascript to mirror imageboards locally by iterating through their entire database and grabbing everything it sees. This allows for users to customize their searches and execute searches based on their own computing power, not through subscription-based throttling. Currently only supports Danbooru (The API seems positively worthless, which makes this approach perfect); a WIP.

# Usage
The directory structure is still a WIP, and tests don't quite work yet, but for now the basic functionality should work. From the booruMirror directory, run:

```
python booruMirror.py
```

# Dependencies
So far, dependencies include mega (https://pypi.org/project/mega.py/), numpy/scipy, pandas, and Flask. Please use pip to install them, with python -m pip install <packageName>. 
 
Note that, with the most recent upgrade to Python 3.7, mega no longer seems to be hosted as a repository. Until this issue gets resolved, please follow the installation instructions from https://github.com/jeroenmeulenaar/python3-mega.
  
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

# Regarding benchmarks
There were 3 approaches used to parse tags, which we will call the TagParser approach, the Lambda (actually closure) approach, and the pure SQL query approach. The TagParser simply relied on the built in computational ability of the TagParser class, the Lambda approach forked off of the TagParser approach but relied on a lambda function to cache all of its single tag searches and only stored the indices being stored, and the pure SQL query relied on the TagParser to generate a SQL query that could be run to obtain the relevant images.

For benchmarks, we ran 4 searches, using the permutations of 1girl and highres, two of the most popular tags. The initial batch of benchmarks gave the following results:

```
1girl highres
Lambdas: 5.1012
TagParser: 2.898
SQL: 14.410088777542114

highres
Lambdas: 1.4332771301269531
TagParser: 2.2986559867858887
SQL: 14.62399697303772

1girl `| highres
Lambdas: 1.3604545593261719
TagParser: 5.102830648422241
SQL: 22.014472723007202

1girl 
Lambdas: 1.981278657913208
TagParser: 2.7778806686401367
SQL: 18.63368320465088
```

Despite being a supposed improvement over the TagParser approach, the SQL queries actually took the longest time of all. What wasn't explained was why the TagParser approach seemed to be doing better than the closure approach. However, a subsequent search removing the SQL benchmarking and switching around the order gave us a better understanding of what was happening:

```
Highres
Lambdas: 2.4194769859313965
TagParser: 2.321817398071289

1girl
Lambda: 2.6393070220947266
TagParser: 2.5156710147857666

1girl `| highres
Lambda: 0.015957593917846680
TagParser: 5.008820056915283

1girl highres
Lambda: 0.008976221084594727
TagParser: 2.731323003768921
```
It seemed that the caches were being contaminated with the SQL queries, resulting in cache misses for the Lambda approach. Removing the SQL query from the picture helped immensely.

It is worth noting that only the amortized runtime for the cached approach is better. So, if we were to switch around the order:
```
1girl highres
Lambda: 5.527900457382202
TagParser: 2.7200350761413574
1girl
Lambda: 0.013966083526611328
TagParser: 2.7327754497528076
1girl `| highres
Lambda: 0.02194046974182129
TagParser: 5.248839616775513
1girl
Lambda: 0.011994600296020508
TagParser: 2.3438191413879395
```
Not a pretty result for the first search, but many people like to reuse the results of their cache searches, so definitely a tradeoff worth keeping. 

It's also worth that the speedup actually reverses in extreme cases. Searching through a glut of artists (212 artists in total) took 456 seconds for the Lambda approach and 475 seconds for the TagParser approach, presumably due to set/dataframe operations resulting in a significant overhead in these cases, and the former outperforming the latter.

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
4. (Distant future) Use feature branches rather than committing directly to the master

# Danbooru-specific goals

1. Add in support for pools. On one hand, there are currently less than 20000 pools, which makes an indexing compilable in a reasonable amount of time. On the other hand, they're quite worthless and there's no convenient updating scheme for them since they don't update linearly.
2. Add in support for user uploads and favorites. As of this writing, there are 600k users, half of which are empty, but analysis of the user pool could be interesting: it might be possible to generate a user similarity graph, where you can specify your username and find users with similar favorite pools as you do, or have an "other users also liked" feature a la SankakuChannel. Again, this is theoretically parsable, but may dozens of times more time to parse compared to parsing the entire database (which takes 5 hours at the time of this writing) due to the sheer number of page visits required (120 million users, each with a list of favorites; there's a 1-1 relation with the number of uploads, but the favorites is probably more interesting as a whole). 
