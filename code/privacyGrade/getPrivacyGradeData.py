'''
Created on April 24, 2017
@author: Prajit Kumar Das
Usage: python getPrivacyGradeData.py
'''

from bs4 import BeautifulSoup
import urllib2
import sys
import databaseHandler
from mysql.connector import conversion
import time
import datetime
import traceback
import httplib

def extractAppDataToJson(privacyGradeUrl):
	print privacyGradeUrl

def getDeveloperId(dbHandle,app_dict):
	cursor = dbHandle.cursor()
	dev_name = app_dict['developer_name']
	dev_name = conversion.MySQLConverter().escape(dev_name)
	if 'dev_website' in app_dict:
		dev_web = app_dict['dev_website']
	else:
		dev_web = ""
	dev_web = conversion.MySQLConverter().escape(dev_web)
	if 'dev_email' in app_dict:
		dev_email = app_dict['dev_email']
	else:
		dev_email = ""
	dev_email = conversion.MySQLConverter().escape(dev_email)
	if 'dev_location' in app_dict:
		dev_loc = app_dict['dev_location']
	else:
		dev_loc = ""
	dev_loc = conversion.MySQLConverter().escape(dev_loc)
	sqlStatementdDevId = "SELECT `id` FROM `developer` WHERE `name` = '"+dev_name+"';"
	try:
		cursor.execute(sqlStatementdDevId)
		if cursor.rowcount > 0:
			queryOutput = cursor.fetchall()
			for row in queryOutput:
				return row[0]
		else:
			sqlStatementdDevIdInsert = "INSERT into `developer`(`name`,`website`,`email`,`country`) VALUES('"+dev_name+"','"+dev_web+"','"+dev_email+"','"+dev_loc+"');"
			return databaseHandler.dbManipulateData(dbHandle, sqlStatementdDevIdInsert)
	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise

def getCategoryId(dbHandle,app_dict):
	cursor = dbHandle.cursor()
	sqlStatementdAppCatId = "SELECT `id` FROM `appcategories` WHERE `name` = '"+app_dict['app_category'].upper()+"';"
	try:
		cursor.execute(sqlStatementdAppCatId)
		queryOutput = cursor.fetchall()
		for row in queryOutput:
			return row[0]
	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise


# Create the SQL statement to execute out of the dictionary data
def createSQLStatementAndInsert(dbHandle,app_dict):
	if 'app_name' in app_dict:
		app_name = app_dict['app_name']
		app_name = conversion.MySQLConverter().escape(app_name)
		#print app_name

		app_pkg_name = app_dict['app_pkg_name']
		developer_id = getDeveloperId(dbHandle,app_dict)
		app_category_id = getCategoryId(dbHandle,app_dict)

		if 'review_rating' in app_dict:
			review_rating = app_dict['review_rating']
		else:
			review_rating = 0.0

		if 'review_count' in app_dict:
			review_count = app_dict['review_count']
		else:
			review_count = 0

		if 'app_desc' in app_dict:
			app_desc = app_dict['app_desc']
		else:
			app_desc = ''
		escaped_text_desc = conversion.MySQLConverter().escape(app_desc)

		if 'whats_new' in app_dict:
			whats_new = app_dict['whats_new']
		else:
			whats_new = ''
		escaped_text_whats_new = conversion.MySQLConverter().escape(whats_new)

		if 'Updated' in app_dict:
			updated = app_dict['Updated']
		else:
			updated = '1984-08-31'

		if 'Installs' in app_dict:
			installs = app_dict['Installs']
		else:
			installs = 0

		if 'Current_Version' in app_dict:
			version = app_dict['Current_Version']
		else:
			version = ''

		if 'Requires_Android' in app_dict:
			android_reqd = app_dict['Requires_Android']
		else:
			android_reqd = ''

		if 'Content_Rating' in app_dict:
			content_rating = app_dict['Content_Rating']
		else:
			content_rating = ''

		sqlStatement = "INSERT INTO `appdata`(`app_pkg_name`,`app_name`,`developer_id`,`app_category_id`,`review_rating`,`review_count`,`desc`,`whats_new`,`updated`,`installs`,`version`,`android_reqd`,`content_rating`) VALUES('" + app_pkg_name + "','" + app_name + "'," + str(developer_id) +","+ str(app_category_id) +","+ str(review_rating) +","+ str(review_count) +",'"+ escaped_text_desc +"','"+ escaped_text_whats_new +"','" + updated + "',"+ str(installs)+",'" + version + "','" + android_reqd + "','" + content_rating + "');"
		print sqlStatement
		databaseHandler.dbManipulateData(dbHandle, sqlStatement)

