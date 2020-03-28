# encoding=UTF-8
"""__init__.py"""
import re
import csv

def build_filter(args):
    return Filter(args)

class Filter:
    def __init__(self, args):
        if not isinstance(args, bytes):
            args = args.encode('utf8')
        with open(args) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            self.issue_map = { row[0].encode(): row[1].encode() for row in reader}
        self.bz_replace_pattern = re.compile(r"(?i)(\(?(bz|bug|bugzilla)[ /]*#?(\d+)\)?)".encode())

    def commit_message_filter(self, commit_data):
        for match in self.bz_replace_pattern.findall(commit_data['desc']):
            full_match = match[0]
            if full_match in [b'bz2', b'BZ2', b'Bz2']:
                continue
            try:
                bz_number = match[2]
            except IndexError:
                raise ValueError(f'invalid match [{match}] in {commit_data["desc"]}')
            try:
                jira_ticket = self.issue_map[bz_number]
            except KeyError:
                raise ValueError(f'Cannot find jira ticket for {match}')
            commit_data['desc'] = commit_data['desc'].replace(
                full_match, f"(JIRA {jira_ticket.decode()}) (Was BZ {bz_number.decode()})".encode())
