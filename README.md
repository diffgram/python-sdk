
# SDK for Diffgram

This is the SDK for [Diffgram](https://github.com/diffgram/diffgram) <br> and
[Diffgram.com](https://diffgram.com/) <br>

## SDK Install

#### [Full Documentation](https://diffgram.readme.io/docs)

### Quickstart Install SDK
`pip install diffgram`

On linux
`pip3 install diffgram`

[Credentials Guide](https://diffgram.readme.io/reference) <br>
[Get Credentials from Diffgram.com](https://diffgram.com/) (or your Private Deploy)

The starting point for most useful work is to get a project:
```
from diffgram import Project

project = Project(host = "https://diffgram.com",
		  project_string_id = "replace_with_project_string",
		  client_id = "replace_with_client_id",
		  client_secret = "replace_with_client_secret")
```

Replace `host` with your URL for Open Core installs.

* [Tasks Introduction](https://diffgram.readme.io/docs/tasks-introduction)
* [Import Introduction](https://diffgram.readme.io/docs/importing-your-data)
* [Updating Existing Instances](https://diffgram.readme.io/docs/importing-instances-walkthrough)
* [Pre-Label Example Video](https://youtu.be/55Hofp1H7yM)
* [Compatibility](https://diffgram.readme.io/docs/compatibility-will-diffgram-work-with-my-system)


#### Beta
Note the API/SDK is in beta and is undergoing rapid improvement. There may be breaking changes.
Please see the [API docs](https://diffgram.readme.io/reference) for the latest canonical reference 
and be sure to upgrade to latest ie: `pip install diffgram --upgrade`. We will attempt to keep the SDK up to date with the API.

[Help articles for Diffgram.com](https://diffgram.readme.io/)  See below for some examples.

Requires Python >=3.5

The default install through pip will install dependencies
for local prediction (tensorflow opencv) as listed in `requirements.txt`.
The only requirement needed for majority of functions is `requests`. 
If you are looking for a minimal size install and already have requests use
the `--no-dependencies` flag ie `pip install diffgram --no-dependencies`

