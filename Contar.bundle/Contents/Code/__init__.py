####################################################################################################
PLUGIN_PREFIX   = '/video/contar'
PLUGIN_API_URL  = 'https://api.cont.ar/api/v2/'

####################################################################################################
def Start():
    Plugin.Nice(10)
    ObjectContainer.title1  = L("TITLE")
    ObjectContainer.content = "items"
    DirectoryObject.thumb   = R("icon-category.png")    

####################################################################################################
@handler(PLUGIN_PREFIX, L("TITLE"), R("icon-default.png"))
def MainMenu():    
    oc = ObjectContainer()
    
    oc.add(PrefsObject(title=L("MENU_PREFS"), thumb=R("icon-preferences.png")))
    oc.add(InputDirectoryObject(key=Callback(Search), prompt=L("PROMPT_SEARCH"), title=L("MENU_SEARCH"), thumb=R("icon-search.png")))
    
    oc.add(DirectoryObject(key=Callback(GetPromotions), title=L("MENU_NEWS"), thumb=R("icon-news.png")))
    oc.add(DirectoryObject(key=Callback(GetSections), title=L("MENU_CATEGORIES"), thumb=R("icon-categories.png")))
    oc.add(DirectoryObject(key=Callback(GetChannels), title=L("MENU_CHANNELS"), thumb=R("icon-channels.png")))
    oc.add(DirectoryObject(key=Callback(GetLive), title=L("MENU_LIVE"), thumb=R("icon-live.png")))

    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/news')
def GetPromotions():

    url = PLUGIN_API_URL + 'promotions'
    promotions = JSON.ObjectFromURL(url)

    oc = ObjectContainer(title2=L("MENU_NEWS"), no_cache=True)
    for promotion in promotions['data']:
        is_show = promotion['is_serie']
        is_stream = promotion['is_stream']
        item = promotion['item']

        if is_show:
            image  = promotion['mbg']
            oc.add(CreateTVShow(item=item, image=image))

        elif is_stream:
            title2 = promotion['cta']
            image  = promotion['mbg']
            oc.add(CreateLiveStream(item=item, image=image, title2=title2))

    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/live')
def GetLive():
    oc = ObjectContainer(title2=L("MENU_LIVE"), no_cache=True)
    
    url = PLUGIN_API_URL + 'live'
    channels = JSON.ObjectFromURL(url)['data']

    for channel in channels:
        image = channel['cover']
        oc.add(CreateLiveStream(item=channel, image=image))
    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/sections')
def GetSections():
    
    url = PLUGIN_API_URL + 'section'
    sections = JSON.ObjectFromURL(url)['data']

    oc = ObjectContainer(title2=L("MENU_CATEGORIES"), no_cache=True)
    
    oc.add(DirectoryObject(key=Callback(GetKids), title=L("MENU_KIDS"), thumb=R("icon-kids.png")))
    for section in sections:
        if section['name']=='Destacados':
            thumb=R("icon-star.png")
        elif section['name']=='Recomendados':
            thumb=R("icon-recommend.png")
        else:
            thumb=R("icon-category.png")
        oc.add(DirectoryObject(key=Callback(GetFullSection, sectionid=section['id']), title=section['name'], thumb=thumb))
    return oc

@route(PLUGIN_PREFIX + '/sections/kids')
def GetKids():

    url = PLUGIN_API_URL + 'kids/section'
    sections = JSON.ObjectFromURL(url)['data']

    oc = ObjectContainer(title2=L("MENU_KIDS"))
    for section in sections:
        oc.add(DirectoryObject(key=Callback(GetKidsSection, sectionid=section['id'], sectiontitle=section['name']), title=section['name']))
    return oc

@route(PLUGIN_PREFIX + '/sections/full/{sectionid}')
def GetFullSection(sectionid):
    
    url = PLUGIN_API_URL + 'full/section/' + sectionid + '?sort=suggested'
    section  = JSON.ObjectFromURL(url)['data']
    
    oc = ObjectContainer(title2=section['title'])
    CreateSectionObject(section=section['videos'], container=oc)
    return oc

