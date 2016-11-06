#!/usr/bin/env python


def get_conf():

    dict_conf = {}
    with open('data.conf') as file_hndlr:
        for l in file_hndlr:
            split_equal = l.split('=')
            dict_conf[split_equal[0]] = split_equal[1].strip()
    return dict_conf
