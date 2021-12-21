# Unit Test Coverage
## Api2

- [ ] User
    - [x] Creation
    - [x] Deletion
    - [ ] Modification
        - [x] Username
        - [x] Display Name
        - [x] Bio
        - [ ] Header Image
        - [ ] Profile Picture
    - [x] Get Info
- [ ] User Session
  - [x] Creation
  - [x] Deletion
  - [ ] Get Info
- [ ] Block
    - [ ]  Create
    - [ ]  Remove
    - [ ] Check blocked user not in post feed
- [ ] Post
    - [ ] Plaintext post
    - [ ] With image
    - [ ] With images
    - [ ] Delete post
    - [ ] Attempt to delete other persons post
- [ ] Follow
    - [ ] Follow User
    - [ ] Unfollow User
    - [ ] Attempt to follow self
- [ ] Report
    - [ ] Report post
    - [ ] Attempt to double report post
        - Need to mess with the config for this, since it
        depends on whether silent_fail_on_double_report is True
    - [ ] Attempt to double report with silent fail on
        - Same as previous
- [ ] Image
    - [ ] Get Image

## Database Schema

- [ ] User
    - [ ] Create valid
    - [ ] Create missing data
    - [ ] Create invalid data
    - [ ] Remove
- List TBD later

# Notes

## Tags

- Max length of 12 characters.
- Case-insensitive.
- a-z and A-Z ONLY!
- Prefixed with a # character.
- Up to 10 tags per post ???

## Rich Text

- Can use bold, italic and underline?
- Markdown syntax
- Might not happen

## Usernames

- Max length of 20 characters (was going to be 15, but one socialshare user had to have a 16 char username)
- Case-insensitive.
- Globally unique.
- a-z, 0-9 and \_ ONLY!

## Display Names

- Max length of 32 characters. If yours is longer, it will be truncated. Sorry socialshare users.
- Saved; if you type one that's never been done it just gets added to the DB. Otherwise, you get to join the users of that tag! FUN!
- Whatever you want I guess (will regret this later?)

# Bios

- Max length of 256 characters (we don't want ur fucking life story lmao)
- Whatever you want.

# Posts

- Max length of 256 characters. That should be enough???
- Whatever you want.

# Images

- Max image count per post: 4
- When sending a cropped image, we should send the original too. The client should send a json string in the payload, like the following:

```
  {
    "original": "ORIGINAL_BASE64_STRING",
    ""cropped": "CROPPED_BASE64_STRING"
  }
```

If no cropped image is present, then cropped can be omitted, and the server will understand.
