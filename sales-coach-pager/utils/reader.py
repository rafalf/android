#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

CWD = os.getcwd()
RWD = os.path.join(CWD[:CWD.find('tests')], 'static', 'txt')
PATH = lambda y: os.path.join(RWD, y)


def get_conf():

    dict_conf = {}
    with open(PATH('data.conf'), 'r') as file_hdlr:
        for l in file_hdlr:
            split_equal = l.split('=')
            dict_conf[split_equal[0]] = split_equal[1].strip()
    return dict_conf


def get_locators():

    dict_locator = {}
    with open(PATH('locator.txt'), 'r') as file_hdlr:
        for l in file_hdlr:
            split_equal = l.split('=')
            dict_locator[split_equal[0]] = split_equal[1].strip()
    return dict_locator
