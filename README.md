# clients
Various clients for various APIs (Freebox, Subsonic, Slack, ...)

[SLACK]
The slack client retrieves history for all Slack channels and writes it in a file.
There is one file per channel.
Edit the script to add your Slack Token (can be found @ https://api.slack.com/web) and modify the path where the logs are written.
10000 messages roughly take ~30M of disk space.
