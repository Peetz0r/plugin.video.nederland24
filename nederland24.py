# This file is part of plugin.video.nederland24 ("Nederland24")

# Nederland24 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Nederland24 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Nederland24.  If not, see <http://www.gnu.org/licenses/>.


import os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib
import urllib2
import re
import urlparse
import httplib
from BeautifulSoup import BeautifulStoneSoup, SoupStrainer

xbmc.log("plugin.video.nederland24:: Starting Addon")

###
addon = xbmcaddon.Addon()
addonId = addon.getAddonInfo('id')

pluginhandle = int(sys.argv[1])
settings = xbmcaddon.Addon(id='plugin.video.nederland24')
xbmcplugin.setContent(pluginhandle, 'episodes')
#xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)  #enable for alphabetic listing
IMG_DIR = os.path.join(settings.getAddonInfo("path"),"resources", "media")

###
API_URL = 'http://ida.omroep.nl/aapi/?stream='
BASE_URL = 'http://livestreams.omroep.nl/live/npo/'
USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53'
REF_URL = 'http://www.npo.nl'

CHANNELS = [
  
  ["NPO 101","npo-101.png","thematv/101tv/101tv.isml/101tv.m3u8","Weg met suffe en saaie tv! Het is tijd voor NPO 101, het 24-uurs jongerenkanaal van BNN en de Publieke Omroep. Met rauwe en brutale programma's, van en voor jongeren. Boordevol hilarische fragmenten, spannende livegames, bizarre experimenten en nieuws over festivals en gratis concertkaartjes. Kijken dus!"],
  ["NPO Best","npo-best.png","thematv/best24/best24.isml/best24.m3u8","NPO Best brengt hoogtepunten uit zestig jaar televisiehistorie. Het is een feelgoodkanaal met 24 uur per dag de leukste, grappigste en meest spraakmakende programma's uit de Hilversumse schatkamer. NPO Best: de schatkamer van de publieke omroep."],
  ["NPO Cultura","npo-cultura.png","thematv/cultura24/cultura24.isml/cultura24.m3u8","Dit is het 'cultuurkanaal van de Publieke Omroep' met de beste recente en oudere 'kunst en expressie' over verschillende onderwerpen. Klassieke muziek, dans, literatuur, theater, beeldende kunst, film 'Waar cultuur is, is NPO Cultura'."],
  ["NPO Zapp Xtra","npo-zapp-xtra.png","thematv/zappelin24/zappelin24.isml/zappelin24.m3u8","NPO Zapp Xtra zendt dagelijks uit van half drie 's nachts tot half negen 's avonds. Familie24 is er op de tussenliggende tijd. Z@ppelin 24 biedt ruimte aan (oude) bekende peuterprogramma's en je kunt er kijken naar nieuwe kleuterseries. Op Familie24 zijn bekende programma's te zien en nieuwe programma's en documentaires die speciaal voor Familie24 zijn gemaakt of aangekocht."],
  ["NPO Doc","npo-doc.png","thematv/hollanddoc24/hollanddoc24.isml/hollanddoc24.m3u8","NPO Doc brengt op verschillende manieren en niveaus documentaires en reportages onder de aandacht. De programmering op NPO Doc is gecentreerd rond wekelijkse thema's, die gerelateerd zijn aan de actualiteit, de programmering van documentairerubrieken, van culturele instellingen en festivals."],
  ["NPO Humor TV","npo-humor-tv.png","thematv/humor24/humor24.isml/humor24.m3u8","NPO Humor TV is een uitgesproken comedykanaal: een frisse, Nederlandse humorzender met hoogwaardige, grappige, scherpe, jonge, nieuwe, satirische, humoristische programma's."],
  ["NPO Nieuws","npo-nieuws.png","thematv/journaal24/journaal24.isml/journaal24.m3u8","Via het themakanaal 'NPO Nieuws' kunnen de live televisieuitzendingen van het NOS Journaal worden gevolgd. De laatste Journaaluitzending wordt herhaald tot de volgende uitzending van het NOS Journaal."],
  ["NPO Poitiek","npo-politiek.png","thematv/politiek24/politiek24.isml/politiek24.m3u8","NPO Politiek is het digitale kanaal over de Nederlandse politiek in de breedste zin van het woord."],
  ["NPO 1","npo-1.png","tvlive/ned1/ned1.isml/ned1.m3u8","Televisiekijken begint op NPO 1. Van nieuws en actualiteiten tot consumentenprogramma's en kwaliteitsdrama. Programma's die over jou en jouw wereld gaan. Met verhalen die je herkent over mensen die zomaar in je straat kunnen wonen. Ook als er iets belangrijks gebeurt, in Nederland of in de wereld, kijk je NPO 1."],
  ["NPO 2","npo-2.png","tvlive/ned2/ned2.isml/ned2.m3u8","NPO 2 zet je aan het denken. Met programma's die verdiepen en inspireren. Als je wilt weten wat het verhaal achter de actualiteit is. Of als je het eens van een andere kant wilt bekijken. NPO 2 biedt het mooiste van Nederlandse en internationale kunst en cultuur, literatuur, documentaires, art-house films en kwaliteitsdrama."],
  ["NPO 3","npo-3.png","tvlive/ned3/ned3.isml/ned3.m3u8","Op NPO 3 vind je programma's waar jong Nederland zich in herkent en die je uitdagen een eigen mening te vormen. Met veel aandacht voor nieuwe media en experimentele vernieuwing brengt NPO 3 een gevarieerd aanbod van de dagelijkse actualiteit tot muziek, reizen, human interest, talkshows en documentaires."],
  ["NPO 3FM","npo-3fm.png","visualradio/3fm/3fm.isml/3fm.m3u8","Op NPO 3FM staat de liefde voor muziek centraal. Samen met de luisteraar vindt NPO 3FM nieuwe muziek, nieuw Nederlands poptalent en jong radiotalent. Je komt onze dj's vaak tegen op festivals en concerten."],
]

