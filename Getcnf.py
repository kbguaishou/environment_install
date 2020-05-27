import sys

import os
from concurrent.futures._base import LOGGER


def read_cnf(cnf_path):
    assert cnf_path is not None and os.path.exists(cnf_path)
    cnf_dict = {}
    cur_section = None
    content_set = []
    with open(cnf_path, 'r', encoding='UTF-8') as cnf_reader:
        for line in cnf_reader.readlines():
            # line = str(line).rstrip("\n")
            if len(line) <= 0 or '#' == line[0]:
                continue
            if '[' == line[0] and ']' == line[-2]:
                cur_section = line[len('['):len(line) - 2]
                if cur_section not in cnf_dict:
                    cnf_dict[cur_section] = {}
                    continue
            if line.strip() != "":
                content_set.append(line)
            if line.strip() == "":
                cnf_dict[cur_section]['content'] = content_set
                content_set = []
        cnf_dict[cur_section]['content'] = content_set
    return cnf_dict


def main():
    cnf_path = "../oracle/conf.txt"

    mycnf = read_cnf(cnf_path)

    print(mycnf["/home/oracle/.bash_profile"]["content"])
    conf = mycnf["/home/oracle/.bash_profile"]["content"]
    for line in conf:
        print(line)

if __name__ == '__main__':
    main()
