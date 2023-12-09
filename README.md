# Stacey Davids - Telegram bot for my Technical Support Team
#### tg: @supvsnbot

This is a Telegram bot that I created both for practice and to have fun with my support team colleagues. 
Currently it has three commands:
1. `/start` -- if a user sends this command, Stacey replies with a message with an inline keyboard that allows to choose what Stacey should do. There are currently two options that can benefit my teammates' workflow, since it sends you frequently needed info so you don't need to search for it.
2. `/help` -- this command basically lets you know how to start (to send `/start` command, of course).
3. `/all` -- this command tags everyone in the chat. **Important:** since telegram bots can't just get a list of users in a group (it is not supported in Telegram API, probably for security), the only way to gather info is to parse the updates from the users and get their nicknames and id's. In this case I did it manually, since the bot is needed only for a certain group. However, I might automatize it later. Currently, if the command is sent from anywhere else apart from our team group, no users will be tagged.

Apart from commands, the bot has a lot of 'easter eggs', such as:
- sending locally funny stickers when some certain words are present in a message (handled with the help of simple regular expressions), even if Stacey is not tagged in it;
- a funny reaction with another inline keyboard when a voice message is sent;
- a feature that allows to tag one of our teammates and call him a random nickname from a tuple with >20 options;
- a feature that allows you to ask Stacey to respond to any other message with a 'get lost, please' message. 

Also this project has a pretty nice logging system. It is not that needed for a bot that has 10 users top, but I just liked the idea and wanted to keep track of the errors and everything else that happens in the app. First I had simple 'print' logging for debugging, but when Stacey was already in a good state, I decided to make logs more consistent, precise and.. well, professional.
1. First of all, I have added a custom `conversation` logger that keeps track of the users' messages and reactions of Stacey. It has the `INFO` logging level, and the logs are sent to the console.
2. I have also configured the `root` logger to save full logs to a `root.log` file. It includes logs from all loggers that are used while the bot is running, so the resulting logs are full. However, I've set the `httpx` logger's level to `WARNING`, since I didn't need to gather all the http-requests.
3. Also I have added a custom `error_handler` to the `root` logger, that saves all errors to a separate `errors.log` file. It makes it easier to track only errors when it's needed.
4. Both `root.log` and `errors.log` files are being handled by `TimedRotatingFileHandler`. Each day at midnight new log files are created, making it easier to differentiate the days. The `backupCount` is equal to 7, so only the newest 7 log files are kept.
5. Also I started using decorators for logging.

For now this is it, thank you for reading this description :) I am planning to add some more features soon, so.. to be continued!
