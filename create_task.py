#!/usr/bin/env python3

import argparse
import gaa_lib_config
import subprocess
import sys
import os

def explanation_info():
    print("EXPLANATION: this program execute GAA task. please place this script on your home directory and execute this program on same dir of dl_image_manager")

class GAATaskManager():
    #need to execute this program on same dir of "dl_image_manager"
    DL_IMANAGE_MANAGER_DIR = "./dl_image_manager/"

    def __init__(self):
        if os.path.exists(self.DL_IMANAGE_MANAGER_DIR) is False:
            explanation_info()
            raise ValueError("%s not found" % (self.DL_IMANAGE_MANAGER_DIR))



    def create_task(self, dl_type):
        #self.__do_learn_sh(dl_type)
        self.__backup_dl_image_manager_dir()

    def __do_learn_sh(self, dl_type):
        os.chdir(self.DL_IMANAGE_MANAGER_DIR)
        command = ["pwd"]
        res = subprocess.check_output(command)
        print(res)

        if dl_type == "ssd":
            print("INFO: ssd")
            command = ["./learn_batch.sh", "ssd"]
            res = subprocess.check_output(command)
        elif dl_type == "resnet34":
            print("INFO: resnet34")
            command = ["./learn_batch.sh", "resnet34"]
            res = subprocess.check_output(command)
        else:
            raise ValueError("invalid dl_type")

        os.chdir("../")

    def __backup_dl_image_manager_dir(self):
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("task_name", type=str)
    parser.add_argument("--memo", type=str)
    parser.add_argument("--explanation_of_this", type=str)
    args = parser.parse_args()

    if args.explanation_of_this is not None:
        explanation_info()
        sys.exit(0)


    gaa_task_manager = GAATaskManager()
    gaa_task_manager.create_task(args.task_name)


