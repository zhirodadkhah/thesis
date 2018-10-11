from mysql import connector

class DB:
    """
    :todo:
    """
    query = {
        'all_commit_filenames': "SELECT commit, files from bug_and_files",
        'limit_commit_filenames': "SELECT commit, files from bug_and_files limit %s",
        'filenames_where_commit': "SELECT files from bug_and_files where commit= %s"
    }
    def __init__(self):



        self.cnx = None
        self.cursor = None
        pass

    def setup_connection(self, **configs):
        if self.cnx is not None:
            self.cnx.close()
            self.cursor.close()

        self.cnx = connector.connect(**configs)
        self.cursor = self.cnx.cursor()
        pass

    def reterive(self, query, *args):
        """

        :param query:
        :param args:
        :return:
        structure: list of raws as tuple: [(Feild1, Feild2, ..., Feildn)]
        """

        self.cursor.execute(query, args)
        return self.cursor.fetchall()