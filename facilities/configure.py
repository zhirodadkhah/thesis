
import os
import sys
if sys.version_info[0]<3:
    import simplejson as json
else:
    import json



class AddressBank():

    def __init__(self):
        """
        :todo: some pathes in address are not corect.
        """
        try:
            self.adrs_file = json.load(open(os.path.abspath("/media/zhiro/2A1498C4149894831/in_rogress/Thesis/softwares/ZH_MainTools/facilities/Address"), 'r'))
            self.root = "/media/zhiro/2A1498C4149894831/in_rogress/Thesis/"
        except :
            raise Exception("could not open Address file")
        pass


    def find_path_for(self, name, path):
        for root, dirs, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)
        raise Exception("could not find path for %s" % name)

    def path_for(self, item):

        return os.path.abspath(os.path.join(self.root, self.adrs_file[item]))


def mysqlconfig():
    config = {
        'connection':{'user': 'python',
                    'password': 'pyconnector',
                    'host': '127.0.0.1',
                    'raise_on_warnings': True},
        'BIRT':{'database': 'Birt'},
        'TOMCAT': {'database': 'Tomcat'},
        'SWT': {'database': 'SWT'},
        'JDT': {'database': 'JDT'},
        'ECLIPSE': {'database': 'Eclipse_Platform_UI'},
        'API': {'database': 'API_Descriptions'},
        'ASPECTJ' : {'database': 'AspectJ'}
    }

    return config

def main():
    a = AddressBank()
    for item in os.listdir(a.path_for('BIRT_target')):
        print(item)

if __name__ == '__main__':
    main()
