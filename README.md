# arxiv_daily_tools

This script converts arxiv papers (given id or title) into a certain markdown [format](https://github.com/weihaox/awesome-neural-rendering). I utilize this script to categorize daily arxiv papers based on my research interests ([awesome-neural-rendering](https://github.com/weihaox/awesome-neural-rendering), [awesome-3D-aware-synthesis](https://github.com/weihaox/awesome-3D-aware-synthesis), [awesome-gan-inversion](https://github.com/weihaox/awesome-gan-inversion), [awesome-image-translation](https://github.com/weihaox/awesome-image-translation)). 

## usage

If you find some interesting papers on arxiv today and want to add them to your paper list, please add their arxiv ids to `paper_list.txt` and run the following command.

```Shell
python arxiv_daily_tools.py
```

If you have a papers.md (like [this](https://github.com/weihaox/arxiv_daily_tools/blob/main/papers.md)) and would like to update some information, please use the following command.

```Shell
python update_info.py
```
If you want to convert the markdown file to BibTeX (.bib) or BibLaTeX (.bbl) references, please use the following command.

```Shell
python markdown_to_bib.py papers.md ./ --mode 1 # mode 1 is for BibTeX, and mode 1 is for BibLaTeX
```
## related 

Thanks to [yzy1996](https://github.com/yzy1996) for sharing the [code](https://github.com/yzy1996/Python-Code/commit/9d76bd75cc4d6f3980b5c6ef8a20cedd92c0fa1b).