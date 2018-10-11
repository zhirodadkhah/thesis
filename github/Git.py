
from facilities import configure
import pycurl
import certifi
import json
from io import BytesIO
import os




class GitHandle:
    Repos={
        'BIRT': 'BIRT',
        'TOMCAT': 'TOMCAT',
        'SWT': 'SWT',
        'JDT': 'JDT',
        'ECLIPSE': 'ECLIPSE',
        'ASPECTJ': 'ASPECTJ'}

    def __init__(self):
        """
        :todo: access_token may expire.
        """
        self.url = {'githubapi': 'https://api.github.com/repos/',
                    #'file_dl': ['https://github.com/','raw/'],
                    'file_dl': ['https://raw.githubusercontent.com/',''],
                    'commits': 'commits/',
                    'token': '/?access_token=653120e02d8c8f61c4d97161fa2b5a3f20535b3d',
                    'github': 'https://github.com/',
                    self.Repos['BIRT']: 'eclipse/birt/',
                    self.Repos['TOMCAT']: 'apache/tomcat/',
                    self.Repos['ASPECTJ']: 'eclipse/org.aspectj/',
                    self.Repos['JDT']: 'eclipse/eclipse.jdt.ui/',
                    self.Repos['SWT']: 'eclipse/eclipse.platform.swt/',
                    self.Repos['ECLIPSE']: 'eclipse/eclipse.platform.ui/'}
        
        self.patterns = {'target_commit': "Recent Commits to "}

        self.files = {'http_404': 'http_404.csv',
                      'commit_status': 'commit_status.csv'}

        self.log = {}

        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.CAINFO, certifi.where())
        self.buffer = BytesIO()
        self.chosen_repository = None

        self._create_logs()
        pass

    def refresh(self):

        self.curl.close()

        self.curl = pycurl.Curl()
        self.curl.setopt(pycurl.CAINFO, certifi.where())

    def _create_logs(self):

        for key in self.files.keys():
            self.log.update({key:open(self.files[key],'a')})
            self.log[key].close()
            pass
        pass

    def _open_logs(self):

        for key in self.files.keys():
            self.log.update({key:open(self.files[key],'a')})
            pass

    def _close_logs(self):
        """
        :todo: centralize the file open and termination tasks.
        :return:
        """
        for file in self.log:
            self.log[file].close()

    def set_repository(self, repository = Repos['BIRT']):
        self.chosen_repository = repository
        pass

    def write_to_csv(self, file, *args):

        raw = ""
        for i in range(len(args)-1):
            raw += args[i]+","
        raw += args[-1]+'\n'
        file.write(raw)



    def _get(self, url, redirect = False):
        """
        The method browses the given url.
        :param url:
        :param redirect:
        :return: HTTP_CODE == 404 returns False; else returns True.
        """

        # Refresh the buffer.
        self.buffer.close()
        self.buffer = BytesIO()

        # replace wihtspaces
        url = url.replace(' ', '%20')

        # setups
        self.curl.setopt(pycurl.WRITEFUNCTION, self.buffer.write)
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.FOLLOWLOCATION, redirect)

        self.curl.perform()
        x = self.curl.getinfo(pycurl.HTTP_CODE)
        x1 = self.buffer.getvalue()

        return self.curl.getinfo(pycurl.HTTP_CODE)==200


    def commit_prior_to(self, commit_sh):
        """
        The method finds the commit befor commit_sh
        :todo: inexsiting commits.
        :param commit_sh:
        :param repository:
        :return: if method fails to extract the older commit, so returns None.
        """

        # self._get(url=self.url['githubapi']+self.url[self.chosen_repository]+self.url['commits']+commit_sh+'~1'+
        #                 self.url['token'])
        # try:
        #     return json.loads(self.buffer.getvalue())['sha']
        # except Exception:
        #     # raise Exception('No commit Found for the given commit_sha: %s'%commit_sh)
        #     return None
        # pass

        # below section uses github api. because the server may response to limited requests in a special time span,
        # HTTP request are send to server.

        if self._get(url=self.url['github'] + self.url[self.chosen_repository] + self.url['commits'] +
                         commit_sh + '~1') :

            data = str(self.buffer.getvalue())
            i = data.rfind(self.patterns['target_commit']) + 20
            data = data[i:i+100].split('"')[0]
            data = data[data.find(':')+1:]
            return data
        else:
            return None
        pass

    def save_file(self, save_path, filename, commit_sha0, commit_sha1, preserve_tree=True):
        """
        :todo: (solved) what should be done if the file already exist.
        :solution: the directory structure is implemented.
        :param save_path: the path to save the file.
        :param filename: name of the target file.
        :param preserve_tree: if file name containce a tree structure, the spedified direcotries in the filename will
        be created and the file will be located at the bottom of the subdirecory.
        :return:
        """

        if not preserve_tree:
            with open(save_path + filename[filename.rfind('/'):] + "_" + commit_sha1[:7] + '.' + commit_sha0[:7],
                      'wb') as file:
                file.write(self.buffer.getvalue())
        else:
            # split filename into filepath and name.
            index = filename.rfind('/') + 1
            name = filename[index:]
            filepath = filename[:index]

            save_path += '/'+ filepath
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
            # The first 7 characters of commit_sha and commit
            with open(save_path + name + "_" + commit_sha1[:7] + '.' + commit_sha0[:7], 'wb') as file:
                file.write(self.buffer.getvalue())

    def download_files_prior_to(self, commit_sha1, filenames, save_path, preserve_tree = False):
        """
        This method downloads the specified files for the given commit_sha.
        The method preserves the file location in project tree.
        if the older commit prior to the given one is not found, it will be logged in commit_status_log.csv
        if the files for a given commit do not exist, they will be logged in http_404.csv.
        :todo: what about files which are not find or commit_shaes that don't exist.
        :param filenames: is a list of filenames.
        :param commit_sha1:
        :param save_path:
        :return:
        """
        self._open_logs()

        # for i in range(2):
        #     commit_sha0 = self.commit_prior_to(commit_sha1)
        #     if commit_sha0 is not None:
        #         break
        #     else:
        #         self.refresh()

        commit_sha0 = self.commit_prior_to(commit_sha1)
        if commit_sha0 == None:

            self.write_to_csv(self.log['commit_status'], self.chosen_repository, '-'+commit_sha1)
            print('-%s' % commit_sha1)
        else:
            self.write_to_csv(self.log['commit_status'], self.chosen_repository, '+' + commit_sha1)
            print(commit_sha1)
            for filename in filenames:

                if self._get(url=self.url['file_dl'][0] + self.url[self.chosen_repository] + self.url['file_dl'][1] +
                              commit_sha0 + '/' + filename, redirect=True):

                    self.save_file(save_path, filename, commit_sha0, commit_sha1, preserve_tree)
                else:
                    self.write_to_csv(self.log['http_404'], self.chosen_repository, commit_sha1, commit_sha0, filename)
                    pass
                pass
        self._close_logs()
        pass

    def batch_download_files_prior_to(self, bugs, save_path, preserve_tree=True):
        """
        This methos downloads all files from github in batch.
        the method dosen't preserves the file location in project tree.
        if the older commit prior to the given one is not found, it will be logged in commit_status_log.csv
        if the files for a given commit do not exist, they will be logged in http_404.csv.
        :param bugs: [commit_sha, str(file_names)]
        :param save_path:
        :return:
        """
        self._open_logs()


        for bug in bugs:

            # for i in range(2):
            #     commit_sha0 = self.commit_prior_to(bug[0])
            #     if commit_sha0 is not None:
            #         break
            #     else:
            #         self.refresh()

            commit_sha0 = self.commit_prior_to(bug[0])
            if commit_sha0 == None:

                self.write_to_csv(self.log['commit_status'], self.chosen_repository, '-'+ bug[0])
                print('-%s' %bug[0])

            else:
                self.write_to_csv(self.log['commit_status'], self.chosen_repository, '+' + bug[0])
                print(bug[0])
                for filename in bug[1]:
                    if self._get(url=self.url['file_dl'][0] + self.url[self.chosen_repository] + self.url['file_dl'][1] +
                                  commit_sha0 + '/' + filename, redirect=True):

                        self.save_file(save_path, filename, commit_sha0, bug[0], preserve_tree)
                    else:
                        self.write_to_csv(self.log['http_404'], self.chosen_repository, bug[0], commit_sha0, filename)
                    pass
            pass
        self._close_logs()
        pass


def main():
    path = configure.AddressBank.path_for('?')
    filenames=['data/org.eclipse.birt.data.oda.mongodb.ui/src/org/eclipse/birt/data/oda/mongodb/ui/impl/MongoDBDataSetWizardPage.java']
    git = Git()
    git.set_repository(Git.Repos.BIRT)
    git.download_files_prior_to(commit_sha1='345f01b', filenames=filenames, save_path=path['paths']['source_codes'])
    pass




if __name__ == '__main__':
    main()