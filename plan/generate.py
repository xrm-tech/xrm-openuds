import pickle
import sys, os

sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
import apiclient
from vdi import Authenticator, ServicePool, ServiceProvider, Transport, Permissions

class Generate:
    def __get_data_by_pool_name (src_broker_connection_param,
                                 src_broker_ip,
                                 src_broker_auth,
                                 src_broker_user,
                                 src_broker_pwd, 
                                 dst_broker_ip,
                                 dst_broker_auth,
                                 dst_broker_user,
                                 dst_broker_pwd, 
                                 sn):
        
        spl = ServicePool(
            primary_broker= src_broker_connection_param,
            pool_name= sn
        )
        spl.get_logs()    

        spr = ServiceProvider(
            primary_broker= src_broker_connection_param,
            service_pool_data= spl.data_dict
        )            
        spr.get_logs()

        a = Authenticator(
            primary_broker= src_broker_connection_param,
            pool_groups_list= spl.groups_list,
            pool_assigned_services= spl.assigned_services_list
        )
        a.get_logs()

        t = Transport(
            primary_broker= src_broker_connection_param,
            pool_transports_list= spl.transports_list
        )
        t.get_logs()

        p = Permissions(
            primary_broker= src_broker_connection_param,
            service_pool_param= spl,
            service_provider_param= spr,
            authenticator_param= a,
            transport_param= t
        )
        p.get_logs()

        service_data= {
            'src_broker_ip': src_broker_ip,
            'src_broker_user': src_broker_user,
            'src_broker_auth': src_broker_auth,
            'src_broker_pwd': src_broker_pwd,

            'dst_broker_ip': dst_broker_ip,
            'dst_broker_user': dst_broker_user,
            'dst_broker_auth': dst_broker_auth,            
            'dst_broker_pwd': dst_broker_pwd, 

            'service_name': sn,
            'service_pool': spl,
            'service_provider': spr,
            'authenticator': a,
            'transport': t,
            'permissions': p
        }

        return service_data


    def __save_plan_data(plan_data, packs_path:str, plan:str):        

        plan_ending= '.plandata'
        os.makedirs(os.path.dirname(packs_path), exist_ok=True)
        plan_full_name= os.path.join(packs_path, plan + plan_ending)


        with open(plan_full_name, 'wb') as f:
            pickle.dump(plan_data, f)


    def run(config, packs_path:str, plan:str):
        
        src_broker_connection= apiclient.Client(
            host= config['01_broker_primary_ip'],
            username= config['02_broker_primary_username'],
            auth= config['03_broker_primary_authenticator'],
            password= config['04_broker_primary_password'],
        )

        result = False        

        try: 
       
            src_broker_connection.login()
            service_pools_str= config['09_service_pool_name']

            if (service_pools_str[-1] == ';'):
                service_pools_str= service_pools_str[:-1]

            service_pools_names_list= service_pools_str.split(";") 
            service_pools_data_list=[]

            for service_pool_name in service_pools_names_list:

                try:

                    print(f'\n\nTrying to get data from broker for "{service_pool_name}" plan name\n\n')    
                    service_pool_data= Generate.__get_data_by_pool_name(
                        sn= service_pool_name,
                        src_broker_connection_param= src_broker_connection,
                        src_broker_ip= config['01_broker_primary_ip'],
                        src_broker_user= config['02_broker_primary_username'],
                        src_broker_pwd= config['04_broker_primary_password'],
                        src_broker_auth= config['03_broker_primary_authenticator'],
                        dst_broker_ip= config['05_broker_secondary_ip'],
                        dst_broker_user= config['06_broker_secondary_username'],
                        dst_broker_pwd= config['08_broker_secondary_password'],
                        dst_broker_auth= config['07_broker_secondary_authenticator'])
                    
                    if service_pool_data:                       
                        service_pools_data_list.append(service_pool_data)         



                except Exception as e:
                    print(e)
                    return False

            Generate.__save_plan_data(
                packs_path= packs_path,
                plan= plan, 
                plan_data= service_pools_data_list,                
            )

            result = True

        except Exception as e:
            raise Exception('Caught exception: {}'.format(e))

        finally:
            try:
                src_broker_connection.logout()    

            except Exception as e:
                print(e)

            return result