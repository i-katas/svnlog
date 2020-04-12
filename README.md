# SVNLog

SVNLog is an extension tools for formating the svn xml log, e.g:

```bash
svn log --xml -v | svnlog --remote-path /remote/trunk --template custom_template.txt >changelist.txt
```
