# 📷 socialserver neo

socialserver-neo is a rewrite of [socialserver 2.x](https://www.github.com/niallasher/socialserver). Its main goal is to
actually almost maybe somewhat competent in comparison to its predecessor.

Documentation has not been written yet.

### Quickstart

- Download package
- Create venv for it
- Enter venv
- cat requirements.txt | pip install
- set ```SOCIALSERVER_ROOT``` environment variable to where you want things to get stored
- ```python3 -m socialserver devel-run``` for development, ```gunicorn socialserver``` for production
- If you want to change settings, default config is at ```$SOCIALSERVER_ROOT/config.toml```. It can be over-ridden with
  ```$SOCIALSERVER_CONFIG_FILE``` to change the location that is checked.
- If no file exists, the server will make it. If the file is missing keys the server will exit with a non-zero error 
  code.

### Notes

- Nothing here is complete
- It's all subject to change
- There is still quite a bit of jank that needs sorting
- Especially with the images.
- The images have problems.
- Not functionality problems.
- But problems nonetheless.
- Api2 isn't stable yet, and might even become api v3 to keep in line with this being major server version 3
- Yes that does kinda mean that major 2.0 just broke API compatibility instead of adding a new API, resulting in silent \
 failures for new clients.
- No I don't want that happening again.
- Also, Api1 isn't implemented in here yet either.
- Api2 is partial.
- Yeah, you can't really do much server-ing with this socialserver right now.
- No migration from 2.x -> 3.x exists yet since the current DB Schema isn't even stable
- It'll probably be available via smth like ```python3 -m socialserver migrate-2.x-db {OLD_DB_ADDR_STR}```