#!/usr/bin/python

#http://wwwsearch.sourceforge.net/old/ClientCookie/
import ClientCookie
#http://wwwsearch.sourceforge.net/old/ClientForm/
import ClientForm
import urllib
import json
import sys
import getpass
from urllib import urlencode
import mechanize
import cookielib

def _get_access_token():
	br = mechanize.Browser()

	# Cookie Jar
	cj = cookielib.LWPCookieJar()
	br.set_cookiejar(cj)

	# Browser options
	br.set_handle_equiv(True)
	#br.set_handle_gzip(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)

	# Follows refresh 0 but not hangs on refresh > 0
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

	# User-Agent (this is cheating, ok?)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686;en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9Firefox/3.0.1')]

	user_perms = ["email", "publish_actions", "user_about_me", "user_actions.music", "user_actions.news", "user_actions.video", "user_activities", "user_birthday", "user_education_history", "user_events", "user_games_activity", "user_groups", "user_hometown", "user_interests", "user_likes", "user_location", "user_notes", "user_photos", "user_questions", "user_relationship_details", "user_relationships", "user_religion_politics", "user_status", "user_subscriptions", "user_videos", "user_website", "user_work_history"]
	friend_perms = ["friends_about_me", "friends_actions.music", "friends_actions.news", "friends_actions.video", "friends_activities", "friends_birthday", "friends_education_history", "friends_events", "friends_games_activity", "friends_groups","friends_hometown","friends_interests","friends_likes", "friends_location","friends_notes", "friends_photos","friends_questions", "friends_relationship_details","friends_relationships", "friends_religion_politics","friends_status", "friends_subscriptions", "friends_videos", "friends_website", "friends_work_history"]
	extended_perms = ["ads_management","create_event","create_note","export_stream","friends_online_presence","manage_friendlists","manage_notifications","manage_pages","offline_access","photo_upload","publish_checkins","publish_stream","read_friendlists","read_insights","read_mailbox","read_page_mailboxes","read_requests","read_stream","rsvp_event","share_item","sms","status_update","user_online_presence","video_upload","xmpp_login"]

	user_perms = ",".join(user_perms)
	friend_perms = ",".join(friend_perms)
	extended_perms = ",".join(extended_perms)
	all_perms = ",".join([user_perms,friend_perms,extended_perms])

	r = br.open('https://graph.facebook.com/oauth/authorize?type=user_agent&client_id=163193033824504&redirect_uri=http://www.yahoo.com&scope='+all_perms)#email,user_birthday,user_online_presence,read_stream,offline_access')

	# Select the first (index zero) form
	br.select_form(nr=0)

	# User credentials
	br.form['email'] = _usr_id
	br.form['pass'] = _pswrd
	
	# Login
	r = br.submit()
	
	if "access_token" in r.geturl():
		token_url = r.geturl()
		amp = token_url.find("&")
		eql = token_url.find('=')
		if amp>0:
			return token_url[(eql+1):amp]
		return token_url[(eql+1):]

	i=0
	while(i<10):
		i += 1
		br.select_form(nr=2)
		r = br.submit()
		print "r url: "+r.geturl()
		#sleep(10)
		if "access_token" in r.geturl():
			token_url = r.geturl()
			print "TOKEN URL: "+token_url
			amp = token_url.find("&")
			eql = token_url.find('=')
			if amp>0:
				return token_url[(eql+1):amp]
			return token_url[(eql+1):]

	raise ValueError("Unable to get access_token.")


def _post_request(api_url, post_data):
	"""Make request using supplied parameters and return the response, unless an error occurs"""
	try:
		#make the request and return response
		response = ClientCookie.urlopen(url=api_url,data=post_data)
		return response
	except HTTPError as exc:
		#tell user the details of the error
		raise HTTPException(exc)
		
def _authenticate():
	"""Logs the user in to Facebook"""
	# Create special URL opener (for User-Agent) and cookieJar
	cookieJar = ClientCookie.CookieJar()

	opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(cookieJar))
	opener.addheaders = [("User-agent","Mozilla/5.0 (compatible)")]
	ClientCookie.install_opener(opener)
	fp = ClientCookie.urlopen("https://graph.facebook.com/oauth/authorize?type=user_agent&client_id=163193033824504&redirect_uri=http://www.yahoo.com&scope=email,user_birthday,user_online_presence,read_stream,offline_access")
	forms = ClientForm.ParseResponse(fp)
	fp.close()

	form = forms[0]

	# supply user id and pw
	form["email"]  = _usr_id
	form["pass"] = _pswrd
	
	fp = ClientCookie.urlopen(form.click())
	#print "IN AUTHENTICATE:",fp.geturl()
	fp.close()
		

