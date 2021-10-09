# 2x2-bot
Repository for the backend code being used by the 2x2 Twitter bot.

# TODO
* The function is taking a long time, mostly from downloading the photo from S3. I am not too concerned because the function runs very infrequently. I would still like to see if I can shorten execution time.
* I would like the triggering event to automatically pause the schedule if it detects there are no unposted entries in the database.
* Create scripts that upload the photo to S3 and add a corresponding entry to the database.
* Develop a web app front-end to view what is in the database quickly and upload new squares.
* Develop a mobile app that scans, crops, and uploads to the database.
