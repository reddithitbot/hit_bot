import praw
import urllib2
import random
#from time import gmtime, strftime
from datetime import datetime
from pytz import timezone
import time

G_ADFLYAPI = "http://api.adf.ly/api.php?key=XXXXXXXXX&uid=XXXXXXX&advert_type=int&domain=adf.ly&url="

G_TYPE_BADURL = 10
G_TYPE_UNHANDLEDHTTP = 20
G_TYPE_ADFLYDELETED = 30
G_TYPE_DEADHIT = 40
G_TYPE_CANTVIEW = 50
G_TYPE_INFO = 60
G_TYPE_RESURRECTED = 70

G_MSG_CANTVIEW = "Unable to view HIT because of qualification requirements."
G_MSG_ADFLYDELETED = "Unable to check HIT because the Adf.ly link has been deleted."
G_MSG_UNHANDLEDURL = "Unable to check HIT because a url returned an unhandled error code. Error code: #errcode#"
G_MSG_BADURL = "Unable to check HIT because a url for #sitename# returned a 404 Not Found error."
G_MSG_BOTINFO = "*[I am a bot](http://www.reddit.com/r/hit_bot/), and this action was performed automatically.  I am designed to help determine when HITs are no longer available.  Please [contact the mods of this subreddit](http://www.reddit.com/message/compose?to=%2Fr%2F#subname#) if you have any questions or concerns.*"
G_MSG_LINK = "*Support your local programmer! [#link#](#link#)*"
G_MSG_DEADHIT = "Dead HIT @ #time#."
G_MSG_RESURRECTED = "Resurrected @ #time#."
G_MSG_TOLINK = "[Requester's TO Profile](http://turkopticon.differenceengines.com/#reqid#)"
G_MSG_TOREVIEWLINK = "[Review Requester](http://turkopticon.differenceengines.com/report?requester%5Bamzn_id%5D=#reqid#)"
G_MSG_INFO = "HIT Info: " + G_MSG_TOLINK + " - " + G_MSG_TOREVIEWLINK


#####SETTINGS#####
G_DEBUG = 1
G_COMMENTS_ON = 1
G_VERBOSE = 0
G_SETFLAIR_ON = 1

G_TIMEZONE = "US/Eastern"

G_USER_AGENT = "MTurk HIT Bot 0.1 by /u/ProgrammingHotness runs as /u/HIT_Bot"
#G_SUBREDDIT_NAME = "noaccounttest"
G_SUBREDDIT_NAME = "HitsWorthTurkingFor"
G_ME = "hit_bot"


def getLastUpdated():
  return "\n\n*Last checked: " + getTime() + "*"

def getCommentText(commentType, optInfo = "", withFooter = 1):
  footer = "\n\n" + G_MSG_BOTINFO.replace("#subname#",G_SUBREDDIT_NAME) + "\n\n" + G_MSG_LINK.replace("#link#", getAdFlyLink())
  msgBody = ""
  if (commentType == G_TYPE_BADURL):
    msgBody = G_MSG_BADURL.replace("#sitename#", optInfo)
  elif (commentType == G_TYPE_UNHANDLEDHTTP):
    msgBody = G_MSG_UNHANDLEDURL.replace("#errcode#", optInfo)
  elif (commentType == G_TYPE_ADFLYDELETED):
    msgBody = G_MSG_ADFLYDELETED
  elif (commentType == G_TYPE_CANTVIEW):
    msgBody = G_MSG_CANTVIEW
  elif (commentType == G_TYPE_DEADHIT):
    msgBody = G_MSG_DEADHIT.replace("#time#", getTime())
  elif (commentType == G_TYPE_INFO):
    msgBody = G_MSG_INFO.replace("#reqid#", optInfo)
  elif (commentType == G_TYPE_RESURRECTED):
    msgBody = G_MSG_RESURRECTED.replace("#time#", getTime())

  if (withFooter == 1):
    return msgBody + footer
  else:
    return msgBody
    
