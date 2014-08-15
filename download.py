# -*- coding: utf-8 -*-


from mechanize import Browser
import re
from BeautifulSoup import BeautifulSoup
from subprocess import call



def ungzipResponse(r,b):
    headers = r.info()
    if headers['Content-Encoding']=='gzip':
        import gzip
        gz = gzip.GzipFile(fileobj=r, mode='rb')
        html = gz.read()
        gz.close()
        headers["Content-type"] = "text/html; charset=utf-8"
        r.set_data( html )
        b.set_response(r)

def remove_tags(text):
	return ''.join( BeautifulSoup(text).findAll( text = True )) 

def get_chapter_urls(novelid):
	urls = []
	br = Browser()
	link = "http://www.jjwxc.net/onebook.php?novelid=" + str(novelid)
	br.open(link)
	response = br.response()
	ungzipResponse(response, br)
	html = response.read()
	html = html.replace('div', '\n')
	lines = html.split('\n')
	for line in lines:
		if "chapterid" in line:
			items = line.split()
			for item in items:
				url = None
				if "href=" in item  and "onebook" in item:
					url = item.replace("href=", "")
				if "rel=" in item  and "onebook" in item:
					url = item.replace("rel=", "")
				if not url:
					continue
				match = re.match(r'\".*?\"', url)
				url = match.group(0)
				url = url.replace('"','')
				urls.append(url)
	return urls


def get_chapter(chapter_url, out_fp):
	br = Browser()
	br.open(chapter_url)
	response = br.response()
	ungzipResponse(response, br)
	html = response.read()
	html = html.decode('gb18030','ignore')
	html = remove_tags(html)
	lines = html.split('\n')
	chapterid = url.split('=')[1]

	#out_fp.write(((u"第 2 章").encode('gb2310'))
	out_fp.write('Chapter ' + chapterid)
	out_fp.write('\n\n')
	for line in lines:
		if "Copyright of" in line:
			line = re.sub(r'\@.*?\@','',line)
			line = re.sub(r'\t.*?\t','',line)
			line = re.sub(r'\w\d]*', '', line)
			line = line.replace(u'9','')
			line = line.replace(u'8','')
			line = line.replace(u'7','')
			line = line.replace(u'6','')
			line = line.replace(u'5','')
			line = line.replace(u'4','')
			line = line.replace(u'3','')
			line = line.replace(u'2','')
			line = line.replace(u'1','')
			line = line.replace(u'0','')


			line = line.replace(u'a','')
			line = line.replace(u'b','')
			line = line.replace(u'c','')
			line = line.replace(u'd','')
			line = line.replace(u'e','')
			line = line.replace(u'f','')


			line = line.replace(u'《','')
			line = line.replace(u'》','')

			line = line.replace(u'。',u'。\n')

			line = line.replace('       ', '')

			sublines = line.split('\n')
			for subline in sublines:
				if not subline.strip(u'。').strip(u' ').strip():
					continue
				out_fp.write(subline.encode('gb18030') + '\n')

			out_fp.write(''.join(c for c in line if u'\u4e00' <= c <= u'u9fff'))



		
urls = get_chapter_urls(912073)
text_file = open("output.txt", "w")
for url in urls:
	if "vip" not in url:
		get_chapter(url, text_file)
text_file.close()


call(["/Applications/calibre.app/Contents/console.app/Contents/MacOS/ebook-convert", "output.txt", "output.mobi"])
