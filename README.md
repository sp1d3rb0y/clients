# clients
Various clients for various APIs (Freebox, Subsonic, Slack, ...)

[SLACK]
The slack client retrieves history for all Slack channels and writes it in a file.
There is one log file per channel, and one hidden file per channel for storing the timestamp of the last retrieved message.
Edit the script to add your Slack Token (can be found @ https://api.slack.com/web) and modify the path where the logs are written.
10000 messages roughly take ~1M of disk space.
Use -v argument for verbose mode.
Example of cron line to retrieve new messages every hour :
0 */1 * * * python ~/slack-history-retriever.py -v >> ~/slack-history.log