def editComment(commentType, commentText, comment):
  #substring lengths chosen because these lengths differentiate between the comments
  #it allows me to tell the difference between them
  keepBody = 0
  
  if ((commentType == G_TYPE_BADURL) and (comment.body[:37] == G_MSG_BADURL[:37])): 
    keepBody = 1
  elif ((commentType == G_TYPE_UNHANDLEDHTTP) and (comment.body[:37] == G_MSG_UNHANDLEDURL[:37])):
    keepBody = 1
  elif ((commentType == G_TYPE_ADFLYDELETED) and (comment.body[:37] == G_MSG_ADFLYDELETED[:37])):
    keepBody = 1
  elif ((commentType == G_TYPE_CANTVIEW) and (comment.body[:14] == G_MSG_CANTVIEW[:14])):
    keepBody = 1
  elif ((commentType == G_TYPE_DEADHIT) and (comment.body[:10] == G_MSG_DEADHIT[:10])):
    keepBody = 1
  elif ((commentType == G_TYPE_DEADHIT) and (comment.body[:8] == G_MSG_INFO[:8])):
    keepBody = 2 #was alive, now dead, keep the INFO
  elif ((commentType == G_TYPE_DEADHIT) and (comment.body[:8] == G_MSG_RESURRECTED[:8])):
    keepBody = 2 #was alive, now dead, keep the INFO
  elif ((commentType == G_TYPE_INFO) and (comment.body[:10] == G_MSG_DEADHIT[:10])):
    keepBody = 2 #was dead, now alive, keep the history
    commentType = G_TYPE_RESURRECTED
  elif ((commentType == G_TYPE_INFO) and (comment.body[:8] == G_MSG_INFO[:8])):
    keepBody = 1

  if (keepBody == 1):
    #I want to keep the entire message body
    #just new to update/add Last Updated reply
    addLastUpdateReply(comment)
    return 0
  elif (keepBody == 2):
    #I need to keep the original body and prepend a new message
    comment.edit(getCommentText(commentType, withFooter=0) + "\n\n" + comment.body)
    addLastUpdateReply(comment)
    return 1
  else:
    #I need to replace the entire message
    comment.edit(commentText)
    addLastUpdateReply(comment)
    return 1
   
def addLastUpdateReply(comment):
  #check to see if reply exists
  if (len(comment.replies) > 0):
    for rep in comment.replies:
      if (rep.author.name == G_ME):
        rep.edit(getLastUpdated())
        return
  #if we get here, reply did not exist, create it
  comment.reply(getLastUpdated())
   
   
def postComment(commentType, submission, optInfo = ""):
  try:
    commentText = getCommentText(commentType, optInfo)
    for comment in submission.comments:
      #print dir(comment)
      if (comment.author.name == G_ME):
        if (G_DEBUG):
          print "Already commented. Editing existing comment."
        if (G_COMMENTS_ON != 1):
          return 0
        return editComment(commentType, commentText, comment)
        #comment.edit(commentText + "\n\n*Last updated: " + getTime() + "*")
    if (G_COMMENTS_ON != 1):
      return 0
    submission.add_comment(commentText)
    return 0 #new comment, don't need to set flair
  except:
    return 0

def getTime():
  tz = timezone(G_TIMEZONE)
  fmt = "%I:%M%p %Z%z"
  loc = tz.localize(datetime.now())
  return loc.strftime(fmt)
  #return strftime("%I:%M%p GMT", gmtime())

def getSite():
  sites = ['http://www.randomkittengenerator.com/','http://www.animal-photos.org/shuffle/','http://www.outdoor-photos.com/shuffle/','http://ivyjoy.com/quote.shtml','http://www.cybersalt.org/clean-jokes/random-jokes','http://www.gcfl.net/randomfunny.php']
  s = random.randint(0,len(sites)-1)
  return sites[s]

  
def getAdFlyLink():
  site = getSite()
  url = G_ADFLYAPI + site
  resp = urllib2.urlopen(url)
  link = resp.read()
  return link

def parseURL(txt):
  if (G_VERBOSE):
    print "Title Comment:",txt
  try:
    txt = txt.replace("&lt;","<").replace("&gt;",">").replace("&amp;amp;","&")
    txt = txt.split("<a href=\"")
    txt = txt[1].split("\">")
    if (G_DEBUG):
      print txt[0]
    return txt[0]
  except:
    return ""

def getURLFromADFLY(_url, sub):
  if (_url.find("mturk.com") == -1):
    try:
      resp = urllib2.urlopen(_url)
      adfly_html = resp.read()
    except urllib2.HTTPError, e:
      if (e.code == 404):
        print "Bad adfly link."
        postComment(G_TYPE_BADURL, sub, "Adf.ly")
      else:
        print "Unhandled code: ", e.code  
        postComment(G_TYPE_UNHANDLEDHTTP, sub, str(e.code))
      return ""
    except:
      return ""
    
    if (adfly_html.find("Sorry, but that link has been deleted.") != -1):
      print "Adfly link deleted."
      postComment(G_TYPE_ADFLYDELETED, sub)
      return ""
 
    try:
      turk_url = adfly_html.split("var zzz = '")
      turk_url = turk_url[1].split("';",1)
      return turk_url[0]
    except:
      return ""
  else:
    return _url

    
def getMTurkHTML(_url, sub):
    html = ""
    try:
      resp = urllib2.urlopen(_url)
      html = resp.read()
    except urllib2.HTTPError, e:
      if (e.code == 404):
        print "Bad mturk URL."
        postComment(G_TYPE_BADURL, sub, "mturk.com")
      else:
        print "Unhandled code: ", e.code  
        postComment(G_TYPE_UNHANDLEDHTTP, sub, str(e.code))
      return ""
    except:
      return ""
    return html

