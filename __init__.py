"""
This module initializes and sets up the Fooocus extension for ComfyUI.
It handles folder creation, file downloads, and node mapping for the extension.
"""

import os
import importlib
import shutil
import folder_paths
import filecmp

def create_folder_and_update_paths(folder_name):
    folder_path = os.path.join(folder_paths.models_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    folder_paths.folder_names_and_paths[folder_name] = (
        [
            folder_path,
            *folder_paths.folder_names_and_paths.get(folder_name, [[], set()])[0]
        ],
        folder_paths.supported_pt_extensions
    )
create_folder_and_update_paths("fooocus_expansion")
create_folder_and_update_paths("inpaint")
create_folder_and_update_paths("ipadapter")

from .py.fooocus_modules.model_loader import load_file_from_url
from .py.fooocus_modules.config import (
    path_fooocus_expansion as fooocus_expansion_path,
)
from .py import fooocus_log


node_list = [
    "fooocus_api",
    "fooocusNodes",
    "fooocus_prompt"
]


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
for module_name in node_list:
    imported_module = importlib.import_module(
        ".py.{}".format(module_name), __name__)
    NODE_CLASS_MAPPINGS = {**NODE_CLASS_MAPPINGS,
                           **imported_module.NODE_CLASS_MAPPINGS}
    NODE_DISPLAY_NAME_MAPPINGS = {
        **NODE_DISPLAY_NAME_MAPPINGS, **imported_module.NODE_DISPLAY_NAME_MAPPINGS}


WEB_DIRECTORY = "./web"


def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f),
                                    os.path.join(dest, f),
                                    ignore)
    else:
        if not os.path.exists(dest) or not filecmp.cmp(src, dest):
            shutil.copyfile(src, dest)
            fooocus_log.log_node_info(f'Copying file from {src} to {dest}')

def get_ext_dir(subpath=None, mkdir=False):
    dir = os.path.dirname(__file__)
    if subpath is not None:
        dir = os.path.join(dir, subpath)
    dir = os.path.abspath(dir)
    if mkdir and not os.path.exists(dir):
        os.makedirs(dir)
    return dir


def install_expansion():
    src_dir = get_ext_dir("fooocus_expansion")
    if not os.path.exists(src_dir):
        fooocus_log.log_node_error(
            "prompt_expansion is not exists. Please reinstall the extension.")
        return
    if not os.path.exists(fooocus_expansion_path):
        os.makedirs(fooocus_expansion_path)
    recursive_overwrite(src_dir, fooocus_expansion_path)


def download_models():

    install_expansion()

try:
    download_models()
except:
    pass

__all__ = ['NODE_CLASS_MAPPINGS',
           'NODE_DISPLAY_NAME_MAPPINGS', "WEB_DIRECTORY"]
print("\033[0m\033[95m ComfyUI  Fooocus Nodes  :\033[0m \033[32mloaded\033[0m")
