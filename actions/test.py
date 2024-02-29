import base64
import os
import requests

def parse_storage_to_json(primary_storages,secondary_storages):
    """
    Sample output:

    [
    { primary_type: "nfs", primary_path: "/nfs_dom", primary_addr: "192.168.0.1", secondary_type: "nfs", secondary_path: "/nfs_dom_replica", secondary_addr: "192.168.0.1" },
    { primary_type: "nfs", primary_path: "/nfs_dom", primary_addr: "192.168.0.1", secondary_type: "nfs", secondary_path: "/nfs_dom_replica", secondary_addr: "192.168.0.1" }
    ]
    """
    ret = []
    item = {}
    for stg in primary_storages.split(";"):
        try:
            type= stg.split("://")[0]
            addr = stg.split("://")[1].split(":")[0]
            path = "/"+stg.split(":/")[2].split("/")[0]
            print (type +" "+ addr+" "+path)
            item={"primary_type":type,"primary_addr":addr,"primary_path":path}
            ret.append(item)
        except Exception as e:
            print("Exception in parse_storage_to_json: " + str(e))
    idx = 0
    for stg in secondary_storages.split(";"):
        try:
            type= stg.split("://")[0]
            addr = stg.split("://")[1].split(":")[0]
            path = "/"+stg.split(":/")[2].split("/")[0]
            print (str(idx)+" "+type +" "+ addr+" "+path)
            ret[idx]["secondary_type"] = type;
            ret[idx]["secondary_addr"] = addr;
            ret[idx]["secondary_path"] = path;
        except Exception as e:
            print("Exception in parse_storage_to_json: " + str(e))
        idx+=1
            
    return ret

jsonout = parse_storage_to_json("nfs://192.168.122.210:/nfs_dom/;nfs://192.168.122.210:/nfs_backup/","nfs://192.168.122.210:/nfs_dom_replica/;nfs://192.168.122.210:/nfs_backup_replica/;nfs://192.168.122.210:/nfs_backup/")
print (jsonout)