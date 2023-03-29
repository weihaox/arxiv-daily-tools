#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   arxiv_daily_tools.py
@Time    :   2023/03/29 09:45:43
@Author  :   Weihao Xia (xiawh3@outlook)
@Version :   v3.0 2023/03/29 09:45:43 use feedparser to remove regular expressions
             v2.0 2023/03/23 12:19:44 clean up the code
             v1.0 2022/11/02 12:19:44
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
import feedparser

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

        self.data = request.urlopen(self.query_url).read().decode('utf-8')
        self.abs_url, self.title, self.authors, self.year, self.comment, self.urls = self.get_arxiv_info()
        self.title = self.clean_title(self.title)

        self.pdf_url = self.abs_url.replace('abs', 'pdf')

    def get_arxiv_info(self):
        '''
        extract information
        '''
        feed = feedparser.parse(self.data)

        title = feed.entries[0].title
        authors = [author.name for author in feed.entries[0].authors]
        abs_url = feed.entries[0].link # arxiv.org/abs/2103.11536v1
        year = feed.entries[0].published.split('-')[0] # 2021-03-23T00:00:00Z -> 2021
        comment = feed.entries[0].arxiv_comment

        urls = []
        if comment:
            comment = comment.strip()
            extractor = URLExtract()
            urls = extractor.find_urls(comment)

        return abs_url, title, authors, year, comment, urls

    def clean_title(self, title):
        '''
        remove certain punctuations in the title; and
        capitalize the first letter of each word (except for prepositions and acronyms)
        '''
        prepositions = ['about', 'and', 'as', 'at', 'but', 'by', 'for', 'from', 'in', 'nor', 'of', 'on', 'or', 'to', 'with']
        title = [word.capitalize() if word not in prepositions and word.islower() else word for word in title.split()]
        title = ' '.join(title) # word.islower() is to prevent changing "Aadf-GAN" to "Aadf-Gan"
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
        publish = f'[\s\S]*({publish_regex})[\s\S]*'
        publish = re.findall(publish, self.comment)

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