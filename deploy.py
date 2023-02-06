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


    #targz is TarFile object
    def __extract_file_from_targz(self, targz, target_file_name):
        r = re.compile(".*/%s" % (target_file_name))
        targets = []
        for i in targz.getmembers():
            if r.match(i.name):
                targets.append(i)

        #search newest file
        if len(targets) == 0:
            print("ERROR: %s not found" % (target_file_name))
            raise ValueError("")
        elif len(targets) >= 2:
            print("WARNING: multiple %s found select newest" % (target_file_name))
        
        target_file = max(targets, key = lambda x: x.mtime)
        temp_file_name = "./temp/%s" % (target_file_name)
        outfile = open(temp_file_name,'wb')
        outfile.write(targz.extractfile(target_file).read())
        outfile.close()
        return temp_file_name

    #targz is TarFile object
    def __extract_best_weight_file(self, targz):
        return self.__extract_file_from_targz(targz,\
                  gaa_constants.gaa_best_weight_file_name)

    #targz is TarFile object
    def __extract_data_set_file(self, targz):
        return self.__extract_file_from_targz(targz,\
                 gaa_constants.gaa_data_set_file_name)

    def __send_data_set_to_remote(self, dl_type):
        ssh = EasySSHSCP()
        file_name = self.LOCAL_LEARNING_TASK_OUTPUT_DIR + \
                    self.deploy_target_task_name + "/" + \
                    gaa_learning_task_common.dl_image_manager_file_name(dl_type)
        print("INFO: extracting data set file from %s" % (file_name))
        targz =  tarfile.open(file_name)
        data_set_file_name = self.__extract_data_set_file(targz)

        print("INFO: file found, and send it to service")
        remote_host = dl_type
        remote_temp_path = gaa_constants.gaa_service_remote_data_set_temp_path[dl_type]
        ssh.upload(data_set_file_name, remote_host, remote_temp_path)

        remote_data_set_path = gaa_constants.gaa_service_remote_data_set_path[dl_type]
        remote_temp_path = remote_temp_path + os.path.basename(data_set_file_name)

        print("INFO: %s uploaded successfully" % (remote_temp_path))
        print("INFO: extract data_set.tar.gz on remote host")
        res = ssh.ssh(remote_host, "rm -rf %s/*" % (remote_data_set_path))
        print(res[1]) #print stderr only
        res = ssh.ssh(remote_host, "tar xvfz %s -C %s" % (remote_temp_path, remote_data_set_path)) 
        print(res[1])
        res = ssh.ssh(remote_host, "mv %s/%s/* %s" % (remote_data_set_path, gaa_constants.GAA_DATA_SET_FILE_INTERNAL_DIR, remote_data_set_path)) 
        print(res[1])
        res = ssh.ssh(remote_host, "rm -rf %s/%s" % (remote_data_set_path, gaa_constants.GAA_DATA_SET_FILE_INTERNAL_DIR)) 
        print(res[1])

    def __send_best_weight_to_remote(self, dl_type):
        ssh = EasySSHSCP()
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

    def deploy(self):
        for dl_type in gaa_constants.gaa_dl_services:
            print("INFO: trying deploying about %s" % (dl_type))
            self.__send_best_weight_to_remote(dl_type)
            self.__send_data_set_to_remote(dl_type)
            print("INFO: done")



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

