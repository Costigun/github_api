import requests
import datetime
import sys



old_content_count = {}

def filter_response(response, filter_type,date_start=None, date_end=None):
    result = []
    tod = datetime.datetime.now()
    if date_start is None and date_end is not None:
        end = datetime.datetime.strptime(date_end, '%Y-%m-%d')
        if filter_type == 'commit':

            for data in response:
                data_time = data['commit']['author']['date']
                data_time = datetime.datetime.strptime(data_time, '%Y-%m-%dT%H:%M:%SZ')
                if data_time <= end:
                    result.append(data)
            return result
        elif filter_type == 'pulls' or filter_type == 'issue':
            if filter_type == 'pulls':
                time_delta = datetime.timedelta(days=30)
            else:
                time_delta = datetime.timedelta(days=14)
            old_count = 0
            content_type = 'open'
            for data in response:
                created_at = data['created_at']
                created_at = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                closed_at = data['closed_at']
                if created_at <= end:
                    result.append(data)
                    if end >= created_at and (created_at + time_delta) < tod and content_type == 'open':
                        old_count += 1
                        old_content_count[filter_type] = old_count

                elif closed_at is not None:
                    content_type='close'
                    closed_at = datetime.datetime.strptime(closed_at, '%Y-%m-%dT%H:%M:%SZ')
                    if closed_at <= end:
                        result.append(data)


            old_content_count[filter_type]=old_count
            return result
    elif date_start is not None and date_end is None:
        start = datetime.datetime.strptime(date_start, '%Y-%m-%d')
        if filter_type == 'commit':
            for data in response:
                data_time = data['commit']['author']['date']
                data_time = datetime.datetime.strptime(data_time, '%Y-%m-%dT%H:%M:%SZ')
                if start <= data_time:
                    result.append(data)
            return result
        elif filter_type == 'pulls' or filter_type == 'issue':
            if filter_type == 'pulls':
                time_delta = datetime.timedelta(days=30)
            else:
                time_delta = datetime.timedelta(days=14)
            old_count = 0

            content_type = 'open'
            for data in response:
                created_at = data['created_at']
                created_at = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                closed_at = data['closed_at']

                if start <= created_at and closed_at is None:
                    result.append(data)
                    if start <= created_at and (created_at + time_delta) < tod and content_type == 'open':
                        old_count+= 1
                        old_content_count[filter_type] = old_count
                elif closed_at is not None:
                    content_type = 'close'
                    closed_at = datetime.datetime.strptime(closed_at, '%Y-%m-%dT%H:%M:%SZ')
                    if start <= closed_at:
                        result.append(data)

            return result
    elif date_start is not None and date_end is not None:
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
            if filter_type == 'pulls':
                time_delta = datetime.timedelta(days=30)
            else:
                time_delta = datetime.timedelta(days=14)
            old_count = 0
            for data in response:
                created_at = data['created_at']
                created_at = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                closed_at = data['closed_at']
                content_type = 'open'
                if start <= created_at <= end:
                    result.append(data)
                    if start <= created_at <= end and (created_at + time_delta) < tod and content_type == 'open':
                        old_count += 1
                        old_content_count[filter_type] = old_count
                elif closed_at is not None:
                    content_type = 'close'
                    closed_at = datetime.datetime.strptime(closed_at, '%Y-%m-%dT%H:%M:%SZ')
                    if start <= closed_at <= end:
                        result.append(data)
                    old_content_count[filter_type] = old_count
            return result
    else:
        if filter_type not in ['pulls','issue']:
            return response
        else:
            if filter_type == 'pulls':
                time_delta = datetime.timedelta(days=30)
            else:
                time_delta = datetime.timedelta(days=14)
            old_count = 0
            tod = datetime.datetime.now()
            content_type = 'open'
            for data in response:
                created_at = data['created_at']
                created_at = datetime.datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
                closed_at = data['closed_at']
                if (created_at + time_delta) < tod and content_type == 'open' and closed_at is None:
                    old_count += 1
                    old_content_count[filter_type] = old_count
            return response



def get_all_data(url):
    response = requests.get(url)
    repos = response.json()

    while 'next' in response.links.keys():
        response = requests.get(response.links['next']['url'])
        repos.extend(response.json())
    return repos


def get_top_active_users(branch, date_start=None, date_end=None):
    url = URL + '/commits?base={}&per_page=100&page=1'.format(branch)
    authors = {'login': [], 'count': []}
    repos = get_all_data(url)
    for commit in repos:
        commit_author = commit['author']['login']
        authors_list = authors['login']
        if commit_author not in authors_list:
            authors_list.append(commit_author)
    author_final = [{}] * len(authors['login'])
    repos = filter_response(repos, 'commit', date_start, date_end, )
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


def get_pulls_on_branch(branch, date_start=None, date_end=None):
    if branch is None:
        pulls_url = URL + '/pulls?base={}'.format('master')
    else:
        pulls_url = URL + '/pulls?base={}'.format(branch)
    pulls_open = pulls_url + '&state=open&per_page=100&page=1'
    pulls_closed = pulls_url + '&state=closed&per_page=100&page=1'
    pulls_open, pulls_closed = get_all_data(pulls_open), get_all_data(pulls_closed)
    pulls_open = filter_response(pulls_open, 'pulls',date_start, date_end)
    pulls_closed = filter_response(pulls_closed, 'pulls', date_start, date_end)
    pulls_dict = {'open': len(pulls_open), 'closed': len(pulls_closed)}

    return pulls_dict


def get_issues_on_branch(branch, date_start=None, date_end=None):
    if branch is None:
        issues_url = URL + '/issues?base{}'.format('master')
    else:
        issues_url = URL + '/issues?base={}'.format(branch)
    issues_open = issues_url + '&state=open&per_page=100&page=1'
    issues_closed = issues_url + '&state=closed&per_page=100&page=1'
    issues_open, issues_closed = get_all_data(issues_open), get_all_data(issues_closed)
    issues_open = filter_response(issues_open, 'issue',date_start, date_end, )
    issues_closed = filter_response(issues_closed, 'issue', date_start, date_end, )
    issues_dict = {'open': len(issues_open), 'closed': len(issues_closed)}
    return issues_dict

def get_user_and_repo(URL):
    result = URL.split('/')
    user = result[3]
    repo = result[4]
    return user,repo

if __name__ == '__main__':
    PUBLIC_URL = sys.argv[1]
    user,repo = get_user_and_repo(PUBLIC_URL)
    URL = 'https://api.github.com/repos/{}/{}'.format(user,repo)
    try:
        date_start_arg = sys.argv[2]
    except IndexError:
        date_start_arg = None
    try:
        date_end_arg = sys.argv[3]
    except IndexError:
        date_end_arg = None
    try:
        branch_arg = sys.argv[4]
    except IndexError:
        branch_arg = None
    commits = get_top_active_users(branch=branch_arg,date_start=date_start_arg,date_end=date_end_arg)
    pulls = get_pulls_on_branch(branch=branch_arg,date_start=date_start_arg,date_end=date_end_arg)
    issues = get_issues_on_branch(branch=branch_arg,date_start=date_start_arg,date_end=date_end_arg)
    print(f'30 топ пользовате {commits}', pulls, issues, old_content_count,sep='\n')
