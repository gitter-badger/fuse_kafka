#!/usr/bin/env python
""" @package fuse_kafka
Startup script for fuse_kafka.
"""
import sys, getopt, json, glob, os, subprocess
""" CONFIGURATIONS_PATHS is the list of paths where the init script
will look for configurations """
CONFIGURATIONS_PATHS = ["./conf/*", "/etc/fuse_kafka/*", "/etc/*.txt"]
class Configuration:
    """ Utility class to load configurations from properties files """
    def get_property(self, path, name):
        """ Get a property from a well defined property file.

        path - configuration file path
        name - property name

        Returns the first property value found in the given path with the
        given name, None if it was not found
        """
        with open(path) as f:
            for line in f.readlines():
                line = line.split('=', 1)
                if len(line) == 2 and line[0] == name:
                    return line[1].strip()
    def includes_subdir(self, dirs, subdir):
        """ Checks if a subdirectory is included in a list of prefix.

        dirs    - list of prefixes
        subdir  - path to check for prefix

        Returns True if dirs contains a prefix of subdir, False
        otherwise.
        """
        for dir in dirs:
            if subdir.startswith(dir):
                return True
        return False
    def exclude_directories(self, paths, prefixes):
        """ Exclude directories from a list of directories based on
        prefixes

        paths       - list of paths from which to exclude prefixs
        prefixes    - list of prefixes to exclude

        Returns the path list with excluded directories
        """
        return [path for path in paths if not includes_subdir(prefixes,
            os.path.realpath(path))]
    def __init__(self, configurations = CONFIGURATIONS_PATHS):
        self.configurations = configurations
        self.sleeping = False
        self.load()
    def parse_line(self, line, conf):
        """ Parse a configuration line

        line - the line to parse
        conf - a dictionary which will be updated based on the parsing

        Returns the configuration updated configuration based on the
        line
        """
        line = line.split('=', 1)
        if len(line) == 2:
            key = line[0]
            if line[0].startswith('monitoring_logging_') \
                    or line[0].startswith('fuse_kafka_') \
                    or line[0] == 'monitoring_top_substitutions':
                key = key.replace('monitoring_', '')
                key = key.replace('fuse_kafka_', '')
                key = key.replace('logging_', '').replace('top_', '')
                if not key in conf.keys(): conf[key] = []
                parsed = json.loads(line[1])
                if type(parsed) is dict:
                    for parsed_key in parsed.keys():
                        conf[key].append(parsed_key)
                        conf[key].append(parsed[parsed_key])
                else:
                    conf[key].extend(parsed)
    def is_sleeping(self):
        """ Returns True if fuse_kafka is in sleep mode """
        return os.path.exists('/var/run/fuse_kafka_backup')
    def load(self):
        """ Loads configuration from configurations files """
        self.conf = {}
        for globbed in self.configurations:
            for config in glob.glob(globbed):
                with open(config) as f:
                    for line in f.readlines():
                        self.parse_line(line, self.conf)
        if self.is_sleeping():
            self.conf['directories'] = exclude_directories(
               self.conf['directories'], self.conf['sleep'])
        if 'sleep' in self.conf: del self.conf['sleep']
    def args(self):
        """ Returns the fuse_kafka binary arguments based on the
        parsed configuration """
        result = []
        for key in self.conf.keys():
            result.append(' --' + key)
            for item in self.conf[key]:
                result.append(item)
        return result
    def __str__(self):
        return " ".join(self.args())
class FuseKafkaService:
    """ Utility class to run multiple fuse_kafka processes as one service """
    def do(self, action):
        """ Actually run an action 

        action - the action name

        """
        self.prefix = ["fuse_kafka", "_", "-oallow_other", "-ononempty",
                "-s", "-omodules=subdir,subdir=.", "-f", "--"]
        getattr(self, action)()
    def start(self):
        """ Starts fuse_kafka processes """
        env = os.environ.copy()
        env["PATH"] = ".:" + env["PATH"]
        env["LD_LIBRARY_PATH"] += ":/usr/lib"
        self.configuration = Configuration()
        directories = self.configuration.conf['directories']
        for directory in directories:
            self.configuration.conf['directories'] = [directory]
            print(self.configuration.args())
            subprocess.Popen(self.prefix + self.configuration.args(), env = env)
            print str(self.configuration)
    def stop(self):
        """ Stops fuse_kafka processes """
        subprocess.call(["pkill", "-f", " ".join(self.prefix)])
    def restart(self):
        """ Stops and starts fuse_kafka processes """
        self.stop()
        self.start()
    def status(self):
        """ Displays the status of fuse_kafka processes """
        print("undefined")
if __name__ == "__main__":
    FuseKafkaService().do(sys.argv[1])
