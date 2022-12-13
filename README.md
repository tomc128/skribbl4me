# skribbl4me

## What is it?

skribbl4me is a Python tool that allows you to play the game [skribbl.io](skribbl.io) automatically.

## Disclaimer

This project is not affiliated with [skribbl.io](skribbl.io) in any way.

I am not responsible for any bans, kicks or unintended consequences that may occur as a result of using this program. Use at your own risk.

Only use this program in private games. Using it in public games is unfair to other players.

## How does it work?

There are two parts to this project:

1. skribbl4me.
   - This is the main program that controls the browser and interacts with the game.
   - It uses a dictionary to guess the word.
   - Words are guessed randomly at the start, and are then guessed based on the letters that have been revealed.
   - It uses [skribbl-io-autodraw](https://github.com/galehouse5/skribbl-io-autodraw) to draw the word.
     - *This functionality is currently not implemented.*

2. scrape4me.
   - This is a separate program that scrapes the [skribbl.io](skribbl.io) website for words.
   - This bot plays against itself and records the word choices that it is given.

## How to use

1. Install the dependencies.
     - `pip install -r requirements.txt`

2. Run the setup script.
     - `python setup.py <browser> -v <version> -p <platform>`
     - Enter the browser you wish to use, currently `edge` and `chrome` are supported.
     - Enter the version of the broweser that you are using. You can find this by going to [chrome://version](chrome://version) in your browser.
     - Enter the platform that you are using. This is either `win32` or `win64`. Linux and Mac are not yet supported.
     - This script:
       - downloads the correct WebDriver version for your browser
       - downloads the auto-draw extension

3. Run skribbl4me.
     - `cd skribbl4me; python main.py`
     - Ensure your CWD is the inner skribbl4me directory.
     - A window will open, click `Initialise & Launch`.
     - You will see a browser window open. Enter your details and choose your character. Join the private server you wish to join.
     - You will also see the main window open. Click `Start` or `Stop` to control the status of the skribbler bot.

