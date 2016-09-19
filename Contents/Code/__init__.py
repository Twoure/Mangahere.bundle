####################################################################################################
#                                                                                                  #
#                                       MangaHere Plex Channel                                     #
#                                                                                                  #
####################################################################################################
from pluginupdateservice import PluginUpdateService
from DumbTools import DumbKeyboard, DumbPrefs

# setup globals
PREFIX                      = '/photos/Mangahere'
TITLE                       = 'Mangahere'
GIT_REPO                    = 'Twoure/{}.bundle'.format(TITLE)
LIST_VIEW_CLIENTS           = ['Android', 'iOS']
BASE_URL                    = 'http://www.mangahere.co'
SEARCH_URL                  = BASE_URL + u'/search.php?name_method=cw&name={0}&author_method=cw&artist_method=cw&released_method=eq&advopts=1'

# setup thumb/art globals
ART                         = 'art-default_{0}.png'.format(Util.RandomInt(1, 3))
ICON                        = 'icon-default.png'
SEARCH_ICON                 = 'icon-search.png'
PREFS_ICON                  = 'icon-prefs.png'

PREFS_DICT = {
    'A-Z': 'name.az', 'Z-A': 'name.za', 'Ratings: High-Low': 'rating.za',
    'Ratings: Low-High': 'ratings.az', 'Views: High-Low': 'views.za',
    'Views: Low-High': 'views.az', 'Latest Updated': 'last_chapter_time.za'
    }

Updater = PluginUpdateService()

####################################################################################################
def Start():
    Plugin.AddViewGroup('ImageStream', viewMode='Pictures', mediaType='items')
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = TITLE
    ObjectContainer.view_group = 'InfoList'
    DirectoryObject.thumb = R(ICON)

    #HTTP.CacheTime = CACHE_1HOUR
    HTTP.CacheTime = CACHE_1MINUTE
    version = get_channel_version()

    Log.Debug('*' * 80)
    Log.Debug('* Platform.OS            = {0}'.format(Platform.OS))
    Log.Debug('* Platform.OSVersion     = {0}'.format(Platform.OSVersion))
    Log.Debug('* Platform.CPU           = {0}'.format(Platform.CPU))
    Log.Debug('* Platform.ServerVersion = {0}'.format(Platform.ServerVersion))
    Log.Debug('* Channel.Version        = {0}'.format(version))
    Log.Debug('*' * 80)

    if Dict['current_ch_version'] and (ParseVersion(Dict['current_ch_version']) < ParseVersion(version)):
        Log(u"* Channel updated from {0} to {1}".format(Dict['current_ch_version'], version))

    # setup current channel version
    Dict['current_ch_version'] = version

####################################################################################################
@handler(PREFIX, TITLE, ICON, ART)
def MainMenu():

    Log.Debug('*' * 80)
    Log.Debug('* Client.Product         = {0}'.format(Client.Product))
    Log.Debug('* Client.Platform        = {0}'.format(Client.Platform))
    Log.Debug('* Client.Version         = {0}'.format(Client.Version))

    oc = ObjectContainer(view_group='List', no_cache=Client.Product in ['Plex Web'])

    cp_match = Client.Platform in LIST_VIEW_CLIENTS
    # set thumbs based on client
    if cp_match:
        prefs_thumb = None
        search_thumb = None
    else:
        prefs_thumb = R(PREFS_ICON)
        search_thumb = R(SEARCH_ICON)

    # setup updater
    Updater.gui_update(
        PREFIX + '/updater', oc, GIT_REPO,
        tag='latest', list_view_clients=LIST_VIEW_CLIENTS
        )

    oc.add(DirectoryObject(key=Callback(AlphabetList), title='Alphabets'))
    oc.add(DirectoryObject(key=Callback(GenreList), title='Genres'))

    # setup prefs object
    if Client.Product in DumbPrefs.clients:
        DumbPrefs(PREFIX, oc, title='Preferences', thumb=prefs_thumb)
    else:
        oc.add(PrefsObject(title='Preferences', thumb=prefs_thumb))

    # setup search object
    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=search_thumb)
    else:
        oc.add(InputDirectoryObject(
            key=Callback(Search), title='Search Manga', prompt='Search Manga', thumb=search_thumb
            ))

    return oc

####################################################################################################
def ParseVersion(version):
    try:
        return tuple(map(int, (version.split('.'))))
    except:
        return version

####################################################################################################
def get_channel_version():
    plist = Plist.ObjectFromString(Core.storage.load(Core.plist_path))
    return plist['CFBundleVersion'] if 'CFBundleVersion' in plist.keys() else 'Current'

