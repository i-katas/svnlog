# SVNLog

SVNLog is an extension tools for formating the svn xml log.


## Installation

```bash
git clone https://github.com/i-katas/svnlog.git
cd svnlog
pip install .
```


## Usage

```bash
svn log --xml -v | svnlog --remote-path /remote/trunk --template custom_template.txt \
--include src --include test --exclude build --action ARM -s --text >changelist.txt
```
