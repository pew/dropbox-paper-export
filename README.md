# TODO

* [ ] use oauth and store the creds somewhere else

# dropbox paper backup

Dropbox decided to not store *Dropbox Paper* Markdown files in Dropbox but somewhere else, so there's a need to backup these files!

# install & config

```
pip install -r requirements.txt
```

Create a Dropbox Developer App (https://www.dropbox.com/developers/apps) and generate an `Acces token`. Add this `Access token` into the python file from this repository as the `apikey` or export it as an environment variable `paperApiKey` like so:

```
export paperApiKey=ASDF1234-abc
```

# usage

```
python paper-backup.py -d ~/your/dest/folder
```

or force it, which will delete the files in the destination folder and overwrites them.

```
python paper-backup.py -f -d /your/target/folder
```

There's apparently no way to check if the (same file was already downloaded and just needs to be updated, so all your docs will be re-downloaded everytime. Sorry!