# Extract app data and store in DB
def extractAppDataAndStore(dbHandle, urlExtract):
	headers = { 'User-Agent' : 'Mozilla/5.0' }
	req = urllib2.Request(urlExtract, None, headers)
	try:
		page = urllib2.urlopen(req).read()
		soup = BeautifulSoup(''.join(page))
		app_dict = {}

		app_dict['app_pkg_name'] = urlExtract.split("=")[-1]

		for div in soup.findAll(attrs={'class': 'document-title'}):
			for child in div.children:
				if not child.string == ' ':
					app_dict['app_name'] = child.string

		for div in soup.findAll(attrs={'class': 'document-subtitle','class': 'primary'}):
			for child in div.children:
				if not child.string == ' ':
					app_dict['developer_name'] = child.string

		for div in soup.findAll(attrs={'class': 'document-subtitle','class': 'category'}):
			for child in div.children:
				if not child.string == ' ':
					app_dict['app_category'] = child.string

		appDesc = ""
		for div in soup.findAll(attrs={'class': 'id-app-orig-desc'}):
			for desc in div.descendants:
				if type(desc.string).__name__ != "NoneType":
					appDesc = appDesc + desc.string
		app_dict['app_desc'] = appDesc

		whatsNew = ""
		for div in soup.findAll(attrs={'class': 'recent-change'}):
			for desc in div.descendants:
				if type(desc.string).__name__ != "NoneType":
					whatsNew = whatsNew + desc.string
		app_dict['whats_new'] = whatsNew

		for div in soup.findAll(attrs={'class': 'score'}):
			for child in div.children:
				if not child.string == ' ':
					app_dict['review_rating'] = round(eval(child.string),1)

		for div in soup.findAll(attrs={'class': 'reviews-num'}):
			for child in div.children:
				if not child.string == ' ':
					app_dict['review_count'] = eval(child.string.replace(",",""))

		pairing = 0
		key = ""
		value = ""
		for div in soup.findAll(attrs={'class': 'details-section-contents', 'class': 'meta-info'}):
			for child in div.children:
				if type(child.string).__name__ != "NoneType":
					if child.__class__.__name__ == "Tag":
						if pairing == 0:
							key = child.string.strip().replace(' ','_')
							pairing = 1
						else:
							value = child.string.strip()
							pairing = 0
							app_dict[key] = value
		if 'Developer' in app_dict:
			app_dict.pop('Developer', None)
		if 'Permissions' in app_dict:
			app_dict.pop('Permissions', None)
		if 'Report' in app_dict:
			app_dict.pop('Report', None)
		if 'Size' in app_dict:
			app_dict.pop('Size', None)
		if 'Installs' in app_dict:
			app_dict['Installs'] = eval(app_dict['Installs'].split(" ")[-1].replace(",",""))
		if 'Updated' in app_dict:
			app_dict['Updated'] = datetime.datetime.strptime(app_dict['Updated'], '%B %d, %Y').date().isoformat()
		if 'Offered_By' in app_dict:
			app_dict.pop('Offered_By', None)

		for div in soup.findAll(attrs={'class': 'content', 'class': 'contains-text-link'}):
			for child in div.children:
				if child.name == 'a':
					if child.string.strip() == 'Visit Website':
						app_dict['dev_website'] = child.attrs['href']
					elif child.string.strip().startswith('Email'):
						app_dict['dev_email'] = str(child.attrs['href']).split(":")[-1]

		for div in soup.findAll(attrs={'class': 'content', 'class': 'contains-text-link', 'class': 'physical-address'}):
			app_dict['dev_location'] = div.string

	# Return app_dict to write back to JSON file
	# 	app_info = {}
	# 	app_info_json = open("googlePlayStoreAppData.json",'r').read()
	# 	if len(app_info_json) > 0:
	# 		app_info = json.loads(app_info_json)
	# 	app_info[app_dict['app_pkg_name']] = app_dict
	# 	open("googlePlayStoreAppData.json",'w').write(json.dumps(app_info, sort_keys=True, indent=4))
	#Write to SQL now
		createSQLStatementAndInsert(dbHandle,app_dict)
	except urllib2.HTTPError, e:
		print 'HTTPError = ', str(e.code)
		#This is risky!!!!
		# June 19, 2015: Yes, this was risky commenting out this piece of code - Prajit
		# Don't be ridiculous, once you have collected some data you should not be deleting that data, right?
		# Have to monitor this properly
		#sqlStatement = "DELETE FROM `appurls` WHERE `app_url` = '"+urlExtract+"';"
		#databaseHandler.dbManipulateData(dbHandle, sqlStatement)
	except urllib2.URLError, e:
		print 'URLError = ' + str(e.reason)
	except httplib.HTTPException, e:
		print 'HTTPException'
	except Exception:
		print 'generic exception: ' + traceback.format_exc()

