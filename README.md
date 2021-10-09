# 2x2-bot
Repository for the backend code being used by the 2x2 Twitter bot.

# TODO
* The function is taking a long time, mostly from downloading the photo from S3. I am not too concerned because the function runs very infrequently. I would still like to see if I can shorten execution time.
* I would like the triggering event to automatically pause the schedule if it detects there are no unposted entries in the database.
