#!/usr/bin/env python3

import argparse
import requests
import re
import os
import sys
import json
import itertools
from rules import custom_rules
from keywords import search_keywords
from textwrap3 import wrap
from queue import Queue
from threading import Thread
from terminaltables import AsciiTable
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from truffleHogRegexes.regexChecks import regexes

issues = []
fetched_issues = {}
search_queue = Queue(maxsize = 0)
task_queue = Queue(maxsize = 0)
results = {}

def request_session():
	session = requests.Session()
	retries = Retry(total = 5, backoff_factor = 0.1, status_forcelist = [500, 502, 503, 504])
	session.mount('http://', HTTPAdapter(max_retries = retries))
	session.mount('https://', HTTPAdapter(max_retries = retries))
	return session

def get_token():
	try:
		with open('config.json', 'r') as file:
			config = json.load(file)
		return config['token']
	except:
		print("[-] Authorization token required")
		sys.exit(0)

def search(url, keyword, token, issueList = []):
	jql_query = 'text ~ "'+keyword+'"'
	headers = {'Authorization': token, 'X-Atlassian-Token': 'no-check'}
	data = {'startIndex': 0, 'jql': jql_query, 'layoutKey': 'split-view'}
	url = url + '/rest/issueNav/1/issueTable'
	sys.stdout.write('\r => ' + str(keyword))
	sys.stdout.flush()
	req = request_session()
	try:
		response = req.post(url, data=data, headers=headers)
		json_response = response.json()
		try:
			for item in json_response["issueTable"]["issueKeys"]:
				issueList.append(item)
		except:
			print("\n[-] " + keyword + " didn't return any results")
	except:
		print("\n[-] Something went wrong. Check your auth token. Some-times this could be due to Okta/SSO.")
	return issueList

def fetch_issues(url, issueId, token):
	issue_details = {"description": "", "comments": []}
	comments = []
	headers = {'Authorization': token, 'X-Atlassian-Token': 'no-check'}
	params = {'fields': ['description', 'comment', 'created' ,'updated']}
	url = url + '/rest/api/2/issue/' + issueId
	sys.stdout.write('\r => ' + issueId)
	sys.stdout.flush()
	req = request_session()
	try:
		response = req.get(url, params=params, headers=headers)
		json_response = response.json()
		try:
			issue_details["description"] = json_response["fields"]["description"]
			for comment in json_response["fields"]["comment"]["comments"]:
				comments.append(comment["body"])
			issue_details["comments"] = comments
		except:
			print("\n[-] Error fetching issue " + issueId)
	except:
		print("\n[-] Error reaching Jira. Skipping " + issueId)
	return issue_details

def flatten_list(array):
	for items in array:
		for element in items:
			yield element

def check_credentials():
	rules = regexes.copy()
	rules.update(custom_rules)
	for item in fetched_issues:
		sys.stdout.write('\r => ' + item)
		sys.stdout.flush()
		output = {}
		comments = []
		description = fetched_issues[item]["description"] 
		for comment in fetched_issues[item]["comments"]:
			comments.append(comment)
		d_match = []
		c_match = []
		for rule in rules:
			pattern = re.compile(rules[rule])
			d_match.append(pattern.findall(str(description), re.UNICODE))
			for comment in comments:
				c_match.append(pattern.findall(str(comment), re.UNICODE))
		output["description"] = list(flatten_list(d_match))
		output["comments"] = list(flatten_list(c_match))
		results[item] = output

def display_results(results, save, out = None):
	table_data = []
	table_data.append(['Issue ID', 'Description', 'Comments'])
	table = AsciiTable(table_data)
	max_width = table.column_max_width(1)
	align_width = int(max_width/2)
	for result in results:
		description = results[result]["description"]
		comments = results[result]["comments"]
		if not description and not comments:
			continue
		if not description:
			description = "--"
		if not comments:
			comments = "--"
		if len(str(description)) > align_width:
			description = '\n'.join(wrap(str(description), align_width))
		if len(str(comments)) > align_width:
			comments = '\n'.join(wrap(str(comments), align_width))
		table.table_data.append([result, description, comments])
	table.inner_row_border = True
	print(table.table)
	print("[+] Returned " + str(len(table.table_data) - 1) + " items\n") 
	if save:
		output = "\n[+] Jecretz Results\n\n" + table.table + "\n\n[+] Returned " + str(len(table.table_data) - 1) + " items\n\n"
		with open(out, "w") as file:
			file.write(output)

def search_worker(url, token):
	while True:
		keyword = search_queue.get()
		if not keyword:
			break
		search(url, keyword, token, issues)
		search_queue.task_done()

def task_worker(url, token):
	while True:
		issueId = task_queue.get()
		details = fetch_issues(url, issueId, token)
		fetched_issues[issueId] = details
		task_queue.task_done()

def start_thread(worker, url, token, threads):
	for i in range(threads):
		thread = Thread(target=worker, args = (url, token))
		thread.daemon = True
		thread.start()

def main():
	argparser = argparse.ArgumentParser(description = 'Jecretz, Jira Secrets Hunter')
	argparser.add_argument('-u', '--url', help = 'jira instance url, eg: https://jira.domain.tld/', required = True)
	argparser.add_argument('-t', '--threads', metavar = 'threads', default = 10, help = 'default: 10', type = int)
	argparser.add_argument('-o', '--out', metavar = 'file', help = 'file to save output to, eg: -o output.txt')
	args = argparser.parse_args()
	if args.url.endswith('/'):
		args.url = args.url[:-1]
	url = args.url
	threads = args.threads
	save = 0
	if args.out:
		save = 1
	token = get_token()
	print("[+] Initiating search..")
	for item in sorted(search_keywords, key = len):
		search_queue.put(item)
	start_thread(search_worker, url, token, threads)
	search_queue.join()
	issue_set = list(set(issues))
	print("\n[+] Search returned " + str(len(issue_set)) + " tickets")
	print("[+] Fetching Jira Issues..")
	start_thread(task_worker, url, token, threads)
	for issueId in issue_set:
		task_queue.put(issueId)
	task_queue.join()
	print("\n[+] Analyzing..")
	check_credentials()
	print("\n[+] Results\n")
	if save:
		display_results(results, save, args.out)
	else:
		display_results(results, 0)

if __name__ == "__main__":
	main()
