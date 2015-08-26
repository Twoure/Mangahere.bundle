PLUGIN_PREFIX = "/photos/Mangahere"
PLUGIN_TITLE = "Mangahere Reader"
ROOT_URL = "http://www.mangahere.co"
#RE_PAGES = Regex("total_pages = (\d+)")
#RE_IMAGE_URL = Regex("<img src=\"([^']*)\?")

#MANGAHERE_QUERY = ROOT_URL+"/search.php?name=%s&advopts=1"

ART = "art-default.png"
ICON = "icon-default.png"

#GENRES = [
#    'Action', 'Adult', 'Adventure', 'Comedy', 'Doujinshi',
#    'Drama', 'Ecchi', 'Fantasy', 'Gender Bender', 'Harem',
#    'Historical', 'Horror', 'Josei', 'Martial Arts', 'Mature',
#    'Mecha', 'Mystery', 'One Shot', 'Psychological', 'Romance',
#    'School Life', 'Sci-fi', 'Seinen', 'Shoujo', 'Shoujo Ai',
#    'Shounen', 'Shounen Ai', 'Slice of Life', 'Smut', 'Sports',
#    'Supernatural', 'Tragedy', 'Webtoons', 'Yaoi', 'Yuri',
#    ]
#
####################################################################################################

def Start():
    Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, PLUGIN_TITLE, ICON, ART)
    Plugin.AddViewGroup("ImageStream", viewMode="Pictures", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = PLUGIN_TITLE
    ObjectContainer.view_group = "InfoList"
    DirectoryObject.thumb = R(ICON)

#    HTTP.CacheTime = CACHE_1DAY
    HTTP.CacheTime = CACHE_10MINUTES

####################################################################################################

#@handler(PLUGIN_PREFIX, PLUGIN_TITLE)
def MainMenu():
    oc = ObjectContainer(view_group="InfoList")
    oc.add(DirectoryObject(key=Callback(AlphabetList), title="Alphabets"))
#    oc.add(DirectoryObject(key=Callback(GenreList), title="Genres"))
#    oc.add(InputDirectoryObject(key=Callback(Search), title='Search Manga', prompt='Search Manga'))
    return oc

####################################################################################################

@route(PLUGIN_PREFIX + '/alphabets')
def AlphabetList():
    oc = ObjectContainer(view_group="List")
    oc.add(DirectoryObject(key=Callback(DirectoryList, page=1, pname='9'), title='#'))
    for pname in map(chr, range(ord('A'), ord('Z')+1)):
        Log(pname)
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, page=1, pname=pname.lower()),
            title=pname
            ))
    return oc

####################################################################################################
#
#@route(PLUGIN_PREFIX + '/genres')
#def GenreList():
#    oc = ObjectContainer(view_group="List")
#    for title in GENRES:
#        pname = title.lower().replace(' ', '-')
#        oc.add(DirectoryObject(key=Callback(DirectoryList, page=1, pname=pname), title=title))
#    return oc
#
####################################################################################################

@route(PLUGIN_PREFIX + '/directory/{pname}')
def DirectoryList(page, pname):
    Log(page)
    Log(pname)
    oc = ObjectContainer(view_group="List")
    url = ROOT_URL+"/%s/%s.htm?name.az" %(pname, page)
    Log(url)
#    try:
#    http = HTTP.Request(url).content
#    html = HTML.ElementFromString(http)
    html = HTML.ElementFromURL(url)
    Log(html)
#    except:
#        Log("no media available")
#        raise Ex.MediaNotAvailable

    for node in html.xpath('//div[@class="directory_list"]/ul/li'):
        Log("node = %s" % node)
        thumb = node.xpath('.//img')[0].get('src')
        Log("thumb = %s" % thumb)
        node2 = node.xpath('.//div[@class="title"]/a')[0]
        Log("node2 = %s" % node2)
        url = node2.get('href')
        Log("url pass one = %s" % url)
        if url[-1] == '/':
            url = url[:-1]
        Log("url pass 2 = %s" % url)
        manga = url.rsplit('/', 2)[-1]
        Log("manga name = %s" % manga)
        oc.add(DirectoryObject(
            key=Callback(MangaPage, manga=manga),
            title=node2.text,
            thumb=thumb
            ))

    nextpg_node = html.xpath('//div[@class="next-page"]//a[@class="next"]')
    if nextpg_node:
        nextpg = int(nextpg_node[0].get('href').split('.')[0])
        Log.Debug("NextPage = %d" % nextpg)
        oc.add(NextPageObject(
            key=Callback(DirectoryList, page=nextpg, pname=pname),
            title="Next Page>>"
            ))

    return oc
#    return ObjectContainer(
#        header=PLUGIN_TITLE,
#        message='No Manga to Show yet :('
#        )


####################################################################################################
#
#@route(PLUGIN_PREFIX + '/search')
#def Search(query=''):
#    Log.Debug("Search "+query)
#    url = MANGAHERE_QUERY % String.Quote(query, usePlus=False)
#    try:
#        html = HTML.ElementFromURL(url)
#    except:
#        raise Ex.MediaExpired
#    oc = ObjectContainer(view_group="List")
#    for node in html.xpath("//table[@id='listing']//a[contains(@class, 'manga_open')]"):
#        url = node.get('href')
#        if url[-1] == '/':
#            url = url[:-1]
#        manga = url.rsplit('/', 2)[-1]
#        oc.add(DirectoryObject(key=Callback(MangaPage, manga=manga), title=node.text))
#    return oc
#
####################################################################################################

@route(PLUGIN_PREFIX + '/manga/{manga}')
def MangaPage(manga):
    oc = ObjectContainer(title2=manga, view_group="List")
    url = ROOT_URL + '/manga/' + manga + '/'
#    try:
    html = HTML.ElementFromURL(url, timeout=10.0)
#    except:
#        raise Ex.MediaNotAvailable
    for node in html.xpath('//div[@class="detail_list"]//li//a'):
        url = node.get('href') + '1.html'
        oc.add(PhotoAlbumObject(url=url, title=node.text, thumb=None))
    return oc
####################################################################################################
#
#@route(PLUGIN_PREFIX + '/manga/{manga}/chapter')
#def PhotoAlbum(url):
#    oc = ObjectContainer()
#
#    raw = HTTP.Request(url).content
#    pages = int(RE_PAGES.search(raw).group(1))
#    token = url.rsplit('/', 1)
#    for page in range(1, pages + 1):
#        page_url = token[0] + '/%d.html' % page
#        raw = HTTP.Request(page_url).content
#        img_url = RE_IMAGE_URL.search(raw).group(1)
#        oc.add(PhotoObject(
#            url=img_url,
#            title=str(page),
#            thumb=none
#            ))
#
#    return oc
#
