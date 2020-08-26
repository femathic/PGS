import os
import time
import json


def create_directory_file(basedir, path):
    if not os.path.exists(basedir):
        os.makedirs(basedir)  # Create directory
        f = open(path, 'a')  # Create file
        f.close()


def save_json(data_list):
    path = 'bucket/data.json'
    basedir = os.path.dirname(path)

    create_directory_file(basedir, path)
    with open(path, 'r') as infile:
        try:
            file_in = infile.read()
            results = []
            if not file_in:
                file_in = '[]'
            else:
                results = json.loads(file_in, encoding="utf-8")

            if data_list[0].get('id') not in [d['id'] for d in results]:
                results += data_list

            with open(path, 'w') as outfile:
                json.dump(results, outfile, indent=2)
        except Exception as e:
            print(e)  # for the repr
            print(str(e))  # for just the message
            print(e.args)
            with open(path, 'w') as empty:
                empty.write('[]')