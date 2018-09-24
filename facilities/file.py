
import pickle
import os

class SimpleFile:
    def __init__(self):
        pass

    def save_pickle(self, data, address, file_name):

       file = open(address+'/'+file_name+'.pkl', 'wb')
       pickle.dump(data, file)
       file.close()
       pass
