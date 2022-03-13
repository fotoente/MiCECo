# MiCECo
**M**isskey **C**ustom **E**moji **Co**unter

### Introduction
This little script counts custom emojis and used reactions from the previous day and automaticaly creates a note on your Misskey account with an overview. There is also an option to include reaction emojis in the counts too.

*Example Note (with counting of Reactions activated)*: https://ente.fun/notes/8wexz5ov1q

### Installation
Clone the repository into a folder of your choice with `git clone https://github.com/fotoente/MiCECo.git`
Edit the file `example-miceco.cfg` (see table below) and save it as `miceco.cfg`

Install following Python packages via `pip install`
```
emoji
configparser
requests
```

or use `pip install -r requirements.txt` in the cloned folder

You are now ready to run the script with any Python3 version.

I recommend using a cronjob to let it run on a daily basis.
In your console type `crontab -e`
Add `0 9 * * * python3 /path/to/file/miceco.py > /path/to/file/miceco_output.txt`
The script will now be run every day on 9:00am server time.

### Available flags
There are two flags that can be used to specify which external files the script gonna use

| Flag | Long name   | controlled behaviour                                                                     |
|------|-------------|------------------------------------------------------------------------------------------|
| `-c` | `--config`  | What configuration file should be used.<br/>Without this flag `miceco.cfg` will be used. |
 | `-i` | `--ignored` | Which emojis should be ignored.<br/> Without this `ignoredemojis.txt` will be used       |

### Options for the config file
| Name           | Values     | Explanation                                                                                                                                                       |
|----------------|------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| instance       | domain.tld | The domain name for your Misskey instance that you want to read the notes from. Only supply the domain name and TLD, no `/`,`:` or `https`                        |
| user           | `username` | The user you want to read the notes from                                                                                                                          |
| token          | `String`   | The token for your bot. Needs permission to write notes                                                                                                           |
| getReaction    | `Boolean`  | Should reactions emojis be counted as well? `True` or `False`                                                                                                     |
| ignoreEmojis   | `Boolean`  | Should Emojis that are specified in `ignoredemojis.txt` be ignored? `True`or `False`                                                                              |                                                        |
| noteVisibility | `String`   | How should the note be shown in the Timeline? `public`: Visible for everyone<br/>`folowers`: only visible for your followers<br/>`specified`: Only you can see it |

### Other notes
The script is written in a way that only the notes and reactions from yesterday(!!!) are caught and counted. There is no option currently to specify the date range for collection.

The exact timestamp to get yesterday is determined by the timezone of your server. At the moment there is no way to change the timezone.

If the note is longer than the maximum note length of the instance, then only the five most used emojis (and five most used reactions) will be shown.
