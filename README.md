<div align="center">
    <img src="socialserver/static/logo256.png" style="width:64px;margin-top:12px;margin-bottom:5px;"/>
    <h1 style="margin-top:0;margin-bottom:5px;">socialserver</h1>
</div>

The server side of an open shurce social media platform. This is a rewrite of a previous implementation, that adds a new
API, and many more features, including actually being stable (eventually), actually working properly (eventually), being
easy to deploy and work with (eventually), and being far more maintainable.

In the early stages of development currently, and there isn't much (read: any) in the way of documentation right now.

---

### Quickstart

This project uses pipenv for dependency management, so you'll want to have it installed.

- Clone the repository
- Run `pipenv install` to install dependencies
- Set ``SOCIALSERVER_ROOT`` in your environment, to define the folder you want server data stored in.
  - If unset, the default is `$HOME/socialserver`.
- Run `pipenv run devel` for a development server.
  -  Any WSGI server *should* work fine. Gunicorn is a good choice for when you're ready to move away from the Flask dev server.
- A configuration file will be placed at `$SOCIALSERVER_ROOT/config.toml`.
  - You can overwrite this location by setting `SOCIALSERVER_CONFIG_FILE` in your environment.
- ???
- Profit

### Tests

Run `pipenv run tests`. Or `pytest socialserver`.

### Notes

- There is no proper way to create an admin user, due to the initial setup not being done yet. For now, you can
  run ```python3 -m socialserver mk-user```. This will allow you to create a user with the administrator attribute.
    - If you're using the Pipenv setup, you'll want to use pipenv shell first, to ensure all dependencies are available.
    - It's a pretty sketchy little script, and will be replaced in the future.
