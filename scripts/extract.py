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
  return not (("Mutare Provincial Hospital" in ln) or ln.isupper() or re.match("^Name ",ln) or not empty(ln))
  
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
      page.cssselect("text[left='135'][font='0']")))

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

def get_columns(root):
  return reduce(itertools.chain, [[get_columns_from_top(page,t) for t in get_row_tops(page)] for page in
    get_pages(root)])

def get_districts(root):
  return itertools.ifilter(
    district["filter"], (i.text_content() for i in
    root.cssselect(district["selector"])))


def addattr(do,k,v):
  do[k]=v
  return do

def add_districts(cs,districts):
  d=None
  for c in cs:
    if re.search("^1\.", c["Name"]):
      d=districts.next()
    yield addattr(c,"District",d)



def get_root(filename):
  f=open(filename)
  pdf="".join(f)
  return lxml.html.fromstring(
    scraperwiki.pdftoxml(pdf))

if __name__=="__main__":
  root=get_root("../data/provincila and district hospitals.pdf")
  cs=get_columns(root)
  ds=get_districts(root)
  keys=["Name","Owner","Category","District"]
  f=codecs.open("../data/provincial_and_district_hospitals.csv","wb","utf-8")
  f.write(",".join(keys))
  f.write("\n")
  for l in add_districts(cs,ds):
    f.write(u','.join((u'"%s"'%unicode(l[k]) for k in keys)))
    f.write("\n")
  f.close()  
    