@route(PLUGIN_PREFIX + '/sections/kids/{sectionid}')
def GetKidsSection(sectionid, sectiontitle):
    
    url = PLUGIN_API_URL + 'kids/section/' + sectionid + '?sort=suggested'
    section  = JSON.ObjectFromURL(url)

    oc = ObjectContainer(title2=sectiontitle)
    CreateSectionObject(section=section, container=oc)
    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/channels')
def GetChannels():

    url = PLUGIN_API_URL + 'channel/list'
    channels = JSON.ObjectFromURL(url)['data']

    oc = ObjectContainer(title2=L("MENU_CHANNELS"), no_cache=True)
    for channel in channels:
        oc.add(DirectoryObject(key=Callback(GetChannel, channelid=channel['id']), title=channel['name'], thumb=channel['logoImage']))
    return oc

@route(PLUGIN_PREFIX + '/channels/{channelid}')
def GetChannel(channelid):

    url = PLUGIN_API_URL + 'channel/info/' + channelid
    info = JSON.ObjectFromURL(url)['data']

    channelname = info['name']
    config = info['configuration']
    mainpage = config['page']

    oc = ObjectContainer(title2=channelname)
    if mainpage['type'] == 'SERIE':
        oc.add(DirectoryObject(key=Callback(GetChannelPageShows, channelid=channelid, channelname=channelname), title=mainpage['label']))

    tabs = config['tabs']
    for tabname in tabs:
        tab = tabs[tabname]
        if tab['type'] == 'SERIES' or tab['type'] == 'VIDEOS':
            oc.add(DirectoryObject(key=Callback(GetChannelTab, channelid=channelid, channeltabname=tabname), title=tab['name']))
    return oc

@route(PLUGIN_PREFIX + '/channels/{channelid}/shows')
def GetChannelPageShows(channelid, channelname):
    
    url = PLUGIN_API_URL + 'channel/series/' + channelid
    channelshows  = JSON.ObjectFromURL(url)['data']

    oc = ObjectContainer(title2=channelname)
    for show in channelshows:
        oc.add(CreateTVShow(item=show))
    return oc

@route(PLUGIN_PREFIX + '/channels/{channelid}/tab/{channeltabname}')
def GetChannelTab(channelid, channeltabname):
    
    url = PLUGIN_API_URL + 'channel/info/' + channelid
    info = JSON.ObjectFromURL(url)['data']

    config = info['configuration']
    tabs = config['tabs']
    currenttab = tabs[channeltabname]
    
    oc = ObjectContainer(title2=currenttab['name'])
    
    for data in currenttab['data']['data']:
        if isinstance(data, dict):
            if currenttab['type'] == 'SERIES':
                oc.add(CreateTVShow(data))
            elif currenttab['type'] == 'VIDEOS':
                oc.add(CreateVideoStream(data))           
    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/show/{showid}')
def GetSeasons(showid):
    
    url = PLUGIN_API_URL + 'serie/' + showid
    show = JSON.ObjectFromURL(url)['data']
    seasons = show['seasons']['data']
    showname = show['name']

    oc = ObjectContainer(title2=showname)
    for season in seasons:
        
        seasonid = season['id']
        seasonname = 'Temporada ' +  season['name']
        seasonindex = int(season['name']) if season['name'] else 0
        image = season['seasonImage']
        rating_key = str(showid) + '/' + str(seasonid)
        

        oc.add(SeasonObject(
            key=Callback(GetEpisodes, showid=showid, seasonid=seasonid),
            rating_key=rating_key,
            show=showname,
            index=seasonindex,
            title=seasonname,
            thumb=image,
        ))

    return oc

