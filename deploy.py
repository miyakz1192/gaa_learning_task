#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
import shutil
from collections import defaultdict

import gaa_lib_loader
from easy_sshscp import *
import gaa_constants
import gaa_learning_task_common

import gaa_learning_task_config

import tarfile
import re

def explanation_info():
    print("EXPLANATION:")

class GAALearningOutputDeployManager():
    LOCAL_LEARNING_TASK_DIR = "./gaa_learning_task/"
    LOCAL_LEARNING_TASK_OUTPUT_DIR = "./output/"

    def __init__(self, deploy_target_task_name):
        self.deploy_target_task_name = deploy_target_task_name

        target_dir = self.LOCAL_LEARNING_TASK_OUTPUT_DIR + \
                     self.deploy_target_task_name

        if os.path.exists(target_dir) is False:
            err_msg = "ERROR: task dir not found(%s)" % (target_dir)
            print(err_msg)
            raise ValueError(err_msg)

    def __deploy_aux(self, dl_type):
        if not(dl_type in gaa_dl_services):
            raise ValueError("invalid dl_type")
        print("INFO: %s" % (dl_type))

    def __print_pwd(self):
        command = ["pwd"]
        res = subprocess.check_output(command)
        print(res)

    #targz is TarFile object
    def __extract_best_weight_file(self, targz):
        r = re.compile(".*/%s" % (gaa_constants.gaa_best_weight_file_name))
        weights = []
        for i in targz.getmembers():
            if r.match(i.name):
                weights.append(i)

        #search newest file
        if len(weights) == 0:
            print("ERROR: not best weight file not found")
        
        best_weight_file = max(weights, key = lambda x: x.mtime)
        temp_file_name = "./temp/%s" % (gaa_constants.gaa_best_weight_file_name)
        outfile = open(temp_file_name,'wb')
        outfile.write(targz.extractfile(best_weight_file).read())
        outfile.close()
        return temp_file_name

    def deploy(self):
        ssh = EasySSHSCP()
        for dl_type in gaa_constants.gaa_dl_services:
            file_name = self.LOCAL_LEARNING_TASK_OUTPUT_DIR + \
                        self.deploy_target_task_name + "/" + \
                        gaa_learning_task_common.dl_output_file_name(dl_type)
            print("INFO: extracting best weight file from %s" % (file_name))
            targz =  tarfile.open(file_name)
            best_weight_file_name = self.__extract_best_weight_file(targz)

            print("INFO: file found, and send it to service")
            remote_host = dl_type
            remote_path = gaa_constants.gaa_service_remote_weights_path[dl_type]
            ssh.upload(best_weight_file_name, remote_host, remote_path)

            print("INFO: %s%s uploaded successfully" % (remote_path,os.path.basename(best_weight_file_name)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task_name", type=str)
    parser.add_argument("--memo", type=str)
    parser.add_argument("--explanation_of_this", type=str)
    args = parser.parse_args()

    if args.explanation_of_this is not None:
        explanation_info()
        sys.exit(0)

    gaa_deploy = GAALearningOutputDeployManager(args.task_name)
    gaa_deploy.deploy()
    print("INFO: program ended successfully!")