def parseRequesterID(txt):
  try:
    _reqid = txt.split("name=\"requesterId\" value=\"")
    _reqid = _reqid[1].split("\">")
    _reqid = _reqid[0]
    if (_reqid.find("&amp;") != -1):
      _reqid = _reqid.split("&amp;")
      _reqid = _reqid[0]
    return _reqid
  except:
    _reqid = ""

  try:
    _reqid = txt.split("requesterId=")
    _reqid = _reqid[1].split("\">")
    _reqid = _reqid[0]
    if (_reqid.find("&amp;") != -1):
      _reqid = _reqid.split("&amp;")
      _reqid = _reqid[0]
    return _reqid
  except:
    _reqid = ""
  return ""
    
def init():
  print "#########################INIT MESSAGES#######################"
  print G_USER_AGENT
  print "Running on /r/" + G_SUBREDDIT_NAME

  if (G_DEBUG == 1):
    print "Debug mode is ON."
    if (G_VERBOSE == 1):
      print "Verbose mode is ON."
    else:
      print "Verbose mode is OFF."

  if (G_COMMENTS_ON == 1):
    print "Comments are ON."
  else:
    print "Comments are OFF."

  if (G_SETFLAIR_ON == 1):
    print "Set flair is ON."
  else:
    print "Set flair is OFF."
  print "#############################################################"
 
     

r = praw.Reddit(user_agent=G_USER_AGENT)

uname = "HIT_Bot"
passwd = "passwd"
r.login(uname,passwd)

subreddit = r.get_subreddit(G_SUBREDDIT_NAME)

init()

G_DEBUG_SUB = ""
#G_DEBUG_SUB = "http://www.reddit.com/r/HITsWorthTurkingFor/comments/18budr/us_political_attitudes_and_personality_jarret/"

if (G_DEBUG_SUB != ""):
  G_COMMENTS_ON = 0
  sub = r.get_submission(G_DEBUG_SUB)
  print sub.selftext_html
  _url = parseURL(sub.selftext_html)
  print "url parsed from comment:", _url
  _url = getURLFromADFLY(_url, sub)
  print "url after adfly parse:", _url
  _html = getMTurkHTML(_url, sub)
  if (_html == ""):
    print "error retrieving html"
  _reqid = parseRequesterID(_html)
  print "request id:", _reqid
  exit()




while (1):
  print "Sleeping..."
  time.sleep(45)
  try:
    for sub in subreddit.get_hot(limit=50):
      print "################"
      print sub.title
      _html = ""
      _url = ""
      
      #attempt to parse link from title comment
      _url = parseURL(sub.selftext_html)
      if (_url == ""):
        print "No link found."
        continue
      
      #if a link is found, check to see if it's adf.ly or mturk.com
      if ((_url.find("mturk.com") == -1) and (_url.find("adf.ly") == -1) and (_url.find("j.gs") == -1) and (_url.find("q.gs") == -1)):
        print "Not a supported link."
        continue
    
      #if not a direct mturk.com link, go to adf.ly and parse it	
      _url = getURLFromADFLY(_url, sub)
      if (_url == ""):
        continue;
    
      #at this point, the URL should be for mturk
      if (_url.find("mturk.com") == -1):
        print "Not a supported link."
        continue
    
      #if the user has qualifications turned on, turn them off
      #I haven't noticed that this makes a difference.
      if (_url.find("qualifiedFor=on") != -1):
        _url = _url.replace("qualifiedFor=on", "qualifiedFor=off")
    
      #try and retrieve the HIT
      _html = getMTurkHTML(_url, sub)
      if (_html == ""):
        continue;
    
      print _url
      if (_html.find("Your Qualifications do not meet the requirements to preview HITs in this group.") != -1):
        print "Cannot view HIT."
        postComment(G_TYPE_CANTVIEW, sub)
      elif ((_html.find("Your search did not match any HITs.") != -1) or (_html.find("There are no more available HITs in this group.") != -1)):
        print "HIT dead."
        res = postComment(G_TYPE_DEADHIT, sub)
        if ((G_SETFLAIR_ON == 1) and (res == 1)):
          subreddit.set_flair(sub, 'Dead', 'dead')
      else:
        if (G_VERBOSE):
          print "Turk HTML:", _html
        print "HIT still active."
        
        #try and parse requesterId
        #<a href="/mturk/searchbar?selectedSearchType=hitgroups&amp;requesterId=A23NM9GEAV0LLA">Kirsten M</a>
        #<input type="hidden" name="requesterId" value="A1DGSB2GKASN7Q">
        _reqid = parseRequesterID(_html)
      
        if (_reqid != ""):
          print "ReqId:", _reqid
          res = postComment(G_TYPE_INFO, sub, _reqid)
          if ((G_SETFLAIR_ON == 1) and (res == 1)):
            subreddit.set_flair(sub) #clears flair
        else:
          print "Cannot find RequesterId."
    
      #print urllib2.unquote(sub.selftext_html) #or sub.selftext
      #for com in sub.comments:
      #  print com.body
  except:
    print "Error retrieving subs."
    continue