@route(PLUGIN_PREFIX + '/show/{showid}/season/{seasonid}')
def GetEpisodes(showid, seasonid):

    url = PLUGIN_API_URL + 'serie/' + showid
    show = JSON.ObjectFromURL(url)['data']
    seasons = show['seasons']['data']

    currentseason = {}
    for season in seasons:
        if int(season["id"]) == int(seasonid):
            currentseason = season 

    seasonname = 'Temporada ' +  season['name']

    oc = ObjectContainer(title2=seasonname)
    videos = currentseason["videos"]["data"]
    for video in videos:
        if isinstance(video, dict):
            oc.add(CreateVideoStream(video))
    return oc

####################################################################################################
def CreateSectionObject(section, container):
    
    for sestionchilditem in section['data']:
        is_show  = sestionchilditem['type'] == 'SERIE'
        is_stream = sestionchilditem['type'] == 'STREAM' or sestionchilditem['type'] == 'VIDEOS'
        
        if is_show:            
            container.add(CreateTVShow(item=sestionchilditem))
        elif is_stream:
            image = sestionchilditem['mobile_image']
            container.add(CreateLiveStream(item=sestionchilditem, image=image))

    return container

def CreateTVShow(item, image=None):
    
    showid = item['uuid']
    showname = item['name']
    summary = item['story_large']
    episode_count = int(item['totalEpisodes']) if item['totalEpisodes'] else 0
    image = image or item['seasonImage']

    return TVShowObject(
        key=Callback(GetSeasons, showid=showid),
        rating_key=showid,
        title=showname,
        summary=summary,
        episode_count=episode_count,
        thumb=image
    )

def CreateLiveStream(item, image, title2 = ""):
    key = String.UUID()
    title = item['title']
    if title2 != "":
        title = title + " - " + title2
    liveurl = item['hls']
    return CreateVideoClipObject(key=key, url=liveurl, title=title, durationinms=0, summary="", thumb=image)

def CreateVideoStream(video):
    
    key = video['id']

    url = PLUGIN_API_URL + 'videos/' + key
    videoinfo = JSON.ObjectFromURL(url)['data']
 
    title = videoinfo["name"]
    summary = videoinfo["synopsis"]
    image = videoinfo["posterImage"]
    durationinms = int(videoinfo["length"])*1000 if videoinfo["length"] else 0
    url = "https://localhost/hlsstreamnotfound"

    for stream in videoinfo["streams"]:
         if stream["type"] == "HLS":
            url = stream["url"]

    return CreateVideoClipObject(key=key, url=url, title=title, durationinms=durationinms, summary=summary, thumb=image)

####################################################################################################
@route(PLUGIN_PREFIX + '/video/{key}', include_container=bool)
def CreateVideoClipObject(key, url, title, durationinms, summary, thumb, include_container=False, **kwargs):

    videoclip_obj = VideoClipObject(
        key = Callback(CreateVideoClipObject, key=key, url=url, title=title, durationinms=durationinms, summary=summary, thumb=thumb, include_container=True),
        rating_key = key,
        title = title,
        duration = int(durationinms),
        summary = summary,
        thumb=thumb,
        items = [
            MediaObject(
                parts = [PartObject(key=HTTPLiveStreamURL(url))],
                audio_channels = 2,
                optimized_for_streaming = True,
                video_resolution = resolution,
            ) for resolution in [1080, 720, 480, 360, 240]
        ]
    )

    if include_container:
        return ObjectContainer(objects=[videoclip_obj])
    else:
        return videoclip_obj

####################################################################################################
@route(PLUGIN_PREFIX + '/search')
def Search(**kwargs):
    
    query = String.Quote(kwargs['query'])
    isKids = '1' if Prefs['onlyKids'] else '0'

    oc = ObjectContainer(title2=R('MENU_SEARCH'))
    
    url = PLUGIN_API_URL + 'search/videos?query=' + query + '&isKids=' + isKids
    regular = JSON.ObjectFromURL(url)
    CreateSectionObject(section=regular, container=oc)

    return oc