####################################################################################################
@route(PREFIX + '/alphabets')
def AlphabetList():
    """Generate #, ABC list"""

    oc = ObjectContainer(title2='Manga By #, A-Z', view_group='List')

    for pname in list('#'+String.UPPERCASE):
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, page=1, pname=pname.lower() if not '#' else '9', ntitle=pname),
            title=pname
            ))

    Log('Built ABC... Directory')

    return oc

####################################################################################################
@route(PREFIX + '/genres')
def GenreList():
    """Generate Genre List"""

    url = BASE_URL + '/directory/'
    html = HTML.ElementFromURL(url)

    oc = ObjectContainer(title2='Manga By Genres', view_group='List')

    for node in html.xpath('//ul[@class="by_categories clearfix"]/li/a'):
        title = node.get('href') + node.text
        pname = title.rsplit('/', 2)[1]
        new_title = title.rsplit('/', 2)[2]
        #Log(u'Genre path_name:title_name = {0}:{1}'.format(pname, new_title))

        oc.add(DirectoryObject(
            key=Callback(DirectoryList, page=1, pname=pname, ntitle=new_title),
            title=new_title
            ))

    return oc

####################################################################################################
@route(PREFIX + '/directory/{pname}')
def DirectoryList(page, pname, ntitle):
    """Get list of Mangas"""

    url = BASE_URL + '/{0}/{1}.htm?{2}'.format(pname, page, PREFS_DICT[Prefs['sort_opt']])
    #Log(u"Current sort options = '{0}': '{1}'".format(Prefs['sort_opt'], PREFS_DICT[Prefs['sort_opt']]))

    html = HTML.ElementFromURL(url)

    pages = html.xpath('//div[@class="next-page"]//a[@href]')
    total_pages = pages[int(len(pages))-2].text
    #Log(total_pages)

    main_title = u'{0}: Page {1} of {2}'.format(ntitle, page, total_pages)

    oc = ObjectContainer(title2=main_title, view_group='List')

    for node in html.xpath('//div[@class="directory_list"]/ul/li'):
        thumb = node.xpath('.//img')[0].get('src')
        node2 = node.xpath('.//div[@class="title"]/a')[0]
        title = node2.text
        url = node2.get('href')
        if url[-1] == '/':
            url = url[:-1]

        manga = url.rsplit('/', 2)[-1]

        oc.add(DirectoryObject(
            key=Callback(MangaPage, manga=manga, title=title),
            title=title,
            thumb=thumb
            ))

    nextpg_node = html.xpath('//div[@class="next-page"]//a[@class="next"]')
    if nextpg_node:
        nextpg = int(nextpg_node[0].get('href').split('.')[0])
        Log.Debug('NextPage = {0}'.format(nextpg))

        oc.add(NextPageObject(
            key=Callback(DirectoryList, page=nextpg, pname=pname, ntitle=ntitle),
            title='Next Page>>'
            ))

    return oc

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    """Search for Manga"""

    query = query.strip()
    url = SEARCH_URL.format(String.Quote(query, usePlus=True))

    html = HTML.ElementFromURL(url)

    oc = ObjectContainer(view_group='List')

    for node in html.xpath('//div[@class="result_search"]//dt'):
        url = node.xpath('./a')[0].get('href')
        title = node.xpath('./a')[0].text
        if url[-1] == '/':
            url = url[:-1]

        manga = url.rsplit('/', 2)[-1]

        oc.add(DirectoryObject(key=Callback(MangaPage, manga=manga, title=title), title=title))

    return oc

####################################################################################################
@route(PREFIX + '/manga/{manga}')
def MangaPage(manga, title):
    oc = ObjectContainer(title2=title, view_group='List')

    url = BASE_URL + '/manga/' + manga + '/'

    html = HTML.ElementFromURL(url, timeout=10.0)

    fallback = 'http://www.mangahere.co/media/images/nopicture.jpg'
    ht = html.xpath('//meta[@property="og:image"]/@content')
    rt = Regex(r'(https?\:\/\/[^\/]+\/.+?manga\/\d+\/)').search(ht[0]) if ht else None
    thumb = rt.group(1) + 'cover.jpg' if rt else fallback

    for node in html.xpath('//div[@class="detail_list"]//li//a'):
        url = node.get('href') + '1.html'
        chap_title = (node.text).replace(title, '').strip()
        oc.add(PhotoAlbumObject(
            url=url, title=chap_title,
            thumb=Resource.ContentsOfURLWithFallback([thumb, fallback]),
            ))

    return oc
