#common constants or functions

import gaa_lib_loader
from easy_sshscp import *
from gaa_constants import *
from gaa_common import *

def dl_output_file_name(dl_type):
    check_dl_type(dl_type)
    short_file_name = dl_type
    return "%s.tar.gz" % (short_file_name)

def dl_image_manager_file_name(dl_type):
    check_dl_type(dl_type)
    return "%s_dl_image_manager.tar.gz" % (dl_type)
