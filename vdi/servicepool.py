import sys
sys.path.append('/etc/apiclient')
import apiclient

class ServicePool:
    
    perm_class= 'servicespools'
    name:str
    id:str    
    data_list:dict       
    groups_list:list
    transports_list:list
    assigned_services_list:list
    assignables_list:list

    def __init__(self, primary_broker, pool_name):
        
        self.name= pool_name
        self.id= primary_broker.get_pool_id(pool_name)
        self.data_list= primary_broker.get_pool(self.id)
        self.groups_list= primary_broker.list_pool_groups(self.id)
        self.transports_list= primary_broker.list_pool_transports(self.id)         
        __unfiltered_assigned_services_list= primary_broker.list_pool_assigned_services(self.id)                      
        self.assigned_services_list= list(filter(self.__filter_valid_services, __unfiltered_assigned_services_list))           
        self.assignables_list= primary_broker.list_pool_assignables(self.id)
    
    def __filter_valid_services(self, assigned_service):
        if (assigned_service['state'] == 'U'):
            return True
        else:
            return False          
           
    def get_logs(self):

        print('ServicePool [ id ]: ', self.id , '\n')
        print('ServicePool [ data ]: ', self.data_list, '\n')
        print('ServicePool [ groups ]: ', self.groups_list, '\n')
        print('ServicePool [ transports ]: ', self.transports_list, '\n')
        print('ServicePool [ assigned_services ]: ', self.assigned_services_list, '\n')
        print('ServicePool [ assignables ]: ', self.assignables_list, '\n') 
