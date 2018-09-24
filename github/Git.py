
from Facilities import configuration
import pycurl
import json
from io import BytesIO
import os




class Git:
    class Repos:
        BIRT = 'BIRT'
        TOMCAT = 'TOMCAT'
        SWT = 'SWT'
        JDT = 'JDT'
        ECLIPSE = 'ECLIPSE'
        ASPECTJ = 'ASPECTJ'
        pass

    def __init__(self):
        self.url = {'githubapi':'https://api.github.com/repos/',
                    'file_dl': ['https://github.com/','raw/'],
                    'commits':'commits/',
                    self.Repos.BIRT:'eclipse/birt/'}
        self.curl = pycurl.Curl()
        self.buffer = BytesIO()
        self.chosen_repository = None
        pass

    def set_repository(self, repository = Repos.BIRT):
        self.chosen_repository = repository

    def _get(self, url, redirect = False):

        #Refresh the buffer.
        self.buffer.close()
        self.buffer = BytesIO()

        #setups
        self.curl.setopt(pycurl.WRITEFUNCTION, self.buffer.write)
        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.FOLLOWLOCATION, redirect)

        self.curl.perform()


    def commit_prior_to(self, commit_sh):
        """
        The method finds the commit befor commit_sh
        :param commit_sh:
        :param repository:
        :return:
        """

        self._get(url = self.url['githubapi']+self.url[self.chosen_repository]+self.url['commits']+commit_sh+'~1')
        try:
            return json.loads(self.buffer.getvalue())['sha']
        except Exception:
            raise Exception('No commit Found for the given commit_sha: %s'%commit_sh)


    def download_files_prior_to(self, filenames, commit_sha1, save_path ):
        """
        :todo: what about files which are not find or commit_shaes that don't exist.
        :param filenames:
        :param commit_sha1:
        :param save_path:
        :return:
        """

        commit_sha0 = self.commit_prior_to(commit_sha1 )
        for filename in filenames:

            self._get(url=self.url['file_dl'][0] + self.url[self.chosen_repository] + self.url['file_dl'][1] +
                          commit_sha0 + '/' + filename, redirect=True)

            #split filename into filepath and name.
            index = filename.rfind('/') + 1
            name = filename[index:]
            filepath = filename[:index]

            save_path += filepath
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
            # The first 7 characters of commit_sha and commit
            with open(save_path + name + "_" + commit_sha1[:7] +'.'+ commit_sha0[:7], 'wb') as file:
                file.write(self.buffer.getvalue())
        pass


def main():
    path = configuration.load_parameters()
    filenames=['data/org.eclipse.birt.data.oda.mongodb.ui/src/org/eclipse/birt/data/oda/mongodb/ui/impl/MongoDBDataSetWizardPage.java']
    git = Git()
    git.set_repository(Git.Repos.BIRT)
    git.download_files_prior_to(commit_sha1='345f01b', filenames=filenames, save_path=path['paths']['source_codes'])
    pass


if __name__ == '__main__':
    main()