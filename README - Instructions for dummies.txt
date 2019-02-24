Installation instructions for dummies/non-technical people:

1. Download Python 3.7 at https://www.anaconda.com/distribution/#download-section. Be sure to pick the correct operating system/bit type.
2. Go through the installations with default options.
3. Search for "Anaconda Prompt" on your computer, and on the command line type in "python --version" to confirm that your version of Python is at least 3.
4. Go to https://github.com/jeroenmeulenaar/python3-mega, click on clone or download -> download, and unzip to a directory.
5. Using the directory you unzipped it to, type in "cd <DIRECTORY PATH>", press enter, and type in "pip install -r requirements.txt". Once this is done running, run "python setup.py". Note that if this step fails due to permissions errors (likely because you installed Anaconda for all users instead of just yourself), you would need to right click on Anaconda Prompt and run as admin.
6. Type in "cd <WHEREEVER YOU UNZIPPED THIS PROGRAM TO>". Press enter, type in "cd booruMirror", then type in "python booruMirror.py". If there are any errors of the form "No module named '<MODULE NAME>'", type in "pip install <MODULE NAME>", then try again.
7. Once you see "Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)", open your favorite web browser and type in 127.0.0.1:5000. You should be redirected to the proper page.