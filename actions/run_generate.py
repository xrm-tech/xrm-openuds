import pickle
import sys, os
sys.path.append(os.path.abspath('.'))
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
from st2common.runners.base_action import Action
from vdi import *
import apiclient
import traceback


class RunGenerate(Action):
    __result= None
    packs_path= '/opt/stackstorm/packs/saved/'    

    
    def __get_data_by_pool_name (self, 
                                 src_broker_connection_param,
                                 src_broker_ip,
                                 src_broker_auth,
                                 src_broker_user,
                                 src_broker_pwd, 
                                 dst_broker_ip,
                                 dst_broker_auth,
                                 dst_broker_user,
                                 dst_broker_pwd,
                                 dst_ovirt_fqdn,
                                 dst_ovirt_user,
                                 dst_ovirt_pwd,
                                 dst_ovirt_cluster_uuid,
                                 dst_ovirt_sd_uuid,
                                 dst_ovirt_golden_vm_uuid, 
                                 sn):
        
        spl = ServicePool(
            primary_broker=src_broker_connection_param,
            pool_name=sn
        )
        spl.get_logs()    
        
        spr = ServiceProvider(
            primary_broker=src_broker_connection_param,
            service_pool_data=spl.data_dict
        )
        spr.get_logs()

        a = Authenticator(
            primary_broker=src_broker_connection_param,
            pool_groups_list=spl.groups_list,
            pool_assigned_services=spl.assigned_services_list
        )
        a.get_logs()

        t = Transport(
            primary_broker=src_broker_connection_param,
            pool_transports_list=spl.transports_list
        )
        t.get_logs()

        os = OSManager(
            primary_broker=src_broker_connection_param,
            id=spl.os_manager_id    
        )
        os.get_logs()

        tokens = ActorTokens(
            primary_broker=src_broker_connection_param
        )
        tokens.get_logs()

        p = Permissions(
            primary_broker=src_broker_connection_param,
            service_pool_param=spl,
            service_provider_param=spr,
            authenticator_param=a,
            transport_param=t
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
            
            'dst_ovirt_fqdn': dst_ovirt_fqdn,
            'dst_ovirt_user': dst_ovirt_user,
            'dst_ovirt_pwd': dst_ovirt_pwd,
            'dst_ovirt_cluster_uuid' : dst_ovirt_cluster_uuid,
            'dst_ovirt_sd_uuid': dst_ovirt_sd_uuid,
            'dst_ovirt_golden_vm_uuid': dst_ovirt_golden_vm_uuid,
            
            'service_name': sn,
            'service_pool': spl,
            'service_provider': spr,
            'authenticator': a,
            'transport': t,
            'osmanager': os,
            'permissions': p,
            'actor_tokens': tokens,
        }

        return service_data


    def __save_plan_data(self, plan_data, plan:str):        

        plan_ending= '.plandata'
        os.makedirs(os.path.dirname(self.packs_path), exist_ok=True)
        plan_full_name= os.path.join(self.packs_path, plan + plan_ending)


        with open(plan_full_name, 'wb') as f:
            pickle.dump(plan_data, f)


    def run(self, plan_name):
        
        src_broker_connection= apiclient.Client(
            host= self.config['01_broker_primary_ip'],
            username= self.config['02_broker_primary_username'],
            auth= self.config['03_broker_primary_authenticator'],
            password= self.config['04_broker_primary_password'],
        )        

        try: 
       
            src_broker_connection.login()
            service_pools_str= self.config['09_service_pool_name']

            if (service_pools_str[-1] == ';'):
                service_pools_str= service_pools_str[:-1]

            service_pools_names_list= service_pools_str.split(";") 
            service_pools_data_list=[]

            for service_pool_name in service_pools_names_list:

                try:

                    print(f'\n\nTrying to get data from broker for "{service_pool_name}" plan name\n\n')    
                    service_pool_data= self.__get_data_by_pool_name(
                        sn= service_pool_name,
                        src_broker_connection_param= src_broker_connection,
                        src_broker_ip= self.config['01_broker_primary_ip'],
                        src_broker_user= self.config['02_broker_primary_username'],
                        src_broker_pwd= self.config['04_broker_primary_password'],
                        src_broker_auth= self.config['03_broker_primary_authenticator'],
                        dst_broker_ip= self.config['05_broker_secondary_ip'],
                        dst_broker_user= self.config['06_broker_secondary_username'],
                        dst_broker_pwd= self.config['08_broker_secondary_password'],
                        dst_broker_auth= self.config['07_broker_secondary_authenticator'],
                        dst_ovirt_fqdn= self.config['10_ovirt_secondary_fqdn'],
                        dst_ovirt_user= self.config['11_ovirt_secondary_username'],
                        dst_ovirt_pwd= self.config['12_ovirt_secondary_password'],
                        dst_ovirt_cluster_uuid= self.config['13_ovirt_secondary_cluster_uuid'],
                        dst_ovirt_sd_uuid= self.config['14_ovirt_secondary_storagedomain_uuid'],
                        dst_ovirt_golden_vm_uuid= self.config['15_ovirt_secondary_golden_vm_uuid'],)
                    
                    if service_pool_data:                       
                        service_pools_data_list.append(service_pool_data)         

                except Exception:                
                    traceback.print_exc()

            self.__save_plan_data(
                plan= plan_name, 
                plan_data= service_pools_data_list,                
            )

            self.__result= True

        except Exception as e:            
            traceback.print_exc()

        finally:
            try:
                src_broker_connection.logout()    

            except Exception as e:               
                traceback.print_exc()

            return self.__result

