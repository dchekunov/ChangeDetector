from watchdog.events import FileSystemEventHandler
import os
import datetime


class FileLoggingEventHandler(FileSystemEventHandler):
    def __init__(self, dir_name):
        super(FileLoggingEventHandler, self).__init__()
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.dir_name = dir_name

    def on_created(self, event):
        super(FileLoggingEventHandler, self).on_created(event)
        filename = os.path.join(self.path, 'temp', self.dir_name, 'created')
        with open(filename, 'a') as created_file:
            created_file.write('{0}#@#{1}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                    event.src_path))

    def on_moved(self, event):
        super(FileLoggingEventHandler, self).on_moved(event)
        filename = os.path.join(self.path, 'temp', self.dir_name, 'moved')
        with open(filename, 'a') as created_file:
            created_file.write('{0}#@#{1} -> {2}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                           event.src_path, event.dest_path))

    def on_deleted(self, event):
        super(FileLoggingEventHandler, self).on_deleted(event)
        filename = os.path.join(self.path, 'temp', self.dir_name, 'deleted')
        with open(filename, 'a') as created_file:
            created_file.write('{0}#@#{1}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                    event.src_path))

    def on_modified(self, event):
        super(FileLoggingEventHandler, self).on_modified(event)
        filename = os.path.join(self.path, 'temp', self.dir_name, 'modified')
        with open(filename, 'a') as created_file:
            created_file.write('{0}#@#{1}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                    event.src_path))
