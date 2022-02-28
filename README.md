<div align="center">
    <img src="socialserver/static/logo256.png" style="width:64px;margin-top:12px;margin-bottom:5px;"/>
    <h1 style="margin-top:0;margin-bottom:5px;">socialserver-neo</h1>
</div>

The server side of an open source social media platform. This is a rewrite of a previous implementation, that adds a new
API, and many more features, including actually being stable (eventually), actually working properly (eventually), being
easy to deploy and work with (eventually), and being far more maintainable.

Documentation has not been written yet (I'll start on it once interfaces have stabilised a bit), and it's in the very
early stages of development.

---

### Quickstart

- Clone repository
- cat requirements.txt | pip install (recommend using a virtual environment for this, there's a few dependencies)
- set ```SOCIALSERVER_ROOT``` environment variable to where you want things to get stored. Defaults to
  $HOME/socialserver
- ```python3 -m socialserver devel-run``` for development, ```gunicorn socialserver``` for production
- If you want to change settings, default config is at ```$SOCIALSERVER_ROOT/config.toml```. It can be over-ridden with
  ```$SOCIALSERVER_CONFIG_FILE``` to change the location that is checked.
- The server will create the default configuration file automatically, and serve on all available interfaces, using port
    51672.

### Tests

The test suite is written using pytest. Just run ```pytest socialserver``` from the repository root, or alternatively
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
- There is currently no real API documentation. If for whatever reason you want to mess with this in it's current state,
  you'll have to figure this out yourself, or email me.

### What currently works?

This list will probably lag a lot because I never remember to update it.

#### Via /api/v3

- Creating a user
- Modifying user (incl avatar and header image, with already uploaded images)
- Making a post (with already uploaded images)
- Deleting a post
- Reporting a post
- Following a user
- Unfollowing a user
- Blocking a user :(
- Unblocking a user
- Post feed
- Post feed from users you follow
- Post feed from specific set of usernames
- Two factor authentication
- Listing comments (can't make them yet lol)
- Account approvals
- Probably some other stuff.

### Via legacy API

- All original functionalities from socialshare.club except TOTP (coming soon) (relative to the age of the universe)

#### Via local utilities

- Creating a user with custom attributes (e.g. OG server user, administrator, moderator )
- Uploading an image and getting it's identifier for use with the api

### What doesn't currently work?

Everything else

---

### Can I see the old server code?

No.

### Why not?

It's bad

### How bad?

- All contained in one single file, server.py, that contains over 1000 lines of python
- No testing what-so-ever (except for the users lol)
- Incredibly hacky implementations
- Munted configuration file
- The worst image delivery system ever
    - You ever seen a server that delivers profile pictures inline with the post, at full resolution, not allowing a
      browser to cache them? I have.
    - Seriously, we're talking up to 5mb of image delivered inline with a post, such that the profile picture *cannot*
      be cached across posts.
        - For comparison, the current WIP image system delivers a 2kb image using a cachable request on a device with a
          1x pixel ratio.
- The post feeds. Oh god the post feeds.
    - Literally just copied and pasted at points, so that improvements to one don't go down to the others
- Instead of error values being an Enum, they're magic values that you just kinda have to remember
    - Obviously "A08" means "invalid action field on TOTP post call". What sort of idiot wouldn't know that?
    - (direct excerpt from socialserver/src/errors.txt. You're expected to read it whenever you need to remember an
      error.)
    - I knew better ways of doing this, even at the time. I have no excuse.
