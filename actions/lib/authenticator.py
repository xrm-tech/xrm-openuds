import sys
sys.path.append('/etc/apiclient')
import apiclient

class Authenticator:

    perm_class= 'authenticators'
    
    __primary_broker_connection: apiclient.Client
    __pool_groups_list:list
    __pool_assigned_services_list:list
    __ids_list:list
    __user_ids_list:list
    data_list:list
    groups_list:list
    users_list:list

    def __init__(self, primary_broker, pool_groups_list, pool_assigned_services):

        self.__primary_broker_connection= primary_broker
        self.__pool_groups_list= pool_groups_list
        self.__pool_assigned_services_list= pool_assigned_services
        self.__ids_list= self.__get_all_auth_ids()        
        self.data_list= self.__get_all_auth_data()
        self.groups_list= self.__get_all_groups()
        self.__user_ids_list= self.__get_all_user_ids()
        self.users_list= self.__get_all_users()

    #TODO: exclude int db data ???
    def __get_all_auth_ids(self):
        auth_id_list= []
        
        for pool_group in self.__pool_groups_list:
            id_dict={'auth_id':pool_group['auth_id'], 'group_id':pool_group['id']}
            auth_id_list.append(id_dict)

        return auth_id_list

    def __get_all_auth_data(self):
        data_list=[]

        for ids_elem in self.__ids_list:          
            auth_id= ids_elem['auth_id']
            data_list.append(self.__primary_broker_connection.get_auth(auth_id))

        return data_list

    def __get_all_groups(self):
        groups= []

        for id_elem in self.__ids_list:
            group_data= self.__primary_broker_connection.get_auth_group(
                auth_id=id_elem['auth_id'],
                group_id=id_elem['group_id']
            )
            groups.append(group_data)
        
        return groups
    
    def __get_all_user_ids(self):
        user_ids=[]

        for id_elem in self.__pool_assigned_services_list:
            owner= id_elem['owner_info']  
            auth_id= owner['auth_id']
            user_id= owner['user_id']  
            owner_id= {'auth_id':auth_id, 'user_id':user_id}
            user_ids.append(owner_id)
        
        return user_ids

    def __get_all_users(self):
        users_list=[]

        for user_id_elem in self.__user_ids_list:
            user_data= self.__primary_broker_connection.get_auth_user(
                auth_id= user_id_elem['auth_id'],
                user_id= user_id_elem['user_id']
            )
            users_list.append(user_data)

        return users_list

    def get_logs(self):

        print('Authenticator [ data ]: ', self.data_list , '\n')
        print('Authenticator [ groups ]: ', self.groups_list, '\n') 
        print('Authenticator [ users ]: ', self.users_list, '\n') 