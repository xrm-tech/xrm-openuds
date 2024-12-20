import pickle
import sys, os

sys.path.append(os.path.abspath('.'))
sys.path.append('/opt/stackstorm/packs/xrm_openuds/')
from st2common.runners.base_action import Action
from vdi import Failover


class RunFailOver(Action):
    __result = None
    packs_path = '/opt/stackstorm/packs/saved/'


    def run(self, plan_name):
        return Failover.run(self.packs_path, plan_name)
