# skribbl4me

## What is it?

skribbl4me is a command line Python tool that allows you to play the game [skribbl.io](skribbl.io) automatically.

## How does it work?

There are two parts to this project:

1. Guessing.
     - The program uses a dictionary to guess the word.
     - Words are guessed randomly at the start, and are then guessed based on the letters that have been revealed.

2. Drawing.
     - The program uses [skribbl-io-autodraw](https://github.com/galehouse5/skribbl-io-autodraw) to draw the word.
     - *This functionality is currently not implemented.*

## Disclaimer

This project is not affiliated with [skribbl.io](skribbl.io) in any way. I am not responsible for any bans, kicks or unintended consequences that may occur as a result of using this program. Use at your own risk. Please be courteous to other players, and use this program only in private games.

## How to use

1. Install the dependencies.
     - `pip install -r requirements.txt`

2. Run the setup script.
     - `python setup.py -v "<EDGE_VERSION>"`
     - Enter the version of Microsoft Edge that you are using. You can find this by going to [edge://version](edge://version) in your browser.
     - This script:
       - downloads the correct version of the [Microsoft WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
       - downloads the auto-draw extension

3. Run skribbl4me.
     - `python skribbl4me.py`
     - You will see a browser window open. Enter your details and choose your character. Join the private server you wish to join.
     - After clicking play, skribbl4me will start guessing and drawing (depending on your role).

