
from facilities import mysql
from facilities import configure as CONF

from github.Git import GitHandle
from itertools import islice
import time

separator = '>'


def _prepare_data(lines):
    """

    :param lines: is raw text consists of commit_sha and corresponding filenames.
    :return: [[commit_sha1, [filenames]]]
    """
    data = []
    for line in lines:
        x = line.split(',')
        y = x[1].split(separator)
        y[-1] = y[-1][:-1]
        data.append([x[0], y])
    return data


def _read_lines_of_file(file, line_number):
    """
    reades numbers of lines of file in each invocation.
    :param file:
    :param line_number:
    :return:
    """

    lines = [next(file) for x in range(line_number)]
    return lines


def download_files_for(repos):
    """
    :todo: it needs refactoring. DOSE NOT WORK.
    :param repos:
    :return:
    """
    if type(repos) != []:
        repos = [repos]
    for repo in repos:
        with open(repo+'.csv', 'r') as file:
            for line in file:
                data = line.split(',')
                _download_birt_file_for(repo, data[0], data[1].split('-'))
                git = GitHandle()
                git.set_repository(GitHandle.Repos[repo])
                git.download_files_prior_to(commit_sha1=data[0], filenames=data[0],
                                            save_path=CONF.AddressBank().path_for(repo + '_source_file'),
                                            preserve_tree=True)


def download_files_batch(repos, batch_size=100, sleep_interval = 60):
    """
    The fucnction handles reading information from csv files, for every repository in repos.
    Then downloads the corresponding files and stores them in specified locations.
    :param repos: list of repositories.
    :param batch_size: number of lines to be read from file in each read operation.
    :param sleep_interval: duration to sleep the execution. in secs.
    :return:
    """
    if type(repos) != list:
        repos = [repos]

    git = GitHandle()

    for repo in repos:
        it_num = 0
        file = open(repo+'.csv', 'r')
        # read every 60 lines of file
        print("=============================")
        print("Downloading %s's source files" %repo)
        print("=============================")
        while True:

            lines = list(islice(file, batch_size))
            if len(lines) == 0:
                break
            data = _prepare_data(lines)

            git.set_repository(GitHandle.Repos[repo])
            git.batch_download_files_prior_to(data, save_path=CONF.AddressBank().path_for(repo + '_source_file'),
                                              preserve_tree=True)
            it_num+=1

            print("=============================")
            print('%sst.' % it_num)
            print('sleeping for 1 minutes...')
            print("=============================")

            # sleep for 1 minutes
            if sleep_interval :
                time.sleep(sleep_interval)

        file.close()
        pass


def _retrieve_data(repo):
    db = mysql.DB()
    db.setup_connection(**CONF.mysqlconfig['connection'], **CONF.mysqlconfig[repo])
    data = db.reterive(db.query['all_commit_filenames'])
    return data


def create_csv_download_files(repos):
    """
    The Function retrieves data for the given repositories form DB and writes 'commit' and 'filenames' in a csv
    for each repository.
    :param repos: list of repositories' names.
    :return:
    """
    if type(repos) != list:
        repos = [repos]
    for repo in repos:
        data = _retrieve_data(repo)
        file = open(repo+'.csv', 'w')
        for item in data:
            filename = ''
            s = item[1].split('\n')
            for i in range(len(s) - 1):
                filename += s[i]
                filename += separator
            filename += s[-1] + '\n'
            file.writelines(item[0] + ',' + filename)
        file.close()
        pass
    pass


def main():
    """
    :todo: some of the downloaded files for Birt, Tomcat and Aspectj commits were not found.->
    :todo: look for them in http_404(3).csv by searching records not ended with '.java'.
    :return:
    """
    # create_csv_download_files(CONF.epositories)
    download_files_batch(CONF.epositories[3:])


if __name__ == '__main__':
    main()

