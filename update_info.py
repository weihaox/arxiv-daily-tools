#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   update_info.py
@Time    :   2023/03/29 13:08:46
@Author  :   Weihao Xia (xiawh3@outlook)
@Version :   1.0
@Desc    :   This script is used to automatically update publication information.
'''

import os
import re
import json
import feedparser
import argparse
from urllib import request

def parse_paper_info(paper_info_str):
    '''
    parse the paper information
    return:
        paper_info: a dictionary of the paper information
    param:
        paper_info_str: a string of the paper information
    '''
    title, authors, *pubinfo_and_url = paper_info_str.strip().split('\n')
    venue_and_year = pubinfo_and_url[0].split('. ')[0]
    urls = pubinfo_and_url[0].split('. ')[1:] + pubinfo_and_url[1:]
    id = urls[0].split('/')[-1]
    id = id.split('v')[0]
    return {
        'id': id,
        'title': title,
        'authors': authors,
        'venue_and_year': venue_and_year,
        'urls': urls
        }

def get_arxiv_info(query_id):
    '''
    extract information
    return: 
        comment: a string of the comment
    param:
        query_id: the id of the paper
    '''
    query_url = f'http://export.arxiv.org/api/query?id_list={query_id}'
    data = request.urlopen(query_url).read().decode('utf-8')
    feed = feedparser.parse(data)
    comment = feed.entries[0].arxiv_comment
    return comment

def get_publish(query_id):
    '''
    get the publication information
    return:
        publish: a string of the publication information
    param:
        query_id: the id of the paper
    '''

    comment = get_arxiv_info(query_id)

    # read conference names from a text file
    with open('conf_list.txt') as f:
        conf_list = [line.strip() for line in f]
    conf_regex = '|'.join(conf_list)

    publish_regex = fr'({conf_regex}).*?\d{{4}}'
    publish = f'[\s\S]*({publish_regex})[\s\S]*'
    publish = re.findall(publish, comment)

    if publish:
        # extract publish information (e.g. cvpr 2021) from the comment
        publish = publish[0][0]

    return publish

def update_info(paper_info):
    '''
    update the venue_and_year information
    return: 
        papers_info: a list of paper information
    param: 
        papers_info: a list of updated paper information
    '''
    if paper_info['venue_and_year'].split(' ')[0].lower()== 'arxiv':
        id = paper_info['id']
        publish = get_publish(id)
        if publish:
            paper_info['venue_and_year'] = publish
    return papers_info

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Update the publication information of the papers.')
    parser.add_argument('--read_path', type=str, default='papers.md', help='the path of source file')
    parser.add_argument('--save_path', type=str, default='papers_updated.md', \
                        help='the path of target file')
    args = parser.parse_args()
    # read markdown and convert each paper information into a dictionary
    papers_info = []
    with open(args.read_path, 'r') as f:
        paper_info_strs = f.read().strip().split('\n\n')
        for paper_info_str in paper_info_strs:
            paper_info = parse_paper_info(paper_info_str)
            update_info(paper_info)
            papers_info.append(paper_info)
    # save the updated information
    with open(args.save_path, 'w') as f:
        for paper_info in papers_info:
            paper_info_str = f"{paper_info['title']}\n{paper_info['authors']}\
                \n{paper_info['venue_and_year']}. {' '.join(paper_info['urls'])}\n\n"
            f.write(paper_info_str)
    print("Update the publication information successfully!")