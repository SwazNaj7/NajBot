# NajBot

NajBot is a Discord bot built using the discord.py library. It includes various features such as welcoming new members, warning system, and more.

## Features

- Welcome new members to the server
- Warn members and keep track of warnings
- Display member avatars
- Various fun commands like 8ball
- Administrative commands like kick, ban, mute, and unmute

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/NajBot.git
    cd NajBot
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt

3. Enter your discord bot token at the bottom of the file:
```py
client.run('')
```

4. Run the bot:
```sh
python discordbot.py

## Commands

- `.ping`: Check the bot's latency.
- `.avatar [member]`: Display the avatar of a member.
- `.warn [member] [reason]`: Warn a member.
- `.warnings [member]`: Display warnings of a member.
- `.snipe`: Snipe the last deleted message.
- `.help`: Display help for commands.