import base64
import os
import requests
import sys
from st2common.runners.base_action import Action

from lib.xrmcontroller import XRMBaseAction

__all__ = [
    'RunCmd'
]
CONTROLLER_ADDRESS = "http://st2:459Qdr_@xrm-controller:8080/ovirt/generate/"

def format_exception_loc():
    _, _, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    return "{}:{}".format(os.path.basename(filename), lineno)


class RunGenerate(XRMBaseAction):

    def parse_storage_to_json(self,primary_storages,secondary_storages):
        """
        Sample output:

        [
        { primary_type: "nfs", primary_path: "/nfs_dom", primary_addr: "192.168.0.1", secondary_type: "nfs", secondary_path: "/nfs_dom_replica", secondary_addr: "192.168.0.1" },
        { primary_type: "nfs", primary_path: "/nfs_dom", primary_addr: "192.168.0.1", secondary_type: "nfs", secondary_path: "/nfs_dom_replica", secondary_addr: "192.168.0.1" }
        ]
        """
        ret = []
        item = {}
        targets = {}
        idx = 0
        for stg in primary_storages.split(";"):
            try:
                fields = stg.split("://")
                type= fields[0]
                fields = fields[1].split(":/")
                #print (type +" "+ addr+" "+path)
                item={"primary_type":type}
                if type == "fcp":
                    # fcp://id
                    addr = fields[0]
                    item["primary_id"] = addr
                elif type == "iscsi":
                    # iscsi://id:/addr:port:/iqn:name
                    id = fields[0]
                    item["primary_id"] = id
                    addr = fields[1].split(":")
                    item["primary_addr"] = addr[0]
                    item["primary_port"] = addr[1]
                    vol = fields[2]
                    targets[idx] = vol
                elif type == "nfs":
                    # nfs://addr:/path
                    addr = fields[0]
                    path = "/"+fields[1]
                    item["primary_addr"] = addr
                    item["primary_path"] = path
                else:
                    print("Exception in parse_storage_to_json: Type not supported:" + type)
                    return []
                
                ret.append(item)
                idx+=1               
            except Exception as e:
                print("Exception in parse_storage_to_json: (" + format_exception_loc() + ") " + str(e))
        idx = 0
        for stg in secondary_storages.split(";"):
            try:
                fields = stg.split("://")
                type= fields[0]
                ret[idx]["secondary_type"] = type
                fields = fields[1].split(":/")
                if type == "fcp":
                    # fcp://id
                    addr = fields[0]
                    ret[idx]["secondary_id"] = addr
                elif type == "iscsi":
                    # iscsi://id:/addr:port:/iqn:name
                    id = fields[0]
                    ret[idx]["secondary_id"] = id
                    addr = fields[1].split(":")
                    ret[idx]["secondary_addr"] = addr[0]
                    ret[idx]["secondary_port"] = addr[1]
                    vol = fields[2]
                    item["targets"] = {targets[idx]: vol}
                elif type == "nfs":
                        # nfs://addr:/path
                        addr = fields[0]
                        path = "/"+fields[1]
                        #print (str(idx)+" "+type +" "+ addr+" "+path)
                        ret[idx]["secondary_addr"] = addr
                        ret[idx]["secondary_path"] = path
                else:
                    print("Exception in parse_storage_to_json: Type not supported:" + type)
                    return []   
            except Exception as e:
                print("Exception in parse_storage_to_json: (" + format_exception_loc() + ") " + str(e))
            idx+=1
        print (ret)
        return ret

    def parse_params_to_json(self, params_str):
        """
        Sample output:

        [
        "modify_key=Default",
        "delete_key=~",
        ]
        """
        ret = []
        for param in params_str.split(";"):
            ret.append(param)
        print (ret)
        return ret
    
    def run(self, plan_name):
        #self.login()
        data = {"site_primary_url": self.config['01_site_primary_url'],\
                "site_primary_username": self.config['02_site_primary_username'],\
                "site_primary_password": self.config['03_site_primary_password'],\
                "site_secondary_url": self.config['04_site_secondary_url'],\
                "site_secondary_username": self.config['05_site_secondary_username'], \
                "site_secondary_password": self.config['06_site_secondary_password']}
        storage_data =  self.parse_storage_to_json(self.config['07_primary_storage'],self.config['08_secondary_storage'])
        data["storage_domains"] = storage_data

        additional_params_str = self.config['09_additional_params'].strip()
        if additional_params_str != "": data["additional_params"] = self.parse_params_to_json(additional_params_str)

        print (data)
        req = self.session.post(CONTROLLER_ADDRESS+plan_name, json=data)
        print("status", req.status_code)
        print(req.text)

        #print (self.config['01_site_primary_url'])
        #print (self.config['02_site_primary_username'])
        #print (self.config['03_site_primary_password'])
        
        if req.status_code == 200:
            return True
        else:
            sys.exit(1)
            return False
