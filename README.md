### A finalized version of my pomodoro bot written a while ago
## Dependencies
`pip install python-telegram-bot`
clone with submodules (depends on TokenValidityCheck!)
## Launching
`python3 pomodoro_together_bot.py <your token goes here>`
## There's a bit more
You can enable debug mode by sending `/debug <token>` to the bot
This switches minutes to seconds allowing to speedrun sessions for testing purposes
`/listsesh <token>` will list all active session names (chat_id:work|rest)
---
P.S. The only reason I finished this bot is to learn docker by putting python bot into a container
