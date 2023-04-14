## Disclaimer

* This is not intended as a production ready app, there are probably numerous security holes and sub-optimal coding practices. 
* It will charge your OpenAI account for usage. 
* I do not take responsibility for whatever abomination of a bot you can dream up. 

## Quickstart

### Requirements
* Python 3
* Open AI API Key



### Clone and Run
There are simple scripts in the parent directory to get this up and running. To clone and run immediately: 

```bash
git clone https://github.com/Square-Go/gpt-blether.git && cd gpt-blether && ./initial_setup.sh && ./run.sh
```

Or if you've already cloned just run initial_setup.sh and then run.sh.



## Making your own bots

Bots are simple to configure in plain human language. The bots are described in config.json. To create a bot, add an element to the bots list in config.json

```json {
    "bots": [
        {
            "gpt_model": "gpt-3.5-turbo",
            "bot_description": "You are the most boring man on the earth. Whenever a user inputs anything you immediately start to talk about accounting. Never break character",
            "bot_greeting": "Describe yourself!",
            "bot_name": "Boredom-AI",
        },
        ...
```



### Definitions 
* gpt-model: which version of gpt to call, this must be a chat available version. E.g. gpt-3.5-turbo. Note: gpt-4 is currently beta access only. 
* bot_description: Invisible to the user, this is the System prompt that is fed to the user to describe how it should behave. 
* bot_greeting: The first message the bot sends to greet the user.
* bot_name: The name of the bot. 
* logo_file: (Optional) custom logo file located in images directory.



### Optional: Add a logo file 

Ideal icons are perfectly square and don't need to be bigger than 100px x 100px 

To give a bot a custom logo, simply put a .png file in the images/ directory and add the logo_file element to the bot description as so:

```json
            "bots": [
        {
            "gpt_model": "gpt-3.5-turbo",
            "bot_description": "You are the most boring man on the earth. Whenever a user inputs anything you immediately start to talk about accounting. Never break character",
            "bot_greeting": "Describe yourself!",
            "bot_name": "Boredom-AI",
            "logo_file": bored.png
        },

```

