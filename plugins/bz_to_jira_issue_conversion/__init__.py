# encoding=UTF-8
"""__init__.py"""
from __future__ import print_function
import re
import csv

def build_filter(args):
    return Filter(args)

class Filter:
    def __init__(self, args):
        with open(args) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            self.issue_map = { row[0].encode(): row[1].encode() for row in reader}
        self.bz_replace_pattern = re.compile(r"(?i)(\(?(issue|bz|bug|bugzilla|bugzilla bug)[ /]*#?(\d+)\)?)")#.encode())

    def commit_message_filter(self, commit_data):
        for match in self.bz_replace_pattern.findall(commit_data['desc']):
            full_match = match[0]
            if full_match in ['bz2', 'BZ2', 'Bz2']:
                continue
            try:
                bz_number = match[2]
            except IndexError:
                raise ValueError('invalid match [{}] in {}'.format(match, commit_data['desc']))
            try:
                jira_ticket = self.issue_map[bz_number]
                commit_data['desc'] = commit_data['desc'].replace(
                    full_match, "(JIRA {}) (Was BZ {})".format(jira_ticket, bz_number))
            except KeyError:
                pass
