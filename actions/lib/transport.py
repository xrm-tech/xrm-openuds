import sys
sys.path.append('/etc/apiclient')
import apiclient

class Transport:

    perm_class= 'transports'
    
    data: list = []
    ids_list: list = []

    def __init__ (self, primary_broker, pool_transports_list):      
               
        for elem in pool_transports_list:
            self.ids_list.append(elem['id'])

        for id in self.ids_list:
            self.data.append(
                primary_broker.get_transport(id)
            )    

    def get_logs(self):
        
        print('Transport [ data ]: ', self.data , '\n')

    