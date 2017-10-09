import os
import datetime

TAB = '    '


class EmailComposer:
    def __init__(self, time_from, time_to):
        self.time_from = time_from
        self.time_to = time_to
        self.email_body = ''

    @staticmethod
    def format_dict_with_header(header, item_dict):
        result = header + '\n'
        for key in item_dict:
            result += 2 * TAB + key + '\n'
            result += 3 * TAB + item_dict[key] + '\n'
        return result

    @staticmethod
    def add_latest_to_dict(path, time, dct):
        if path not in dct or datetime.datetime.strptime(dct[path], '%Y-%m-%d %H:%M:%S') < \
                datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S'):
            dct[path] = time

    def add_block(self, block_type, content):
        files = {}
        dirs = {}
        items = {}
        for line in content.split('\n'):
            if not line or line.isspace():
                continue
            time, path = line.split('#@#', 1)
            if os.path.isfile(path if block_type != 'moved' else path.split(' -> ', 1)[1]):
                self.add_latest_to_dict(path, time, files)
            elif os.path.isdir(path if block_type != 'moved' else path.split(' -> ', 1)[1]):
                self.add_latest_to_dict(path, time, dirs)
            else:
                self.add_latest_to_dict(path, time, items)
        header = TAB + block_type[0].upper() + block_type[1:]
        block = ''
        if dirs:
            block += self.format_dict_with_header(header + ' directories:', dirs)
        if files:
            block += self.format_dict_with_header(header + ' files:', files)
        if items:
            block += self.format_dict_with_header(header + ' items:', items)
        self.email_body += block

    def is_empty(self):
        return not bool(self.email_body)

    def compose_email(self):
        if not self.is_empty():
            email = 'The following changes occurred between {0} and {1}:\n'.format(self.time_from, self.time_to)
            email += self.email_body
            return email
        else:
            return None
