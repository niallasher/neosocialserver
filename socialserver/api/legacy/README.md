# socialserver legacy api

****

### About bugs etc.

This portion of code is intended to be (mostly; more info further down) bug for bug compatible with an older server
program, hence, some weird decisions and bugs are present in it.

Things like no error codes being returned in some places, but being returned in others are intentional, since the
original server had deficiencies in this regard, and the client didn't handle this.

Some exceptions are made to compatibility; some extra failure conditions have been added, mostly involving input
validation. In some cases, input is simply truncated instead. Alongside this, some security related things have been or
will be modified, since the legacy API didn't always ask for authentication in some places it probably should have.

All legacy code should be considered complete, and not to be touched, unless functionality is broken by changes in other
areas of the program, or unit tests are failing. The exception to this is anything critical regarding security; any big
vulnerabilities caused by server code should be fixed, and any vulnerabilities caused by other factors (e.g. API
specification issues) should be either made toggleable via the configuration file, or outright disabled depending on
severity.

No new feature additions to this code are to be considered. It, and the client(s) supporting it are to be considered
deprecated, and support will only be provided to ensure core functionality is mostly intact on the new server version.

### A note on naming

The reason this portion of the program is not contained in something like ```socialserver.api.v1``` (it used to be) is
that the old server code actually contained some paths marked as API Version 2, which are small in scope
(```user_deauth.LegacyAllDeauth```, ```comment.LegacyCommentLike``` and some upcoming, as of commit #4b9578d6b1, 2FA
functionality.)

It turned out that the original implementation actually had some parts of API version 1 that depended on version 2
functionality, namely when logging in, so I decided it was less confusing to just bundle them into one.

### Targeted compatibility

This probably won't mean much to most people, since the original server code is private, due to being abhorrent to the
eyes, but the compatibility target here is ```2.3.0```.

In practice, the production version of socialserver ended up with a lot of weird little patches, and some
functionality/edge cases not present in the original code. These will not be replicated.

If config.legacy_api_interface.report_legacy_version is True, the server will always report it's version number as
```2.99.0``` when the legacy server_info endpoint is called, to work around some possible issues with very old
socialshare versions feature detection.