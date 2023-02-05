### NOTICE: DO NOT CHANGE HERE START ###
from collections import defaultdict

backup_target_dir = defaultdict()
### NOTICE: DO NOT CHANGE HERE END ###

#configurable part start
##Please set SSD servers (pytorch) directory
backup_target_dir["ssd"] = "/home/a/pytorch_ssd/"

##please set ResNet servers(ResNet) directory
backup_target_dir["resnet34"] = "/home/a/resset/"

