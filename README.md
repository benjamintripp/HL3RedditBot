HL3RedditBot
============

Quickly done reddit bot to respond to reddit posts with numbers in the title with a comment saying HL3 is confirmed


Current implementation is to have the bot run every 30 minutes getting the top 30 posts from r/gaming. Posts that are commented on are stored in a database. There is also a script that is designed to be run weekly to clean up week old post ids from the table.


This was written to be run as a cron job on the shared web host I have, so there are a few design choices that are forced due to limiations on the host. 

__Bot in action:__
http://www.reddit.com/user/hl3confirmedbot


Dependencies
============
PRAW - https://github.com/praw-dev/praw

PyMySQL - https://github.com/petehunt/PyMySQL
