import pickle
import sys, os
sys.path.append(os.path.abspath('.'))
from vdi import *

def read_data(plan,packs_path):

    plan_ending= '.plandata'
    os.makedirs(os.path.dirname(packs_path), exist_ok=True)
    plan_full_name= os.path.join(packs_path, plan + plan_ending)
    print(f'\nTrying to read saved data from "{plan_full_name}" config file\n')
    plan_data_list=[]
    with open(plan_full_name, 'rb') as f:

            plan_data_list= pickle.load(f)

    return plan_data_list


data= read_data(
    plan="1",
    packs_path=r'C:\Users\Anakim\Documents\xrm-vdi-pack\.saved'
)

for plan_data_dict in data:
    service_name = plan_data_dict['service_name']
    print(f'\n+ service name: {service_name}')
    service_pool = plan_data_dict['service_pool']
    service_provider = plan_data_dict['service_provider']
    authenticator = plan_data_dict['authenticator']
    transport = plan_data_dict['transport']
    permissions = plan_data_dict['permissions']
    service_pool.get_logs()
    service_provider.get_logs()
    authenticator.get_logs()
    transport.get_logs()
    permissions.get_logs()

            
 



