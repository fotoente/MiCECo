# MiCECo
**M**isskey **C**ustom **E**moji **Co**unter

### Introduction
This little script counts custom emojis and used reactions from the previous day and automaticaly creates a note on your Misskey account with an overview. There is also an option to include reaction emojis in the counts too.

*Example Note (with counting of Reactions activated)*: https://ente.fun/notes/8wexz5ov1q

### Installation
Clone the repository into a folder of your choice with `git clone https://github.com/fotoente/MiCECo.git`
Edit the file `example-miceco.cfg` (see table below) and save it as `miceco.cfg`

You are now ready to run the script with any Python3 version.

I recommend using a cronjob to let it run on a daily basis.
In your console type `crontab -e`
Add `0 9 * * * python3 /path/to/file/miceco.py > /path/to/file/miceco_output.txt`
The script will now be run every day on 9:00am server time.

### Options for the config file
|Name|Values|Explanation|
|----|----|----|
|instance|domain.tld|The domain name for your Misskey instance that you want to read the notes from. Only supply the domain name and TLD, no `/`,`:` or `https`
|user|`username`|The user you want to read the notes from|
|token|`String`|The token for your bot. Needs permission to write notes|
|getReaction|`Boolean`|Should reactions emojis be counted as well? `True` or `False`|

### Other notes
The script is written in a way that only the notes and reactions from yesterday(!!!) are caught and counted. There is no option currently to specify the date range for collection.

The exact timestamp to get yesterday is determined by the timezone of your server. At the moment there is no way to change the timezone.

#### Feel free to open a feature request or issue if you want something changed!
