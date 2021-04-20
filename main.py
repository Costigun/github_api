import requests
import datetime

URL = "https://api.github.com/repos/ryanheise/audio_service"
TOKEN = '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'
HEADERS = {'Authorization': 'token %s' % TOKEN}
from pprint import pprint

def filter_response(response, date_start, date_end,filter_type):
    result = []
    start = datetime.datetime.strptime(date_start, '%Y-%m-%d')
    end = datetime.datetime.strptime(date_end, '%Y-%m-%d')
    if filter_type == 'commit':
        for data in response:
            data_time = data['commit']['author']['date']
            data_time = datetime.datetime.strptime(data_time, '%Y-%m-%dT%H:%M:%SZ')
            if start <= data_time <= end:
                result.append(data)
        return result
    elif filter_type == 'pulls' or filter_type == 'issue':
        for data in response:
            created_at = data['created_at']
            created_at = datetime.datetime.strptime(created_at,'%Y-%m-%dT%H:%M:%SZ')
            closed_at = data['closed_at']


            if start<=created_at<=end:
                print(data['created_at'])
                result.append(data)
            elif closed_at is not None:
                closed_at = datetime.datetime.strptime(closed_at, '%Y-%m-%dT%H:%M:%SZ')
                if start<=closed_at<=end:
                    result.append(data)
        return result


def get_all_data(url):
    response = requests.get(url, headers=HEADERS)
    repos = response.json()

    while 'next' in response.links.keys():
        response = requests.get(response.links['next']['url'], headers=HEADERS)
        repos.extend(response.json())
    return repos


def get_top_active_users(branch):
    url = URL + '/commits?base{}&per_page=100&page=1'.format(branch)
    authors = {'login': [], 'count': []}
    repos = get_all_data(url)
    for commit in repos:
        commit_author = commit['author']['login']
        authors_list = authors['login']
        if commit_author not in authors_list:
            authors_list.append(commit_author)
    author_final = [{}] * len(authors['login'])
    repos = filter_response(repos, '2019-03-27', '2021-04-15','commit')
    for i, author in enumerate(authors['login']):
        count = 0
        for author_commit in repos:
            author_r = author_commit['author']['login']
            if author_r == author:
                count += 1
                author_final[i] = {
                    'login': author,
                    'count': count
                }

    return author_final[:30]


def get_pulls_on_branch(branch):
    if branch is None:
        pulls_url = URL + '/pulls?base={}'.format('master')
    else:
        pulls_url = URL + '/pulls?base={}'.format(branch)
    pulls_open = pulls_url + '&state=open&per_page=100&page=1'
    pulls_closed = pulls_url + '&state=closed&per_page=100&page=1'
    pulls_open,pulls_closed = get_all_data(pulls_open),get_all_data(pulls_closed)
    pulls_open = filter_response(pulls_open,'2021-01-01', '2021-04-18','pulls')
    pulls_closed = filter_response(pulls_closed,'2021-04-01', '2021-04-19','pulls')
    pulls_dict = {}
    pulls_dict['open'] = len(pulls_open)
    pulls_dict['closed'] = len(pulls_closed)

    return pulls_dict

def get_issues_on_branch(branch):
    if branch is None:
        issues_url = URL + '/issues?base{}'.format('master')
    else:
        issues_url = URL + '/issues?base={}'.format(branch)
    issues_open = issues_url +'&state=open&per_page=100&page=1'
    issues_closed = issues_url + '&state=closed&per_page=100&page=1'
    issues_open,issues_closed = get_all_data(issues_open),get_all_data(issues_closed)
    issues_open = filter_response(issues_open,'2021-04-01', '2021-04-19','issue')
    issues_closed = filter_response(issues_closed, '2021-04-01', '2021-04-19', 'issue')
    issues_dict = {}
    issues_dict['open'] = len(issues_open)
    issues_dict['closed'] = len(issues_closed)
    return issues_dict

if __name__ == '__main__':
    commits = get_top_active_users(None)
    pulls = get_pulls_on_branch(None)
    issues = get_issues_on_branch(None)
    print(commits,pulls,issues,sep='\n')
