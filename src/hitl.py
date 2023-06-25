from typing import Any, Optional, Callable, Dict, List, Tuple, Set, TextIO
import yaml
import copy
import json

class HITL:
    def __init__(self, cfg, clusters_pred, data, save_cfg_path, save_res_path="") -> None:
        self.cfg = copy.deepcopy(cfg)
        self.clusters_pred = copy.deepcopy(clusters_pred)
        self.data = data
        self.interact = True
        self.log = print
        self.cfg_changed = False
        self.save_cfg_path = save_cfg_path
        self.save_res_path = save_res_path
    
    def clusters_command(self, arg: str = ""):
        """Show members in a cluster id"""
        if len(arg) == 0:
            self.log(f"All cluster members: {self.clusters_pred}")
        else:
            try:
                c = int(arg)
            except:
                raise TypeError('cluster id should be integal')
            assert c>=0 and c<len(self.clusters_pred), f"cluster id should be in [0, {len(self.clusters_pred)})"
            self.log(f"The cluster {c}'s member: {self.clusters_pred[c]}")
        
    def samplesc_command(self, arg: str = ""):
        """Show event sequence in a cluster"""
        try:
            c = int(arg)
        except:
            raise TypeError('cluster id should be integal')
        assert c>=0 and c<len(self.data), f"s should be in [0, {len(self.data)})"
        samples = self.clusters_pred[c]
        self.log(f"In cluster id {c}:")
        for s in samples:
            self.log(f"The sample {s}'s content: {self.data[s]}")

    def samples_command(self, arg: str = ""):
        """Show event sequence in a data sample"""
        input = arg.split(' ')
        for s in input:
            try:
                s = int(s)
            except:
                raise TypeError('sample id should be integal')
            assert s>=0 and s<len(self.data), f"s should be in [0, {len(self.data)})"
            self.log(f"The sample {s}'s content: {self.data[s]}")

    def addrs_command(self, arg: str = ""):
        """Add content event id to be removed when processing data"""
        assert isinstance(arg, str), self.log('The event id should be string')
        self.cfg['remove_ids'].append(arg)
        self.cfg_changed = True
        self.log(f"The new cfg remove_ids list is {self.cfg['remove_ids']}")

    def setk_command(self, arg: str = ""):
        """Change maximum length of the event sequence to K"""
        assert isinstance(arg, int), self.log('The max length should be integral')
        self.cfg['max_K'] = arg
        self.cfg_changed = True

    def mergec_command(self, arg: str = ""):
        """Merge c1 and c2 clusters by moving all samples from c2 to c1"""
        c1, c2 = arg.split(' ')
        c1, c2 = int(c1), int(c2)
        self.clusters_pred[c1].extend(self.clusters_pred[c1])
        self.clusters_pred[c2] = []
        self.log(f"Merging cluster {c2} into {c1}")
        self.log(f"New clusters: {self.clusters_pred}")
    
    def addc_command(self, arg: str = ""):
        """Add a new empty cluster"""
        self.clusters_pred.append([])
        self.log(f"New clusters: {self.clusters_pred}")
    
    def moves_command(self, arg: str = ""):
        """Move sample from old cluster to new one"""
        try:
            s, old_c, new_c = arg.split(' ')
        except:
            ValueError("Three arguments <sample_id> <src_cluster> <dst_cluster> should be given")
        self.clusters_pred[int(old_c)].remove(int(s))
        self.clusters_pred[int(new_c)].append(int(s))
        self.log(f"Moved sample {s} from cluster {old_c} to cluster {new_c}")
        # if input("(HITL_HC) Do you want to see new clusters? (y or n)").lower() in ['yes', 'y']:
        self.log(f"All cluster members: {self.clusters_pred}")

    def printc_command(self, arg=None):
        self.log(self.cfg)

    def quit_command(self, arg: str = "") -> None:
        """Finish execution"""
        self.interact = False

    def help_command(self, command: str = "") -> None:
        """Give help on given `command`. If no command is given, give help on all"""

        if command:
            possible_cmds = [possible_cmd for possible_cmd in self.commands()
                             if possible_cmd.startswith(command)]
            if len(possible_cmds) == 0:
                self.log(f"Unknown command {repr(command)}. Possible commands are:")
                possible_cmds = self.commands()
            elif len(possible_cmds) > 1:
                self.log(f"Ambiguous command {repr(command)}. Possible expansions are:")
        else:
            possible_cmds = self.commands()

        for cmd in possible_cmds:
            method = self.command_method(cmd)
            self.log(f"{cmd:20} -- {method.__doc__}")

    def commands(self) -> List[str]:
        """Return a list of commands"""

        cmds = [method.replace('_command', '')
                for method in dir(self.__class__)
                if method.endswith('_command')]
        cmds.sort()
        return cmds
    
    def command_method(self, command: str) -> Optional[Callable[[str], None]]:
        """Convert `command` into the method to be called.
           If the method is not found, return `None` instead."""

        if command.startswith('#'):
            return None  # Comment

        possible_cmds = [possible_cmd for possible_cmd in self.commands()
                         if possible_cmd.startswith(command)]
        if len(possible_cmds) != 1:
            self.help_command(command)
            return None

        cmd = possible_cmds[0]
        return getattr(self, cmd + '_command')
    
    def execute(self, command: str) -> None:
        """Execute `command`"""
        sep = command.find(' ')
        if sep > 0:
            cmd = command[:sep].strip()
            arg = command[sep + 1:].strip()
        else:
            cmd = command.strip()
            arg = ""

        method = self.command_method(cmd)
        if method:
            method(arg)

    def _save_cfg(self):
        if self.save_cfg_path != "":
            with open(self.save_cfg_path, 'w') as fp:
                yaml.dump(self.cfg, fp, default_flow_style=False)

    def _save_res(self):
        if self.save_res_path != "":
            res = dict()
            cluster_id = 0
            for cluster in self.clusters_pred:
                if len(cluster) == 0:
                    continue
                tmp = [' '.join(self.data[c]) for c in cluster]
                res[cluster_id] = tmp
                cluster_id+=1
            with open(self.save_res_path, 'w') as fp:
                json.dump(res, fp, indent=0)

    def rf_command(self, arg):
        """Do nothing cmd, just to refresh print"""
        self.log()

    def run(self):
        self.log('*'*20+' Human Inspection on HC_result Started '+'*'*20)
        while self.interact:
            command = input("(HITL_HC) ")
            self.execute(command)
        if self.cfg_changed:
            self._save_cfg()
        self._save_res()
        
        self.log('*'*20+' Human Inspection on HC_result Ended '+'*'*20)