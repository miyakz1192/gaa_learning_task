#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
import shutil

import gaa_lib_loader
from easy_sshscp import *

import gaa_learning_task_config

def explanation_info():
    print("EXPLANATION: this program execute GAA task. please place this script on your home directory and execute this program on same dir of dl_image_manager")

class GAATaskManager():
    #need to execute this program on same dir of "dl_image_manager"
    DL_IMANAGE_MANAGER_DIR = "/dl_image_manager/"
    DL_IMANAGE_MANAGER_DATA_SET_DIR = "data_set/"
    LEARNING_TASK_DIR = "./gaa_learning_task/"
    LEARNING_TASK_OUTPUT_DIR = "./output/"

    def __init__(self, task_name):
        self.task_name = task_name

        if os.path.exists("../" + self.DL_IMANAGE_MANAGER_DIR) is False:
            explanation_info()
            raise ValueError("%s not found" % (self.DL_IMANAGE_MANAGER_DIR))
        
        output_dir = self.LEARNING_TASK_OUTPUT_DIR + self.task_name
        if os.path.exists(output_dir) is True:
            msg = "ERROR: %s is already exists" % (output_dir)
            print(msg)
            raise ValueError(msg)

        os.makedirs(output_dir)

    def create_task(self, dl_type):
        if not(dl_type == "ssd" or dl_type == "resnet34"):
            raise ValueError("invalid dl_type")
        print("INFO: %s" % (dl_type))
        self.__do_learn_sh(dl_type)
        self.__backup_dl_image_manager_dir(dl_type)
        self.__backup_deep_learning_and_download(dl_type)

    def __print_pwd(self):
        command = ["pwd"]
        res = subprocess.check_output(command)
        print(res)

    def __get_lines(self, cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,encoding='utf-8')

        while True:
            line = proc.stdout.readline()
            if line:
                yield line

            if not line and proc.poll() is not None:
                break

    def __do_learn_sh(self, dl_type):
        os.chdir("../" + self.DL_IMANAGE_MANAGER_DIR)
        self.__print_pwd()

        #command = ["./learn_batch2.sh", dl_type] # for debug
        command = ["./learn_batch.sh", dl_type] # for production run
        for res in self.__get_lines(command):
            sys.stdout.write(res) #avoid from multiple LF
            sys.stdout.flush()

#        res = subprocess.check_output(command, stderr=subprocess.STDOUT,encoding='utf-8')
#        print(res)

        os.chdir("../" + self.LEARNING_TASK_DIR)

    def __delete_data_set_dir(self):
        try:
            shutil.rmtree("./" + self.DL_IMANAGE_MANAGER_DIR + self.DL_IMANAGE_MANAGER_DATA_SET_DIR + "/*")
        except:
            print("INFO: __delete_data_set_dir has error but ignored")

    def __backup_deep_learning_and_download(self, dl_type):
        ssh = EasySSHSCP()
        short_file_name = dl_type
        remote_host = dl_type
        tar_gz_file_path = "/tmp/%s.tar.gz" % (short_file_name)
        ssh.ssh(remote_host, "tar cvfz %s %s" % (tar_gz_file_path, gaa_learning_task_config.backup_target_dir[dl_type])) 
        ssh.download(remote_host, tar_gz_file_path, self.LEARNING_TASK_OUTPUT_DIR + "/" + self.task_name + "/")

    def __backup_dl_image_manager_dir(self, dl_type):
        os.chdir("../")
        self.__delete_data_set_dir()

        file_name = "%s_dl_image_manager.tar.gz" % (dl_type)

        command = ["tar", "cfz", self.LEARNING_TASK_DIR + self.LEARNING_TASK_OUTPUT_DIR + "/" + self.task_name + "/" + file_name , "./" + self.DL_IMANAGE_MANAGER_DIR]
        subprocess.check_output(command, stderr=subprocess.STDOUT,encoding='utf-8')
        os.chdir(self.LEARNING_TASK_DIR)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task_name", type=str)
    parser.add_argument("--memo", type=str)
    parser.add_argument("--explanation_of_this", type=str)
    parser.add_argument("--algo", type=str, default="all")
    args = parser.parse_args()

    if args.explanation_of_this is not None:
        explanation_info()
        sys.exit(0)

    gaa_task_manager = GAATaskManager(args.task_name)

    if args.algo == "all":
        gaa_task_manager.create_task("ssd")
        gaa_task_manager.create_task("resnet34")
    elif args.algo == "ssd":
        gaa_task_manager.create_task("ssd")
    elif args.algo == "resnet34":
        gaa_task_manager.create_task("resnet34")
    else:
        print("ERROR: invalid algo %s" % (args.algo))
        raise ValueError("")

    print("INFO: program finished successfully!!!")


