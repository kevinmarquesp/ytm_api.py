# ytm_api.py

Python script created to easely fetch data from the Youtube Music API from
command line, where I can use jq, yt-dlp and other tools to automate some
downloading process

## Install

```bash
python3 -m pip install ytmusicapi

git clone https://github.com/kevinmarquesp/ytm_api.py
cp ytm_api.py/ytm_api.py ~/.local/bin/ytm-api
rm -rf ytm_api.py

ytm-api --help
```

## Uninstall

```bash
python -m pip uninstall ytmusicapi
rm ~/.local/bin/ytm-api
```
