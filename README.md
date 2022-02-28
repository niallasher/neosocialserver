<div align="center">
    <img src="socialserver/static/logo256.png" style="width:64px;margin-top:12px;margin-bottom:5px;"/>
    <h1 style="margin-top:0;margin-bottom:5px;">socialserver-neo</h1>
</div>

The server side of an open source social media platform. This is a rewrite of a previous implementation, that adds a new
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

- Currently, there is no stability; API version 3 has not been frozen yet, and *anything* is possible to change!
- API version 2 does not exist
    - If you ask where it is, or what happened to it, somebody will show up at your house within the week to have you
      silenced.
    - It kinda exists. APIv1 doesn't work without a few endpoints marked as APIv2. Make no mistake, these are not
      seperate, as some APIv1 functionality utilises APIv2 features, because reasons???
    - The current API version is always to be the same as the server major version, and due to some terrible decisions
      in the past (see above point)
- There is currently no setup process to create a server admin. You can use the hacky little built in user creation
  wizard by running ```python3 -m socialserver mk-user```, to create an admin user. This will change in the future.
  (Web based initial setup at some point.)
- There is currently no real API documentation. If for whatever reason you want to mess with this in its current state,
  you'll have to figure this out yourself, or email me.