#user's email/fb id
_usr_id = sys.argv[1]
#user's FB id (thee number)
_user_fb_id = json.load(ClientCookie.urlopen("http://graph.facebook.com/"+_usr_id))["id"]
# prompt user for pw and don't echo it as user is typing
#_pswrd = sys.argv[3]
_pswrd = getpass.getpass(prompt="".join(["Enter Facebook Password for (",_usr_id,"): "]))

def _my_faves(nbr):
	#log in to FB
	_authenticate()
	#get the ranking data
	f = ClientCookie.urlopen("http://www.facebook.com/ajax/typeahead/search/first_degree.php?__a="+_user_fb_id+"&filter=user&viewer="+_user_fb_id+"&token=&stale_ok=0")
	#print f.read()
	for n, dic in enumerate(json.loads(f.read()[9:])["payload"]["entries"]):	
		#print "".join([str(dic["uid"]),",",str(dic["index"]),",",dic["photo"]])
		if n == 0:
			continue
		usr_info = json.load(ClientCookie.urlopen("http://graph.facebook.com/"+str(dic["uid"])))
		print n+1, usr_info["name"]
		if (n+1)==int(nbr):
			return

#print '-'*15
print "GETTIN ACCES TOKEN"
token = _get_access_token()		
print "GOT ACCES TOKEN: ", token

#print "A_T:",token


FACEBOOK_APP_ID     = '163193033824504'
FACEBOOK_APP_SECRET = '5abefada76940a5b1a179324694ca8d5'
FACEBOOK_PROFILE_ID = _usr_id

def _about_me():
	try:
		me_dict = json.load(ClientCookie.urlopen(url="https://graph.facebook.com/me?access_token="+token))
		for k,v in me_dict.iteritems():
			print k, "   :   ",v
	except Exception as exc:
		print exc

def _post_msg_to_wall(target, message):
	try:
		args = dict(message=message, access_token=token)
		encoded_args = urlencode(args)
		#print "Encoded args:", encoded_args
		response = ClientCookie.urlopen("https://graph.facebook.com/"+target+"/feed?", data=encoded_args)
		return response.read()
	except Exception as exc:
		print "EXCEPTION!!"
		print exc.read()
		
def _my_wall():
	try:
		me_dict = json.load(ClientCookie.urlopen(url="https://graph.facebook.com/me/feed?limit=3&access_token="+token))
		print me_dict["data"]
		#for k,v in me_dict.iteritems():
		#	print k, "   :   ",v
	except Exception as exc:
		print exc

def _create_event():
	name = raw_input('Enter the name of the event: ')
	description = raw_input('Enter the event description: ')
	location = raw_input('Enter the location of the event : ')
	start_time = raw_input('Enter the starting time of the event i.e. 2012-01-25: ')
	#end_time = raw_input('Enter the ending time of the event: ')
	privacy_type = raw_input('Enter the event privacy (OPEN, SECRET, FRIENDS): ')
	
	try:
		args = dict(name=name, description=description, location=location, start_time=start_time,privacy_type=privacy_type , access_token=token)
		encoded_args = urlencode(args)
		#print encoded_args
		response = ClientCookie.urlopen("https://graph.facebook.com/"+_usr_id+"/events", data=encoded_args)
	except Exception as exc:
		print exc
	

def _make_status(message):
	try:
		args = dict(message=message, privacy={'value':'ALL_FRIENDS'}, access_token=token)
		encoded_args = urlencode(args)
		#print "Encoded args:", encoded_args
		response = ClientCookie.urlopen("https://graph.facebook.com/"+_usr_id+"/feed?", data=encoded_args)
		return response.read()
	except Exception as exc:
		print exc

while (1):
	inp = raw_input("What would you like to do?\n")
	#expecting format: 'fb method opts'
	inp = inp.split(" ")
	method = inp[1]
	if method=="me":
		_about_me()
	elif method=="faves":
		_my_faves(inp[2])
	elif method=="wall":
		_my_wall()
	elif method=="post":
		msg = ""
		for elem in inp:
			if elem != inp[0] and elem != inp[1] and elem != inp[2]:
				msg = " ".join([msg,elem])
		_post_msg_to_wall(inp[2],msg)
	elif method=="event":
		_create_event()
	elif method=="status":
		msg = ""
		for elem in inp:
			if elem != inp[0] and elem != inp[1]:
				msg = " ".join([msg,elem])
		_make_status(msg)
	elif method=="exit":
		break
	else:
		exit("Undefined action specified.")