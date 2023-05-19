#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   markdown_to_bib.py
@Time    :   2023/05/19 17:22:10
@Author  :   Weihao Xia 
@Version :   3.0
@Desc    :   In this updated code, I added the generate_bbl function to generate 
             the BBL file based on the parsed paper information. The generate_bbl 
             function iterates over the parsed entries and constructs the BBL 
             content with the required formatting. The BBL content is then written 
             to the specified output file.
             Make sure to provide the paths for the input Markdown file, 
             output BibTeX file, and output BBL file when running the script.
             To run the script and save the desired files, you can use the following command:
             python markdown_to_bib_v2.py papers_updated.md  example_bib.bib example_bbl.bbl
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

    entry = feed.entries[0]
    title = entry.title
    authors = [author.name for author in entry.authors]
    comment = entry.get('arxiv_comment', 'hello world!')

    return title, authors, comment


def clean_title(title):
    '''
    remove certain punctuations in the title; and
    capitalize the first letter of each word (except for prepositions and acronyms)
    '''
    prepositions = ['about', 'and', 'as', 'at', 'but', 'by', 'for', 'from', 'in', 'nor', 'of', 'on', 'or', 'to', 'with']
    words = title.split()
    cleaned_words = [word.capitalize() if word not in prepositions and word.islower() else word for word in words]
    cleaned_title = ' '.join(cleaned_words)
    return cleaned_title


def remove_author_link(names):
    pattern = r"\[([^\]]+)\]\([^)]+\)"
    return re.sub(pattern, r"\1", names)


def convert_author_names(names):
    names = remove_author_link(names)
    author_list = names.split(",")
    formatted_names = [", ".join(author.strip().split()[::-1]) for author in author_list]
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
    venue_and_year, *urls = pubinfo_and_url.split('. ')
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
        entry_type = 'article'
    else:
        entry_type = 'inproceeding'

    bib = f"@{entry_type}{{{entry['authors'].split(',')[0].lower()}{entry['year']}{entry['title'].split()[0].split('-')[0].split(':')[0].lower()}"
    bib += f",\n  title={{{entry['title']}}}"
    bib += f",\n  author={{{entry['authors']}}}"

    if entry['venue'].lower() == 'arxiv':
        bib += f",\n  journal={{arXiv preprint:arXiv {entry['arxiv_id']}}}"
    else:
        bib += f",\n  booktitle={{{entry['venue']}}}"

    bib += f",\n  year={{{entry['year']}}}"
    bib += "\n}"

    return bib


def generate_bbl(entries):
    bbl = ''
    for i, entry in enumerate(entries):
        entry_key = entry['authors'].split(',')[0].lower() + entry['year'] + entry['title'].split()[0].split('-')[0].split(':')[0].lower()
        bbl += f"\\bibitem{{{entry_key}}}\n"
        bbl += f"  {entry['title']}\n"
        bbl += f"  {entry['authors']}\n"
        bbl += f"  {entry['venue']}, {entry['year']}\n\n"
    return bbl


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert academic papers in Markdown to BibTeX and BBL.')
    parser.add_argument('read_path', type=str, default='papers.md', help='path to the input Markdown file')
    parser.add_argument('bib_file', type=str, default='example_bib.bib', help='path to the output BibTeX file')
    parser.add_argument('bbl_file', type=str, default='example_bbl.bbl', help='path to the output BBL file')
    args = parser.parse_args()

    with open(args.read_path, 'r') as f:
        paper_info_strs = f.read().strip().split('\n\n')

    parsed_paper_info = [parse_paper_info(paper_info_str) for paper_info_str in paper_info_strs]
    bibtex_entries = [generate_bib(info) for info in parsed_paper_info]
    bbl_content = generate_bbl(parsed_paper_info)

    with open(args.bib_file, 'w') as bib_file:
        bib_file.write('\n'.join(bibtex_entries))

    with open(args.bbl_file, 'w') as bbl_file:
        bbl_file.write(bbl_content)
