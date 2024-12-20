import sys

import apiclient

class Transport:

    perm_class= 'transports'
    
    data: list = []
    ids_list: list = []

    def __init__ (self, primary_broker, pool_transports_list):      

        ids_list=[]       
        for elem in pool_transports_list:
            ids_list.append(elem['id'])
    
        self.ids_list= ids_list.copy()

        data=[]
        for id in self.ids_list:
            data.append(
                primary_broker.get_transport(id)
            )
        self.data= data.copy()    

    def get_logs(self):
        
        print('Transport [ id ]: ', self.data , '\n')
        print('Transport [ data ]: ', self.data , '\n')

    