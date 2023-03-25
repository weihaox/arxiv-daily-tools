#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   arxiv_daily_tools.py
@Time    :   2023/03/23 12:19:44
@Author  :   Weihao Xia (xiawh3@outlook)
@Version :   v2.0 (v1.0 2022/11/02 12:19:44)
@Desc    :   This script is used to query arxiv papers and download pdfs.
             It converts arxiv papers (given id or title) into the following markdown format.
             **Here is the Paper Name.**<br>
             *[Author 1](homepage), Author 2, and Author 3.*<br>
             Publication Year. [[PDF](link)] [[Project](link)] 
'''

import re
import os
from urllib import request
from urlextract import URLExtract
from PyPDF2 import PdfFileReader
from tqdm import trange


class Information():
    '''
    get information from arxiv api
    '''
    def __init__(self, query_id=None, query_title=None):
        if query_id:
            self.query_url = f'http://export.arxiv.org/api/query?id_list={query_id}'
        elif query_title:
            query_title = query_title.replace(' ', '+')
            self.query_url = f'https://export.arxiv.org/api/query?search_query=all:{query_title}&max_results=1'

        self.strInf = request.urlopen(self.query_url).read().decode('utf-8')
        self.id_version, self.id, self.title, self.authors, self.year, self.comment, self.urls = self._re_process()
        self.title = self._clean_title(self.title)

        self.abs_url = f'https://arxiv.org/abs/{self.id}'
        self.pdf_url = f'https://arxiv.org/pdf/{self.id}'

    def _re_process(self):
        '''
        extract information from the xml file
        '''
        id_version = re.findall(r'<id>http://arxiv.org/abs/(.*)</id>', self.strInf)[0]
        id = id_version[:-2]
        title = re.findall(r'<title>([\s\S]*)</title>', self.strInf)[0]
        authors = re.findall(r'<author>\s*<name>(.*)</name>\s*</author>', self.strInf)
        year = re.findall(r'<published>(\d{4}).*</published>', self.strInf)[0]
        comment = re.findall(r'<arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">([\s\S]*?)</arxiv:comment>', self.strInf)

        urls = []
        if comment:
            comment = comment[0].strip()
            extractor = URLExtract()
            urls = extractor.find_urls(comment)

        return id_version, id, title, authors, year, comment, urls

    def _clean_title(self, title):
        '''
        remove certain punctuations in the title; and
        capitalize the first letter of each word (except for prepositions and acronyms)
        '''
        prepositions = ['about', 'and', 'as', 'at', 'but', 'by', 'for', 'from', 'in', 'nor', 'of', 'on', 'or', 'to', 'with']
        title = re.sub(r'\n\s', '', title) # remove '\n' and the following spaces
        title = re.sub(r'\b(?!(' + '|'.join(prepositions) + r'))[a-z]', lambda x: x.group(0).upper(), title)
        # title = [word.capitalize() if word not in prepositions else word for word in title.split()]
        # title = ' '.join(title) # this will undesirably change 'Aadf-GAN' to 'Aadf-Gan'.
        return title

    def get_publish(self):
        '''
        get the publication information
        '''
        # read conference names from a text file
        with open('conf_list.txt') as f:
            conf_list = [line.strip() for line in f]
        conf_regex = '|'.join(conf_list)

        publish_regex = fr'({conf_regex}).*?\d{{4}}'
        publish = f'<arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">[\s\S]*({publish_regex})[\s\S]*</arxiv:comment>'
        publish = re.findall(publish, self.strInf)

        if publish:
            # extract publish information (e.g. cvpr 2021) from the comment
            publish = publish[0][0]
        else:
            # arxiv + year
            publish = f'arXiv {self.year}'

        self.publish = publish

    def write_notes(self):
        '''
        define the markdown format and write notes
        '''
        self.get_publish()
        # render the title, authors, and publication info
        title_url = f'**{self.title}.**<br>'
        authors_str = ', '.join(self.authors)
        authors = f'*{authors_str}.*<br> '
        publish = f'{self.publish}. [[PDF]({self.abs_url})]'

        print(f'{title_url}\n{authors}\n{publish}')

        if self.urls:
            for i in range(len(self.urls)):
                print (f'[[Link]({self.urls[i]})]')
        print('\n')

    def download(self):
        '''
        define the download path and title, and
        download all pdfs in the list
        '''
        save_path = 'downloads'
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        request.urlretrieve(self.pdf_url, f'{save_path}/{self.year}_{self.title}.pdf')

if __name__ == '__main__':

    # query with title
    # info = Information(query_title='A Survey on 3D-aware Image Synthesis')
    # info.write_notes()

    # query with id
    # idx = '2210.14267'
    # information = Information(query_id=idx)
    # information.write_notes()

    # query given a paper_list.txt
    with open(r'paper_list.txt') as f:
        ids = [line.strip() for line in f]
    for idx in ids:
        if re.match(idx, r'\t'):
            pass
        information = Information(query_id=idx)
        information.write_notes()
        # information.download() 