# Methods to retrieve data from text files
import os
import shutil


def get_dir_list(path):
    filename = os.path.join(path, 'directories', 'directories.txt')
    with open(filename, 'r') as dir_file:
        return dict(line.strip().split(':') for line in dir_file if line and not line.isspace())


def get_emails(path):
    filename = os.path.join(path, 'emails', 'emails.txt')
    with open(filename, 'r') as dir_file:
        return [line.strip() for line in dir_file if line and not line.isspace()]


def clean_temp(base_path):
    temp_path = os.path.join(base_path, 'temp')
    shutil.rmtree(temp_path)
    os.mkdir(temp_path)
