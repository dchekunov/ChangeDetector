import configparser
import os
import sys
import time
import datetime
import file_utils
import email_composer
import logging
import shutil
from log_utils import FolderLogger
from mail_utils import MailSender
from handler import FileLoggingEventHandler
from watchdog.observers import Observer


def main():
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    logging.info('File Checker v.1.0')
    logging.info('Initialising...')
    base_path = os.path.dirname(os.path.realpath(__file__))
    config = configparser.RawConfigParser()
    config.read(os.path.join(base_path, 'config', 'settings.cfg'))

    # Cleaning the temp directory
    file_utils.clean_temp(base_path)

    # Initialising email sending
    mail_sender = MailSender(config.get('email-login', 'login'), config.get('email-login', 'pass'),
                             config.get('email-server', 'server'), int(config.get('email-server', 'port')))

    # Reading files for directories to watch and email addresses to send reports to
    dirs = file_utils.get_dir_list(base_path)
    emails = file_utils.get_emails(base_path)

    # Initial timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Creating observer for every directory in a list and recording them in a pool
    observer_pool = {}
    for dir_name in list(dirs):
        event_handler = FileLoggingEventHandler(dir_name)
        observer = Observer()
        try:
            observer.schedule(event_handler, dirs[dir_name], recursive=True)
        except FileNotFoundError:
            logging.warning('Directory %s cannot be found, skipping...', dir_name)
            dirs.pop(dir_name, None)
            continue
        observer_pool[dir_name] = observer
        observer.daemon = True
        observer.start()
        # Creating dir to store temp data for every directory
        temp_dir = os.path.join(base_path, 'temp', dir_name)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
    if not len(dirs):
        logging.info('No directories to watch, exiting.')
        sys.exit()

    logging.info('Watching %i directories.', len(dirs))

    # Initialising logger
    folder_logger = FolderLogger(os.path.join(base_path, 'log'))
    folder_logger.initialise(list(dirs))

    logging.info('Started successfully.')

    # Looping forever until interrupted
    try:
        while True:
            # Time between checks is retrieved from config
            time.sleep(int(config.get('time', 'period')))
            new_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if not len(dirs):
                logging.info('No directories to watch, exiting.')
                sys.exit()

            # Logging and emailing changes for every watched directory
            for dir_name in list(dirs):
                temp_dir = os.path.join(base_path, 'temp', dir_name)

                # If watched directory does not exists anymore, it must've been deleted
                if not os.path.exists(dirs[dir_name]):
                    logging.warning('Watched directory %s has been deleted.', dir_name)
                    for email in emails:
                        mail_sender.send_message(email, 'Changes occurred in directory ' + dir_name,
                                                 'Directory {0} has been deleted.'.format(dir_name))
                    folder_logger.write(dir_name, 'Directory {0} has been deleted.'.format(dir_name))
                    dirs.pop(dir_name, None)
                    observer_pool[dir_name].stop()
                    # Removing temp dir for this directory
                    shutil.rmtree(temp_dir)
                    continue

                # Composing email text from data gathered in temp files
                composer = email_composer.EmailComposer(timestamp, new_timestamp)
                for filename in os.listdir(temp_dir):
                    with open(os.path.join(temp_dir, filename), 'r+') as file:
                        file_contents = file.read()
                        if file_contents:
                            composer.add_block(filename, file_contents)
                        file.seek(0)
                        file.truncate()
                # Logging and sending if composer managed to compose text (i.e. something was changed)
                if not composer.is_empty():
                    logging.info('Changes occurred in directory %s, sending emails', dir_name)
                    text = composer.compose_email()
                    folder_logger.write(dir_name, text)
                    for email in emails:
                        mail_sender.send_message(email, 'Changes occurred in directory ' + dir_name, text)
            # Updating timestamp
            timestamp = new_timestamp
    except KeyboardInterrupt:
        for key in observer_pool:
            observer_pool[key].stop()
    logging.info('Operation ended by user.')
    for key in observer_pool:
        observer_pool[key].join()
    file_utils.clean_temp(base_path)


if __name__ == '__main__':
    main()
