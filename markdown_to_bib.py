#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   markdown_to_bib.py
@Time    :   2023/05/19 12:37:28
@Author  :   Weihao Xia (xiawh3@outlook)
@Version :   1.0
@Desc    :   This script is used to automatically convert a paper list in markdown to bib.
'''

import re
import feedparser
import argparse
from urllib import request

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

    # sometimes the tiltle and authors are changed
    title = feed.entries[0].title
    authors = [author.name for author in feed.entries[0].authors]
    try:
        comment = feed.entries[0].arxiv_comment
    except AttributeError:
        comment = 'hello world!'

    return title, authors, comment

def clean_title(title):
    '''
    remove certain punctuations in the title; and
    capitalize the first letter of each word (except for prepositions and acronyms)
    '''
    prepositions = ['about', 'and', 'as', 'at', 'but', 'by', 'for', 'from', 'in', 'nor', 'of', 'on', 'or', 'to', 'with']
    title = [word.capitalize() if word not in prepositions and word.islower() else word for word in title.split()]
    title = ' '.join(title) 
    return title

def remove_author_link(names):
    pattern = r"\[([^\]]+)\]\([^)]+\)"
    return re.sub(pattern, r"\1", names)

def convert_author_names(names):
    names = remove_author_link(names)
    author_list = names.split(",")
    formatted_names = []
    for author in author_list:
        formatted_author = ", ".join(author.strip().split()[::-1])
        formatted_names.append(formatted_author)
    return " and ".join(formatted_names)

def parse_paper_info(paper_info_str):
    '''
    parse the paper information
    return:
        paper_info: a dictionary of the paper information
    param:
        paper_info_str: a string of the paper information
    '''
    title, authors, *pubinfo_and_url = paper_info_str.strip().split('\n')
    pubinfo_and_url = ' '.join(pubinfo_and_url)
    venue_and_year = pubinfo_and_url.split('. ')[0]
    urls = pubinfo_and_url.split('. ')[1]
    urls = urls.split()# multiple spaces
    arxiv_id = re.search(r"\d+\.\d+", urls[0]).group(0)

    pattern_title = r'\*\*(.*?)\.\*\*<br>'
    match_title = re.search(pattern_title, title)

    pattern_authors = r'\*(.*?)\.\*<br>'
    match_authors = re.search(pattern_authors, authors)

    title = match_title.group(1)
    authors = match_authors.group(1)

    authors = convert_author_names(authors)

    return {
        'title': title,
        'authors': authors,
        'venue': venue_and_year.split(' ')[0],
        'year': venue_and_year.split(' ')[1],
        'arxiv_id': arxiv_id
        # 'urls': urls
        }

def generate_bib(entry):
    '''
    generate the bib entry
    return:
        bib: a string of the bib entry
    param:
        entry: a dictionary of the paper information
    '''
    # conference_list = ['CVPR', 'ECCV', 'ICCV', 'SIGGRAPH', 'NeurIPS']
    journal_list = ['TPAMI', 'TIP', 'TOG']

    authors = entry['authors'].split(' and ')
    if entry['venue'].lower() == 'arxiv' or entry['venue'] in journal_list:
        bib = f"@article{{{entry['authors'].split(',')[0].lower()}{entry['year']}{entry['title'].split()[0].split('-')[0].split(':')[0].lower()}," + "\n"
    else:
        bib = f"@inproceeding{{{entry['authors'].split(',')[0].lower()}{entry['year']}{entry['title'].split()[0].split('-')[0].split(':')[0].lower()}," + "\n"
    bib += f"  title={{{entry['title']}}}," + "\n"
    bib += f"  author={{{entry['authors']}}}," + "\n"
    if entry['venue'].lower() == 'arxiv':
        bib += f"  journal={{arXiv preprint:arXiv {entry['arxiv_id']}}}," + "\n"
    else:
        bib += f"  booktitle={{{entry['venue']}}}," + "\n"
    bib += f"  year={{{entry['year']}}}" + "\n"
    bib += "}"
    return bib

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert academic papers in Markdown to BibTeX.')
    parser.add_argument('read_path', type=str, default='papers.md', help='path to the input Markdown file')
    parser.add_argument('bib_file', type=str, default='example_bib.bib', help='path to the output BibTeX file')
    args = parser.parse_args()

    # # read conference names from a text file
    # with open('conf_list.txt') as f:
    #     conf_list = [line.strip() for line in f]
    # conf_regex = '|'.join(conf_list)
    # publish_regex = fr'({conf_regex}).*?\d{{4}}'
    # publish_regex = f'[\s\S]*({publish_regex})[\s\S]*'

    # read markdown and convert each paper information into a dictionary
    # Open the file and read the contents into one string
    with open(args.read_path, 'r') as f:
        paper_info_strs = f.read().strip().split('\n\n')

    # Parse the string into a list of paper info
    updated_papers_info = []

    with open(args.bib_file, 'w') as bib_file:
        for paper_info_str in paper_info_strs:
            paper_info = parse_paper_info(paper_info_str)
            bib_content = generate_bib(paper_info)

            bib_file.write(bib_content + "\n")