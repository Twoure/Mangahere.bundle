PLUGIN_PREFIX = '/photos/Mangahere'
PLUGIN_TITLE = 'Mangahere'
ROOT_URL = 'http://www.mangahere.co'

MANGAHERE_QUERY = ROOT_URL + '/search.php?name_method=cw&name=%s&author_method=cw&artist_method=cw&released_method=eq&advopts=1'

"""
USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/31.0.1650.63 Safari/537.36'
    )
"""

randomArt = Util.RandomInt(1, 3)
ART = 'art-default_' + str(randomArt) + '.png'
ICON = 'icon-default.png'

####################################################################################################
def Start():
    Plugin.AddViewGroup('ImageStream', viewMode='Pictures', mediaType='items')
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = PLUGIN_TITLE
    ObjectContainer.view_group = 'InfoList'
    DirectoryObject.thumb = R(ICON)

    HTTP.CacheTime = 0
    #HTTP.Headers['User-Agent'] = USER_AGENT

####################################################################################################
@handler(PLUGIN_PREFIX, PLUGIN_TITLE, ICON, ART)
def MainMenu():
    oc = ObjectContainer(view_group='List')

    oc.add(DirectoryObject(key=Callback(AlphabetList), title='Alphabets'))
    oc.add(DirectoryObject(key=Callback(GenreList), title='Genres'))
    oc.add(PrefsObject(title='Preferences'))
    oc.add(InputDirectoryObject(key=Callback(Search), title='Search Manga', prompt='Search Manga'))

    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/ValidatePrefs')
def ValidatePrefs():
    """Set the sort option for displaying Manga list"""

    if Prefs['sort_opt'] == 'A-Z':
        Dict['s_opt'] = 'name.az'
    elif Prefs['sort_opt'] == 'Z-A':
        Dict['s_opt'] = 'name.za'
    elif Prefs['sort_opt'] == 'Ratings: High-Low':
        Dict['s_opt'] = 'rating.za'
    elif Prefs['sort_opt'] == 'Ratings: Low-High':
        Dict['s_opt'] = 'ratings.az'
    elif Prefs['sort_opt'] == 'Views: High-Low':
        Dict['s_opt'] = 'views.za'
    elif Prefs['sort_opt'] == 'Views: Low-High':
        Dict['s_opt'] = 'views.az'
    elif Prefs['sort_opt'] == 'Latest Updated':
        Dict['s_opt'] = 'last_chapter_time.za'

    Dict.Save()

####################################################################################################
@route(PLUGIN_PREFIX + '/alphabets')
def AlphabetList():
    """Generate #, ABC list"""

    oc = ObjectContainer(title2='Manga By #, A-Z', view_group='List')

    for pname in ['#'] + map(chr, range(ord('A'), ord('Z')+1)):
        oc.add(DirectoryObject(
            key=Callback(DirectoryList, page=1, pname=pname.lower() if not '#' else '9', ntitle=pname),
            title=pname
            ))

    Log('Built ABC... Directory')

    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/genres')
def GenreList():
    """Generate Genre List"""

    url = ROOT_URL + '/directory/'  # set url for populating genres array
    html = HTML.ElementFromURL(url)  # formate url response into html so we can use xpath

    oc = ObjectContainer(title2='Manga By Genres', view_group='List')

    # For loop to pull out valid genres
    for node in html.xpath('//ul[@class="by_categories clearfix"]/li/a'):
        title = node.get('href') + node.text  # append results to empty array
        pname = title.rsplit('/', 2)[1]  # name used internally
        new_title = title.rsplit('/', 2)[2]  # name used for title2
        Log('Genre path_name:title_name = %s:%s' % (pname, new_title))

        oc.add(DirectoryObject(
            key=Callback(DirectoryList, page=1, pname=pname, ntitle=new_title),
            title=new_title
            ))

    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/directory/{pname}')
def DirectoryList(page, pname, ntitle):
    """Get list of Mangas"""

    url = ROOT_URL + '/%s/%s.htm?%s' %(pname, page, Dict['s_opt'])
    Log(Dict['s_opt'])

    html = HTML.ElementFromURL(url)

    pages = html.xpath('//div[@class="next-page"]//a[@href]')
    total_pages = pages[int(len(pages))-2].text
    Log(total_pages)

    main_title = '%s: Page %s of %s' % (str(ntitle), str(page), str(total_pages))

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
        Log.Debug('NextPage = %d' % nextpg)

        oc.add(NextPageObject(
            key=Callback(DirectoryList, page=nextpg, pname=pname, ntitle=ntitle),
            title='Next Page>>'
            ))

    return oc

####################################################################################################
@route(PLUGIN_PREFIX + '/search')
def Search(query=''):
    """Search for Manga"""

    Log.Debug('Search ' + query)
    url = MANGAHERE_QUERY % String.Quote(query, usePlus=True)

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
@route(PLUGIN_PREFIX + '/manga/{manga}')
def MangaPage(manga, title):
    oc = ObjectContainer(title2=title, view_group='List')

    url = ROOT_URL + '/manga/' + manga + '/'

    html = HTML.ElementFromURL(url, timeout=10.0)

    for node in html.xpath('//div[@class="detail_list"]//li//a'):
        url = node.get('href') + '1.html'
        ntitle = (node.text).replace(title, '').strip()
        oc.add(PhotoAlbumObject(url=url, title=ntitle))

    return oc
