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
BASE_URL                    = 'http://www.mangahere.co'
SEARCH_URL                  = BASE_URL + u'/search.php?name_method=cw&name={0}&author_method=cw&artist_method=cw&released_method=eq&advopts=1'

# setup thumb/art globals
ART                         = 'art-default.jpg'
ICON                        = 'icon-default.png'
ABC_ICON                    = 'icon-abc.png'
GENRES_ICON                 = 'icon-genres.png'
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
    DirectoryObject.art = R(ART)
    InputDirectoryObject.art = R(ART)

    #HTTP.CacheTime = CACHE_1HOUR
    HTTP.CacheTime = CACHE_1MINUTE
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.113 Safari/537.36'
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

    """
    # setup updater
    Updater.gui_update(PREFIX + '/updater', oc, GIT_REPO, tag='latest')
    """

    oc.add(DirectoryObject(key=Callback(AlphabetList), title='Alphabets', thumb=R(ABC_ICON)))
    oc.add(DirectoryObject(key=Callback(GenreList), title='Genres', thumb=R(GENRES_ICON)))

    # setup prefs object
    if Client.Product in DumbPrefs.clients:
        DumbPrefs(PREFIX, oc, title='Preferences', thumb=R(PREFS_ICON))
    else:
        oc.add(PrefsObject(title='Preferences', thumb=R(PREFS_ICON)))

    # setup search object
    if Client.Product in DumbKeyboard.clients:
        DumbKeyboard(PREFIX, oc, Search, dktitle='Search', dkthumb=R(SEARCH_ICON))
    else:
        oc.add(InputDirectoryObject(
            key=Callback(Search), title='Search Manga',
            prompt='Search Manga', thumb=R(SEARCH_ICON)
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

    return oc

####################################################################################################
@route(PREFIX + '/genres')
def GenreList():
    """Generate Genre List"""

    html = HTML.ElementFromURL(BASE_URL + '/directory/')

    oc = ObjectContainer(title2='Manga By Genres', view_group='List')

    for node in html.xpath('//ul[@class="by_categories clearfix"]/li/a'):
        title = node.get('href') + node.text
        pname = title.rsplit('/', 2)[1]
        new_title = title.rsplit('/', 2)[2]

        oc.add(DirectoryObject(
            key=Callback(DirectoryList, page=1, pname=pname, ntitle=new_title),
            title=new_title
            ))

    return oc

####################################################################################################
@route(PREFIX + '/directory/{pname}', page=int)
def DirectoryList(page, pname, ntitle):
    """Get list of Mangas"""

    html = HTML.ElementFromURL(BASE_URL + '/{0}/{1}.htm?{2}'.format(pname, page, PREFS_DICT[Prefs['sort_opt']]))

    pages = html.xpath('//div[@class="next-page"]//a[@href]')
    total_pages = pages[int(len(pages))-2].text

    oc = ObjectContainer(title2=ntitle, view_group='List')

    for node in html.xpath('//div[@class="directory_list"]/ul/li'):
        node2 = node.xpath('.//div[@class="title"]/a')[0]
        title = node2.get('title').strip()
        if ';' in title:
            title = String.DecodeHTMLEntities(title)
        url = node2.get('href')
        oc.add(DirectoryObject(
            key=Callback(MangaPage, manga=manga_from_url(url), title=title),
            title=title, thumb=node.xpath('.//img')[0].get('src')
            ))

    nextpg_node = html.xpath('//div[@class="next-page"]//a[@class="next"]')
    if nextpg_node:
        nextpg = int(nextpg_node[0].get('href').split('.')[0])
        oc.add(NextPageObject(
            key=Callback(DirectoryList, page=nextpg, pname=pname, ntitle=ntitle),
            title='Next {0} of {1} >>'.format(nextpg, total_pages)
            ))

    return oc

####################################################################################################
@route(PREFIX + '/search')
def Search(query=''):
    """Search for Manga"""

    query = query.strip()
    html = HTML.ElementFromURL(SEARCH_URL.format(String.Quote(query, usePlus=True)))

    oc = ObjectContainer(view_group='List')

    for node in html.xpath('//div[@class="result_search"]//dt'):
        url = node.xpath('./a')[0].get('href')
        title = node.xpath('./a')[0].text
        oc.add(DirectoryObject(
            key=Callback(MangaPage, manga=manga_from_url(url), title=title),
            title=title
            ))

    return oc

####################################################################################################
@route(PREFIX + '/manga/{manga}')
def MangaPage(manga, title):
    oc = ObjectContainer(title2=title, view_group='List')

    html = HTML.ElementFromURL(BASE_URL + '/manga/' + manga + '/', timeout=10.0)

    fallback = 'http://www.mangahere.co/media/images/nopicture.jpg'
    ht = html.xpath('//meta[@property="og:image"]/@content')
    rt = Regex(r'(https?\:\/\/[^\/]+\/.+?manga\/\d+\/)').search(ht[0]) if ht else None
    thumb = rt.group(1) + 'cover.jpg' if rt else fallback

    for node in html.xpath('//div[@class="detail_list"]/ul/li'):
        href = node.xpath('.//a/@href')
        if not href:
            continue

        date = node.xpath('.//span[@class="right"]/text()')
        tagline = node.xpath('.//span/span/text()')
        chap_title = str(float(href[0].rsplit('/', 2)[1].split('c')[1]))
        url = href[0] + '1.html'

        oc.add(PhotoAlbumObject(
            key=Callback(GetPhotoAlbum, url=url, title=chap_title),
            rating_key=url,
            title=chap_title,
            source_title='MangaHere',
            tagline=tagline[0].strip() if tagline else None,
            originally_available_at=Datetime.ParseDate(date[0]) if date else None,
            thumb=Resource.ContentsOfURLWithFallback([thumb, fallback]),
            art=R(ART),
            ))

    return oc

####################################################################################################
@route(PREFIX + '/get/photoablum')
def GetPhotoAlbum(url, title):
    oc = ObjectContainer(title2=title)

    html = HTML.ElementFromURL(url)

    node = html.xpath('//select[@class="wid60"]')[0]
    page_list = node.xpath('./option[@value]')
    for item in page_list:
        oc.add(CreatePhotoObject(
            title=item.text.strip(),
            url=Callback(GetPhoto, url=item.get('value')),
            ))

    return oc

####################################################################################################
@route(PREFIX + '/create/photo-object', include_container=bool)
def CreatePhotoObject(title, url, include_container=False, *args, **kwargs):
    photo_object = PhotoObject(
        key=Callback(CreatePhotoObject, title=title, url=url, include_container=True),
        rating_key=url,
        source_title='MangaHere',
        title=title,
        thumb=url,
        art=R(ART),
        items=[MediaObject(parts=[PartObject(key=url)])]
        )

    if include_container:
        return ObjectContainer(objects=[photo_object])
    return photo_object

####################################################################################################
@route(PREFIX + '/get/photo')
def GetPhoto(url):
    return Redirect(HTML.ElementFromURL(url).xpath('//section[@id="viewer"]/a/img[@onload]/@src')[0])

####################################################################################################
def manga_from_url(url):
    url = url[:-1] if url.endswith('/') else url
    return url.rsplit('/', 2)[-1]
