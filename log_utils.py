import os


class FolderLogger:
    def __init__(self, base_path):
        self.base_path = base_path
        self.logfiles = {}

    def initialise(self, dir_list):
        for directory in dir_list:
            dir_path = os.path.join(self.base_path, directory)
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            filename = os.path.join(dir_path, directory + '.log')
            self.logfiles[directory] = filename

    def write(self, dir_name, text):
        with open(self.logfiles[dir_name], 'a') as file:
            file.write('\n')
            file.write(text)
