import itertools
import scraperwiki
import lxml.html
import re
import codecs

def empty(ln):
  return ln.strip()

def clinic(ln):
  return re.match("^[0-9]",ln) or empty(ln)

def district(ln):
  return not (("Mutare" in ln) or ln.isupper() or re.match("^Name ",ln) or not empty(ln))
  
columns = {
  "Name": {"filter":clinic, "selector":"text[left='135'][font='0']"},
  "Category": {"filter":empty, "selector":"text[left='356'][font='0']"},
  "Owner": {"filter":empty, "selector":"text[left='578'][font='0']"},
   }
district={"filter":district, "selector":"text[left='135'][font='1']"}

def get_pages(root):
  return root.cssselect("page")

def get_row_tops(page):
  return (i.attrib['top'] for i in 
    itertools.ifilter(lambda x: empty(x.text_content()), 
      page.cssselect("text[left=135'][font='0']")))

def get_text_content(page,selector):
  c=page.cssselect(selector)
  if len(c):
   return c[0].text_content() 
  else:
    return ""

def get_columns_from_top(page,top):
  top="[top='%s']"%top
  return dict(((k, get_text_content(page,"%s%s"%(v["selector"],top))) for
  (k,v) in columns.items()))

def get_districts(root):
  return itertools.ifilter(
    district["filter"], (i.text_content() for i in
    root.cssselect(district["selector"])))

def get_column(root,column):
  return (i for i in
  (itertools.ifilter(column["filter"],(i.text_content() for i in
  root.cssselect(column["selector"])))))

def get_columns(root,columns):
  return dict(((k,get_column(root,v)) for (k,v) in columns.items()))

def taken(n,iter):
  return itertools.islice(iter,n)

def counts(it):
  it.next() # drop the first line
  while True:
    a=len([i for i in itertools.takewhile(lambda x: not re.search("^1\.", x), it)])
    if a:
      yield a+1
    else:
      break

def makedicts(columns):
  keys=columns.keys()
  while True:
    a=dict(((k, columns[k].next()) for k in keys))
    if reduce(lambda x,y: x or y, a.values(), False):
      yield a
    else:
      break

def createblock(ns, src):
  return reduce(lambda x,y: itertools.chain(x, y),
    (itertools.repeat(s,n) for (n,s) in zip(ns,src)))

def blockit(columns):
  (n1,columns["Name"])=itertools.tee(columns["Name"])
  lengths=counts(n1)
  columns["District"]=createblock(lengths,columns["District"])
  return columns


def get_root(filename):
  f=open(filename)
  pdf="".join(f)
  return lxml.html.fromstring(
    scraperwiki.pdftoxml(pdf))

if __name__=="__main__":
  root=get_root("../data/provincila and district hospitals.pdf")
  c=get_columns(root,columns)
  c2=blockit(c)
  f=codecs.open("../data/provincial_and_district_hospitals.csv","wb","utf-8")
  keys=columns.keys()
  f.write(",".join(keys))
  f.write("\n")
  for l in makedicts(c2):
    f.write(u','.join((unicode(l[k]) for k in keys)))
    f.write("\n")
  f.close()  
    
