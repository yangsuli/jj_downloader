# -*- coding: utf-8 -*-

import requests
import browsercookie
from BeautifulSoup import BeautifulSoup
import re
import gzip

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import encoders

from subprocess import call

def remove_tags(text):
	return ''.join( BeautifulSoup(text).findAll( text = True )) 

def get_chapter_urls(novelid):
	urls = []
	link = "http://www.jjwxc.net/onebook.php?novelid=" + str(novelid)
	response = requests.get(link)
	response.encode = 'gb18030'
	html = response.text
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


def get_chapter(chapter_url, cj, out_fp):
	response = requests.get(chapter_url, cookies=cj)
	response.encoding = 'gb18030'
	html = response.text
	html = remove_tags(html)
	lines = html.split('\n')
	chapterid = url.split('=')[2]

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

def get_title(novelid):
	url = "http://www.jjwxc.net/onebook.php?novelid=" + str(novelid)
	response = requests.get(url)
	response.encoding='gb18030'
	for line in response.text.split('\n'):
		if "articleSection" in line:
			line = remove_tags(line)
			return line.strip()

def send_email_attachment(fromaddr, toaddr, password, attach_filepath, attach_filename):
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "book"
	 
	body = ""
	msg.attach(MIMEText(body, 'plain'))
	
	attachment = open(attach_filepath, "rb")
	part = MIMEBase('application', 'octet-stream')
	part.set_payload((attachment).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', "attachment; filename= %s" % attach_filename)
	msg.attach(part)
	 
	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, password)
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()


cj = browsercookie.chrome()
novel_id_str = raw_input("what is the novelid you want to download?")
novel_id = int(novel_id_str)
title = get_title(novel_id)
urls = get_chapter_urls(novel_id)
text_file = open(title + ".txt", "w")
for url in urls:
	print "get url:", url
	get_chapter(url, cj, text_file)
text_file.close()

kindle_sendaddr = ""
password = ''
kindle_recvaddr = ""
filename = (title + ".txt").encode('utf-8')
filepath = title + ".txt"
send_email_attachment(kindle_sendaddr, kindle_recvaddr, password, filepath, filename)

call(["/Applications/calibre.app/Contents/console.app/Contents/MacOS/ebook-convert", title + ".txt", title + ".mobi"])
