# jecretz
Jira Secrets Hunter - Helps you find credentials and sensitive contents in Jira tickets. A handy tool for red-team activities, internal assessments and bug-bounties. It performs search based on the keyword-list provided and does regular expression matching for secretz analysis. The search will go deep enough to cover both description and comments section of Jira tickets.

Currently supports self-hosted Jira server instances. Didn't test it on cloud-based instances.

__Requires:__ Python3

### Installing dependencies:

`sudo pip3 install -r requirements.txt`

### Adding auth token:

You can configure Jira auth token in the file __config.json__.

For jira self-hosted software, the auth token is usually `Basic base64_encode(user@xyz.co:password)`

(Note: The username could be with or without email domain in it, depending on how your company uses it)

Yes, you will have to perform Basic authentication, since Jira doesn't provide a feature to generate REST API tokens for self-hosted Jira servers as of writing this. The feature request [JRASERVER-67869](https://jira.atlassian.com/browse/JRASERVER-67869?_ga=2.121133064.1451771552.1590422340-96494979.1587650002) is still open.

### Usage:

`python3 jecretz.py --url "https://jira.domain.tld/" --threads 50 --out output.txt`

If your Jira is behind Okta or any other SSO, make sure to establish SSO session before you run this tool.

##### Help:

```
usage: jecretz.py [-h] -u URL [-t threads] [-o file]

Jecretz, Jira Secrets Hunter

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     jira instance url, eg: https://jira.domain.tld/
  -t threads, --threads threads
                        default: 10
  -o file, --out file   file to save output to, eg: -o output.txt
  ```

### Disclaimer:

I won't be responsible for any action you may perform with this tool. Be careful with them threads.

### Follow me:

Twitter: @sahad_nk
