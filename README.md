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

- Clone repository
- Install dependencies (use a virtual environment.)
- Set the ```SOCIALSERVER_ROOT``` environment variable to the folder you want server data stored in. The default is
  ```$HOME/socialserver```.
- ```python3 -m socialserver devel-run``` for development. Otherwise just point some WSGI server at the
  ```socialserver``` module and you're good to go.
- Configure ```$SOCIALSERVER_ROOT/config.toml``` to your liking. Config location can be over-ridden with the
  ```SOCIALSERVER_CONFIG_FILE``` environment variable.
- ???
- Profit

### Tests

The test suite is written using pytest. Just run ```pytest socialserver``` from the repository root, or, alternatively
```python3 -m socialserver test```.

### Notes

- There is no proper way to create an admin user, due to the initial setup not being done yet. For now, you can
  run ```python3 -m socialserver mk-user```. This will allow you to create a user with the administrator attribute.