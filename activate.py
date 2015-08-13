#page element scraper

"""
This program is designed to 
	1.) scrape a list of URLs for title tags, meta description, and body text
	2.) scan each element for fuzzy keyword matches based on inputted keywords
	3.) output a csv with elements and their respective counts 

inputs: URLs and respective keywords
outputs: text and counts

Requires (installed via pip or other package manager):
	BeautifulSoup (scraping package)
	FuzzyWuzzy (fuzzy matching package)
	NLTK (natural language processor)

Should be standard with Python 3:
	requests
	csv
	os

Extensions:
	textstat readability analysis 
"""

from bs4 import BeautifulSoup
import requests
import csv
from fuzzywuzzy import fuzz
import nltk.data
from nltk.tokenize import RegexpTokenizer
#from textstat.textstat import textstat
import time
import re
import os
"""Retrieve an attachment from a Message.
""" 
  
import base64
from apiclient import errors
import httplib2

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def attachments():
    """List all Messages of the user's mailbox matching the query.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    user_id = "me"
    query = 'label:raspberry'
    try:
        response = service.users().messages().list(userId=user_id,q=query).execute()
        messages = []
        if 'messages' in response:
            
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,pageToken=page_token).execute()
            messages.extend(response['messages'])
        return messages
    except errors.HttpError:
        print('didnt work')

def GetAttachments(msg_ids):
	"""Get and store attachment from Message with given id.

	Args:
	service: Authorized Gmail API service instance.
	user_id: User's email address. The special value "me"
	can be used to indicate the authenticated user.
	msg_id: ID of Message containing attachment.
	store_dir: The directory used to store attachments.
	"""    
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('gmail', 'v1', http=http)
	user_id = "me"
	for x in msg_ids:
	    try:
	        message = service.users().messages().get(userId='me', id=x['id']).execute()

	        for part in message['payload']['parts']:
	            if part['filename']:
	                if 'data' in part['body']:
	                    data=part['body']['data']
	                else:
	                    att_id=part['body']['attachmentId']
	                    att=service.users().messages().attachments().get(userId=user_id, messageId=x['id'],id=att_id).execute()
	                    data=att['data']
	                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
	                
	                path = part['filename']
	                if 'csv' in path[-5:]:
	                    print(path)
	                    with open(path, 'wb') as f:

	                        f.write(file_data)
	                        f.close()

	    except errors.HttpError:
	        print('Error XX')





def scrape(URL,KW):
	headers = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}

	start = time.time()
	#for URL in URLlist:
	end = URL[-10:]
	if "pdf" in end.lower():
		return ["NA","NA",[0,1,2],"NA","NA","NA","NA","NA","NA","NA"]
	else:
		r = requests.get(URL,headers=headers,timeout=25)
		stripped = r.text
		stripped = stripped.replace('\n', '. ')
		soup = BeautifulSoup(stripped,"html.parser")
		
	load_time = start - time.time()
	#TITLE TAGS
	start = time.time()
	try:
		title = soup.title.string
		title = title.replace(".   ","")
		title = title.replace(".  ","")
		if title == None:
			title = u"NA"
	except:
		title = u"NA"
	
	#META DESCRIPTION
	try:
		md = soup.findAll(attrs={"name":"description"})
		if md != []:
			meta_raw = md
		else: 
			meta_raw = soup.findAll(attrs={"name":"Description"})
		meta = meta_raw[0]['content']
	except:
		meta = u"NA"

	#H1
	try:
		H1 = soup.h1.string
		H1 = H1.replace(".   ","")
		H1 = H1.replace(".  ","")
		if H1 == None:
			H1 = u"NA"
	except:
		H1 = u"NA"

	#links
	bareresult = url_cleaner(URL)
	exlinks = 0
	inlinks = 0
	exlinks_cc = 0
	inlinks_cc = 0

	for link in soup.find_all(href=re.compile("https?://")):
		full_link=link.get('href')
		clean_link = url_cleaner(link.get('href'))
		if clean_link == bareresult:
			exlinks += 1
			exlinks_cc += len(full_link)
		else:
			inlinks += 1
			inlinks_cc+= len(full_link)


	#BODY
	
	try:
		
		end = URL[-10:]
		if "pdf" in end.lower():
			text = "PDF"
		else:
			for script in soup(["script", "style"]):
				script.extract()
			text = soup.get_text()
			text = text.replace(',',' ')
			text = text.replace('<br/>','. ')
			text = text.replace('\r',' ')
			text = text.replace('\t', ' ')
			text = text.replace('.   ', '')
			text = text.replace('.  ', '')
			text = text.replace('. . ', '')
			starting = text[0:10]
			if "pdf" in starting.lower():
				text = "PDF"
		text_count = count(text, KW)

		# break into lines and remove leading and trailing space on each

	except:	
		text = u"NA"
	parse_time = time.time() -start

	content = [title, meta, text_count, H1, exlinks, inlinks, exlinks_cc, inlinks_cc,load_time, parse_time] 
	return content

def count(text,KW):
	text = text.lower()
	
	sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
	sentences = sent_detector.tokenize(text.strip())
	adjmentions = []
	tokenizer = RegexpTokenizer(r'\w+')
	wordcount = 0

	for sentence in sentences:
		tokens = tokenizer.tokenize(sentence)
		words = len(tokens)
		wordcount += words
		if fuzz.token_set_ratio(KW,sentence)<30:
			score = 0
		else:	
			score = fuzz.token_set_ratio(KW,sentence) *.01
		adjmentions.append(score)

	aggregate = 0 
	for x in range(len(adjmentions)):

		aggregate += adjmentions[x]

	
	text = text.replace('   ', '')
	text = text.replace('.', ' ')
	text = text.replace('   ', '')
	character_count = len(text)
	return [aggregate,wordcount,character_count]



def analysis(inputCSV,output):
	with open(output,'wt') as myfile:
		wr = csv.writer(myfile)
		wr.writerow(['KW','URL','position', 'load time', 'title tag text', 'meta tag text', 'h1 text','title tag count', 'meta description count','h1 count', 'body count','body word count','body character count','ex links','in links','ex links cc','in links cc'])
		with open(inputCSV,'rU', encoding='Latin-1') as fp:
			reader = csv.reader(fp,delimiter=",")
			next(reader, None)

			for row in reader:
				print(row)
				KW = row[0]
				URL = row[1]
				position = row[2]

				try:
					content = scrape(URL,KW)
				except:
					content = ["NA","NA",[0,1,2],"NA","NA","NA","NA","NA","NA","NA"]


				titletag = content[0]
				meta = content[1]
				H1 = content[3]

				titletag_count = count(titletag, KW)
				meta_count = count(meta, KW)
				body_count = content[2]
				H1_count = count(H1, KW)


				wr.writerow([KW,URL, position, content[8], titletag, meta, H1, titletag_count[0], meta_count[0],H1_count[0],body_count[0],body_count[1],body_count[2],content[4],content[5],content[6],content[7]])


def url_cleaner(url):
	"""
	this function matches and cleans a given url to aid in easier matching and dictionary construction later on
	"""
	url_match = re.match("(https?://)?(.*?)\.(.*?)/",url)
	if url_match != None:
		if '.' not in url_match.group(3):
			return url_match.group(2)+'.' +url_match.group(3)
		else:
			return url_match.group(3)

def activate():
	
	count = 0 
	path = os.getcwd()
	def doit(count):

		waiting= []
		for x in os.listdir():
			if "csv" in x[-5:]:
				waiting.append(x)

		donelist = []
		while len(waiting)>0:
			output = path + "files/CA_output_"+waiting[0][9:]
			analysis(waiting[0],output)
			os.rename(waiting[0], path+'done/'+waiting[0])
			donelist.append(waiting.pop(0))
			print(donelist[-1])
		count += 1
	while count<7:

		GetAttachments(attachments())
		os.chdir(path+'files')
		doit(count)
		time.sleep(3600)




if __name__ == '__main__':
	activate()

