# MiCECo
**M**isskey **C**ustom **E**moji **Co**unter

### Introduction
This little script counts custom emojis and used reactions form the day before and notes them automaticaly to Misskey. There is a option if Reactions should be counted as well.

*Example Note (with counting of Reactions activated)*: https://ente.fun/notes/8wexz5ov1q

### Installation
Clone the repository into a folder of your choice with `git clone https://github.com/fotoente/MiCECo.git`
Edit the file `example-miceco.cfg` (see table below) and save it as `miceco.cfg`

You are now ready to run the script with any Python3 Version you like.

I recommend using a cronjob to let it run on a daily basis.
In your console type `crontab -e`
Add `0 9 * * * python3 /path/to/file/miceco.py > /path/to/file/miceco_output.txt`
The script will now be run every day on 9:00am server time.

### Options in cfg
|Name|Values|Explanation|
|----|----|----|
|instance|domain.tld|Put here the domain of the Misskey instance you want to read the notes from. Only domain name and TLD, no `/`,`:` or `https`
|user|`username`|The user you want to read the notes from|
|token|`String`|The token from your bot. Needs right to write notes|
|getReaction|`Boolean`|Should reactions of yesterday be counted as well? `True` or `False`|

### Other notes
The script is written in a way that always the notes and reactions from yesterday(!!!) are caught and counted. There is no option at the moment so you can change the period.
The exact timestamp to get yesterday is determined by the timezone of your server. At the moment there is no way to change the timezone.

#### Feel free to open a feature request or issue if you want something changed!