###
def index():
    for channel in CHANNELS:
        if settings.getSetting( channel[0] )=='true' and settings.getSetting( "GEOIP" )=='false':
            addLink(channel[0],channel[2], "playVideo", os.path.join(IMG_DIR, channel[1]), channel[3])
        else:
            #print ""
            xbmc.log("plugin.video.nederland24:: %s not set (GEOIP)" % str(channel[0]))
    if int(settings.getSetting ( "Depth_Acht" ))!=0:
        url='http://feeds.nos.nl/journaal20uur'
        depth=int(settings.getSetting ( "Depth_Acht" ))
        additionalChannels(url, depth)
    if int(settings.getSetting ( "Depth_Jeugd" ))!=0:
        url='http://feeds.nos.nl/vodcast_jeugdjournaal'
        depth=int(settings.getSetting ( "Depth_Jeugd" ))
        additionalChannels(url, depth)
    else:
        #print ""
        xbmc.log("plugin.video.nederland24:: No additional channels set")
    xbmcplugin.endOfDirectory(pluginhandle)

def resolve_http_redirect(url, depth=0):
    if depth > 10:
        raise Exception("Redirected "+depth+" times, giving up.")
    o = urlparse.urlparse(url,allow_fragments=True)
    conn = httplib.HTTPConnection(o.netloc)
    path = o.path
    if o.query:
        path +='?'+o.query
    conn.request("HEAD", path)
    res = conn.getresponse()
    headers = dict(res.getheaders())
    if headers.has_key('location') and headers['location'] != url:
        return resolve_http_redirect(headers['location'], depth+1)
    else:
        return url

def extract_url(chan):
    URL=API_URL+BASE_URL+(chan)
    req = urllib2.Request(URL)
    req.add_header('User-Agent', USER_AGENT)
    response = urllib2.urlopen(req)
    page = response.read()
    response.close()
    videopre=re.search(r'http:(.*?)url',page).group()
    prostream= (videopre.replace('\/', '/'))
    video = resolve_http_redirect(prostream, 3)
    return video

def addLink(name, url, mode, iconimage, description):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name,
    	                                  "Plot":description,
    	                                  "TVShowTitle":name,
    	                                  "Playcount": 0,
    	                                  })
    
    liz.setProperty("fanart_image", os.path.join(IMG_DIR, "fanart.png"))
    liz.setProperty('IsPlayable', 'true')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def additionalChannels(url, depth):
    i = 0
    #depth = depth
    URL = url
    #URL = 'http://feeds.nos.nl/journaal'
    items = SoupStrainer('item')
    for tag in BeautifulStoneSoup(urllib2.urlopen(URL).read(), parseOnlyThese=items):
        title = tag.title.contents[0]
        url = tag.guid.contents[0]
        img = os.path.join(IMG_DIR, "placeholder.png")
        addLink(title, url, "playVideo", img, '')
        i += 1
        if i == int(depth):
            break

def playVideo(url):
    media = url
    finalUrl=""
    if media and media.startswith("http://"):
        finalUrl=media
    else:
        URL=API_URL+BASE_URL+media
        req = urllib2.Request(URL)
        req.add_header('User-Agent', USER_AGENT)
        req.add_header('Referer', REF_URL)
        response = urllib2.urlopen(req)
        page = response.read()
        response.close()
        videopre=re.search(r'http:(.*?)url',page).group()
        prostream= (videopre.replace('\/', '/'))
        finalUrl = resolve_http_redirect(prostream)
    if finalUrl:
        listitem = xbmcgui.ListItem(path=finalUrl)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)

def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))


if mode == "playVideo":
    playVideo(url)
else:
    index()