# Update "parsed_privacy_grade" column to mark app data has been parsed for privacy_grade website
def updateParsed(dbHandle, tableId):
	sqlStatement = "UPDATE `appurls` SET `parsed_privacy_grade`=1 WHERE `id`="+str(tableId)+";"
	databaseHandler.dbManipulateData(dbHandle, sqlStatement)

# Get URLs for privacy grade app data parsing
def getPrivacyGradeURLs(dbHandle):
	cursor = dbHandle.cursor()
	sqlStatement = "SELECT `id`, `privacy_grade_url` FROM `appurls` WHERE `parsed_privacy_grade` = 0;"
	try:
		cursor.execute(sqlStatement)
		for id, privacy_grade_url in cursor:
			# print id, privacy_grade_url
			extractAppDataToJson(privacy_grade_url)
			# extractAppDataAndStore(dbHandle,privacy_grade_url)
			# updateParsed(dbHandle,id)
	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise

from bs4 import BeautifulSoup
import urllib
import sys

def get_values(act_url):
	app_pkg_split = act_url.split('/')
	app_pkg_html = app_pkg_split[len(app_pkg_split) - 1].split('.')
	app_pkg = ".".join(app_pkg_html[:len(app_pkg_html) - 1])
	
	r = urllib.urlopen(act_url).read()
	soup = BeautifulSoup(r)
	#Parsing Table one : Considering rowspan also
	tbody1_iter = soup.find_all('tr', class_='permission-row')
	rs = 0
	rsval = ''
	table1_arr = []
	if tbody1_iter is not None:
		for i in tbody1_iter:
			childs = i.findChildren()
			if rs < 1:
				rs = int(childs[0]['rowspan'])
				rsval = childs[0].get_text()
				rs -= 1
				tmp = []
				tmp.append(rsval)
				tmp.append(childs[1].get_text())
				tmp.append(childs[2].get_text())
				table1_arr.append(tmp)
			else:
				rs -= 1
				tmp = []
				tmp.append(rsval)
				tmp.append(childs[0].get_text())
				tmp.append(childs[1].get_text())
				table1_arr.append(tmp)
	# Parsing Second table. Since no name using hacks
	tables = soup.find_all('table')
	tbody2 = None
	for i in tables:
		if i.has_attr	('id'):
			if i['id'] == 'third-table':
				tbody2 = i
	table2_arr = []
	if tbody2 is not None:
		all_tds = tbody2.find_all('td')
		row = len(all_tds)
		t2con = []
		i = 0
		while row > 0:
			t2con.append(all_tds[i].get_text())
			i+= 1
			row -= 1
			t2con.append(all_tds[i].get_text())
			i += 1
			row -= 1 
			table2_arr.append(t2con)
			t2con = []
	# Getting the application rating tag and extracting the letter grade
	apprating_tag = soup.find_all('p', 'app-pg-icon hidden-sm hidden-xs')
	apprating = apprating_tag[0].img['alt'][2]
	# Getting the application version 
	versiondiv = soup.find_all("div", "privacy-info-well")
	version = versiondiv[0].findChildren()[2].get_text()
	return app_pkg, version, apprating, table1_arr, table2_arr

def doTask():
	dbHandle = databaseHandler.dbConnectionCheck() # DB Open
	getPrivacyGradeURLs(dbHandle) # Get package names from extracting app details
	dbHandle.close() #DB Close

def main(argv):
	if len(sys.argv) != 1:
		sys.stderr.write('Usage: python getPrivacyGradeData.py\n')
		sys.exit(1)

	startTime = time.time()
	app_pkg, version, apprating, table1_arr, table2_arr = get_values(sys.argv[1]) 
	print "Application Package: " + app_pkg
	print "Application Version: " + str(version)
	print "Application Rating : " + apprating
	print "Application Table1 : " + str(table1_arr)
	print "\n"
	print "Application Table2 : " + str(table2_arr)	
	executionTime = str((time.time()-startTime)*1000)
	print "Execution time was: "+executionTime+" ms"

if __name__ == "__main__":
	main(sys.argv)