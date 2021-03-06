import sys
import requests
from ..request import request
from ..request_class import Request
from ..habanero_utils import sub_str,check_kwargs
from .filters import filter_names, filter_details

class Crossref(object):
    '''
    Crossref: Class for Crossref search API methods

    Includes methods matching Crossref API routes:

    * /works - :func:`~habanero.Crossref.works`
    * /members - :func:`~habanero.Crossref.members`
    * /prefixes - :func:`~habanero.Crossref.prefixes`
    * /funders - :func:`~habanero.Crossref.funders`
    * /journals - :func:`~habanero.Crossref.journals`
    * /types - :func:`~habanero.Crossref.types`
    * /licenses - :func:`~habanero.Crossref.licenses`

    Also:

    * registration_agency - :func:`~habanero.Crossref.registration_agency`
    * random_dois - :func:`~habanero.Crossref.random_dois`

    What am I actually searching when using the Crossref search API?:

    You are using the Crossref search API described at
    https://github.com/CrossRef/rest-api-doc/blob/master/rest_api.md.
    When you search with query terms, on Crossref servers they are not
    searching full text, or even abstracts of articles, but only what is
    available in the data that is returned to you. That is, they search
    article titles, authors, etc. For some discussion on this, see
    https://github.com/CrossRef/rest-api-doc/issues/101

    Doing setup::

        from habanero import Crossref
        cr = Crossref()
        # set a different base url
        Crossref(base_url = "http://some.other.url")
        # set an api key
        Crossref(api_key = "123456")

    '''
    def __init__(self, base_url = "http://api.crossref.org", api_key = None):

        self.base_url = base_url
        self.api_key = api_key

    def __repr__(self):
      return """< %s \nURL: %s\nKEY: %s\n>""" % (type(self).__name__,
        self.base_url, sub_str(self.api_key))

    def works(self, ids = None, query = None, filter = None, offset = None,
              limit = None, sample = None, sort = None,
              order = None, facet = None, cursor = None,
              cursor_max = 5000, **kwargs):
        '''
        Search Crossref works

        :param ids: [Array] DOIs (digital object identifier) or other identifiers
        :param query: [String] A query string
        :param filter: [Hash] Filter options. See ...
        :param offset: [Fixnum] Number of record to start at, from 1 to infinity.
        :param limit: [Fixnum] Number of results to return. Not relavant when searching with specific dois. Default: 20. Max: 1000
        :param sample: [Fixnum] Number of random results to return. when you use the sample parameter,
            the limit and offset parameters are ignored.
        :param sort: [String] Field to sort on, one of score, relevance,
            updated (date of most recent change to metadata. Currently the same as deposited),
            deposited (time of most recent deposit), indexed (time of most recent index), or
            published (publication date). Note: If the API call includes a query, then the sort
            order will be by the relevance score. If no query is included, then the sort order
            will be by DOI update date.
        :param order: [String] Sort order, one of 'asc' or 'desc'
        :param facet: [Boolean] Include facet results. Default: false
        :param cursor: [String] Cursor character string to do deep paging. Default is None.
            Pass in '*' to start deep paging. Any combination of query, filters and facets may be
            used with deep paging cursors. While rows may be specified along with cursor, offset
            and sample cannot be used.
            See https://github.com/CrossRef/rest-api-doc/blob/master/rest_api.md#deep-paging-with-cursors
        :param cursor_max: [Fixnum] Max records to retrieve. Only used when cursor param used. Because
            deep paging can result in continuous requests until all are retrieved, use this
            parameter to set a maximum number of records. Of course, if there are less records
            found than this value, you will get only those found.
        :param kwargs: any additional arguments will be passed on to
            `requests.get`

        :return: A dict

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.works()
            cr.works(ids = '10.1371/journal.pone.0033693')
            dois = ['10.1371/journal.pone.0033693', ]
            cr.works(ids = dois)
            x = cr.works(query = "ecology")
            x['status']
            x['message-type']
            x['message-version']
            x['message']
            x['message']['total-results']
            x['message']['items-per-page']
            x['message']['query']
            x['message']['items']

            # Get full text links
            x = cr.works(filter = {'has_full_text': True})
            x

            # Parse output to various data pieces
            x = cr.works(filter = {'has_full_text': True})
            ## get doi for each item
            [ z['DOI'] for z in x['message']['items'] ]
            ## get doi and url for each item
            [ {"doi": z['DOI'], "url": z['URL']} for z in x['message']['items'] ]
            ### print every doi
            for i in x['message']['items']:
                 print i['DOI']

            # filters - pass in as a dict
            ## see https://github.com/CrossRef/rest-api-doc/blob/master/rest_api.md#filter-names
            cr.works(filter = {'has_full_text': True})
            cr.works(filter = {'has_funder': True, 'has_full_text': True})
            cr.works(filter = {'award_number': 'CBET-0756451', 'award_funder': '10.13039/100000001'})

            # Deep paging, using the cursor parameter
            ## this search should lead to only ~215 results
            cr.works(query = "widget", cursor = "*", cursor_max = 100)
            ## this search should lead to only ~2500 results, in chunks of 500
            res = cr.works(query = "octopus", cursor = "*", limit = 500)
            sum([ len(z['message']['items']) for z in res ])
            ## about 167 results
            res = cr.works(query = "extravagant", cursor = "*", limit = 50, cursor_max = 500)
            sum([ len(z['message']['items']) for z in res ])
            ## cursor_max to get back only a maximum set of results
            res = cr.works(query = "widget", cursor = "*", cursor_max = 100)
            sum([ len(z['message']['items']) for z in res ])
            ## cursor_max - especially useful when a request could be very large
            ### e.g., "ecology" results in ~275K records, lets max at 10,000
            ###   with 1000 at a time
            res = cr.works(query = "ecology", cursor = "*", cursor_max = 10000, limit = 1000)
            sum([ len(z['message']['items']) for z in res ])
            items = [ z['message']['items'] for z in res ]
            items = [ item for sublist in items for item in sublist ]
            [ z['DOI'] for z in items ][0:50]

            # field queries
            res = cr.works(query = "ecology", query_author = 'carl boettiger')
            [ x['author'][0]['family'] for x in res['message']['items'] ]
        '''
        if ids.__class__.__name__ != 'NoneType':
            return request(self.base_url, "/works/", ids,
                query, filter, offset, limit, sample, sort,
                order, facet, None, None, None, **kwargs)
        else:
            return Request(self.base_url, "/works/",
              query, filter, offset, limit, sample, sort,
              order, facet, cursor, cursor_max, **kwargs).do_request()

    def members(self, ids = None, query = None, filter = None, offset = None,
              limit = None, sample = None, sort = None,
              order = None, facet = None, works = False,
              cursor = None, cursor_max = 5000, **kwargs):
        '''
        Search Crossref members

        :param ids: [Array] DOIs (digital object identifier) or other identifiers
        :param query: [String] A query string
        :param filter: [Hash] Filter options. See ...
        :param offset: [Fixnum] Number of record to start at, from 1 to infinity.
        :param limit: [Fixnum] Number of results to return. Not relavant when searching with specific dois. Default: 20. Max: 1000
        :param sample: [Fixnum] Number of random results to return. when you use the sample parameter,
            the limit and offset parameters are ignored. This parameter only used when works requested.
        :param sort: [String] Field to sort on, one of score, relevance,
            updated (date of most recent change to metadata. Currently the same as deposited),
            deposited (time of most recent deposit), indexed (time of most recent index), or
            published (publication date). Note: If the API call includes a query, then the sort
            order will be by the relevance score. If no query is included, then the sort order
            will be by DOI update date.
        :param order: [String] Sort order, one of 'asc' or 'desc'
        :param facet: [Boolean] Include facet results. Default: false
        :param works: [Boolean] If true, works returned as well. Default: false
        :param kwargs: any additional arguments will be passed on to
            `requests.get`

        :return: A dict

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.members(ids = 98)

            # get works
            res = cr.members(ids = 98, works = True, limit = 3)
            len(res['message']['items'])
            [ z['DOI'] for z in res['message']['items'] ]

            # cursor - deep paging
            res = cr.members(ids = 98, works = True, cursor = "*")
            sum([ len(z['message']['items']) for z in res ])
            items = [ z['message']['items'] for z in res ]
            items = [ item for sublist in items for item in sublist ]
            [ z['DOI'] for z in items ][0:50]

            # field queries
            res = cr.members(ids = 98, works = True, query_author = 'carl boettiger', limit = 7)
            [ x['author'][0]['family'] for x in res['message']['items'] ]
        '''
        return request(self.base_url, "/members/", ids,
            query, filter, offset, limit, sample, sort,
            order, facet, works, cursor, cursor_max, **kwargs)

    def prefixes(self, ids = None, filter = None, offset = None,
              limit = None, sample = None, sort = None,
              order = None, facet = None, works = False,
              cursor = None, cursor_max = 5000, **kwargs):
        '''
        Search Crossref prefixes

        :param ids: [Array] DOIs (digital object identifier) or other identifiers
        :param filter: [Hash] Filter options. See ...
        :param offset: [Fixnum] Number of record to start at, from 1 to infinity.
        :param limit: [Fixnum] Number of results to return. Not relavant when searching with specific dois. Default: 20. Max: 1000
        :param sample: [Fixnum] Number of random results to return. when you use the sample parameter,
            the limit and offset parameters are ignored. This parameter only used when works requested.
        :param sort: [String] Field to sort on, one of score, relevance,
            updated (date of most recent change to metadata. Currently the same as deposited),
            deposited (time of most recent deposit), indexed (time of most recent index), or
            published (publication date). Note: If the API call includes a query, then the sort
            order will be by the relevance score. If no query is included, then the sort order
            will be by DOI update date.
        :param order: [String] Sort order, one of 'asc' or 'desc'
        :param facet: [Boolean] Include facet results. Default: false
        :param works: [Boolean] If true, works returned as well. Default: false
        :param kwargs: any additional arguments will be passed on to
            `requests.get`

        :return: A dict

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.prefixes(ids = "10.1016")
            cr.prefixes(ids = ['10.1016','10.1371','10.1023','10.4176','10.1093'])

            # get works
            cr.prefixes(ids = "10.1016", works = True)

            # Limit number of results
            cr.prefixes(ids = "10.1016", works = True, limit = 3)

            # Sort and order
            cr.prefixes(ids = "10.1016", works = True, sort = "relevance", order = "asc")

            # cursor - deep paging
            res = cr.prefixes(ids = "10.1016", works = True, cursor = "*", limit = 200)
            sum([ len(z['message']['items']) for z in res ])
            items = [ z['message']['items'] for z in res ]
            items = [ item for sublist in items for item in sublist ]
            [ z['DOI'] for z in items ][0:50]

            # field queries
            res = cr.prefixes(ids = "10.1371", works = True, query_editor = 'cooper', filter = {'type': 'journal-article'})
            eds = [ x.get('editor') for x in res['message']['items'] ]
            [ z for z in eds if z is not None ]
        '''
        check_kwargs(["query"], kwargs)
        return request(self.base_url, "/prefixes/", ids,
          query = None, filter = filter, offset = offset, limit = limit,
          sample = sample, sort = sort, order = order, facet = facet, works = works,
          cursor = cursor, cursor_max = cursor_max, **kwargs)

    def funders(self, ids = None, query = None, filter = None, offset = None,
              limit = None, sample = None, sort = None,
              order = None, facet = None, works = False,
              cursor = None, cursor_max = 5000, **kwargs):
        '''
        Search Crossref funders

        Note that funders without IDs don't show up on the `/funders` route,
        that is, won't show up in searches via this method

        :param ids: [Array] DOIs (digital object identifier) or other identifiers
        :param query: [String] A query string
        :param filter: [Hash] Filter options. See ...
        :param offset: [Fixnum] Number of record to start at, from 1 to infinity.
        :param limit: [Fixnum] Number of results to return. Not relavant when searching with specific dois. Default: 20. Max: 1000
        :param sample: [Fixnum] Number of random results to return. when you use the sample parameter,
            the limit and offset parameters are ignored. This parameter only used when works requested.
        :param sort: [String] Field to sort on, one of score, relevance,
            updated (date of most recent change to metadata. Currently the same as deposited),
            deposited (time of most recent deposit), indexed (time of most recent index), or
            published (publication date). Note: If the API call includes a query, then the sort
            order will be by the relevance score. If no query is included, then the sort order
            will be by DOI update date.
        :param order: [String] Sort order, one of 'asc' or 'desc'
        :param facet: [Boolean] Include facet results. Default: false
        :param works: [Boolean] If true, works returned as well. Default: false
        :param kwargs: any additional arguments will be passed on to
            `requests.get`

        :return: A dict

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.funders(ids = '10.13039/100000001')
            cr.funders(query = "NSF")

            # get works
            cr.funders(ids = '10.13039/100000001', works = True)

            # cursor - deep paging
            res = cr.funders(ids = '10.13039/100000001', works = True, cursor = "*", limit = 200)
            sum([ len(z['message']['items']) for z in res ])
            items = [ z['message']['items'] for z in res ]
            items = [ item for sublist in items for item in sublist ]
            [ z['DOI'] for z in items ][0:50]

            # field queries
            res = cr.funders(ids = "10.13039/100000001", works = True, query_container_title = 'engineering', filter = {'type': 'journal-article'})
            eds = [ x.get('editor') for x in res['message']['items'] ]
            [ z for z in eds if z is not None ]
        '''
        return request(self.base_url, "/funders/", ids,
          query, filter, offset, limit, sample, sort,
          order, facet, works, cursor, cursor_max, **kwargs)

    def journals(self, ids = None, query = None, filter = None, offset = None,
              limit = None, sample = None, sort = None,
              order = None, facet = None, works = False,
              cursor = None, cursor_max = 5000, **kwargs):
        '''
        Search Crossref journals

        :param ids: [Array] DOIs (digital object identifier) or other identifiers
        :param query: [String] A query string
        :param filter: [Hash] Filter options. See ...
        :param offset: [Fixnum] Number of record to start at, from 1 to infinity.
        :param limit: [Fixnum] Number of results to return. Not relavant when searching with specific dois. Default: 20. Max: 1000
        :param sample: [Fixnum] Number of random results to return. when you use the sample parameter,
            the limit and offset parameters are ignored. This parameter only used when works requested.
        :param sort: [String] Field to sort on, one of score, relevance,
            updated (date of most recent change to metadata. Currently the same as deposited),
            deposited (time of most recent deposit), indexed (time of most recent index), or
            published (publication date). Note: If the API call includes a query, then the sort
            order will be by the relevance score. If no query is included, then the sort order
            will be by DOI update date.
        :param order: [String] Sort order, one of 'asc' or 'desc'
        :param facet: [Boolean] Include facet results. Default: false
        :param works: [Boolean] If true, works returned as well. Default: false
        :param kwargs: any additional arguments will be passed on to
            `requests.get`

        :return: A dict

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.journals(ids = "2167-8359")
            cr.journals()

            # pass many ids
            cr.journals(ids = ['1803-2427', '2326-4225'])

            # search
            cr.journals(query = "ecology")
            cr.journals(query = "peerj")

            # get works
            cr.journals(ids = "2167-8359", works = True)
            cr.journals(ids = "2167-8359", query = 'ecology', works = True, sort = 'score', order = "asc")
            cr.journals(ids = "2167-8359", query = 'ecology', works = True, sort = 'score', order = "desc")
            cr.journals(ids = "2167-8359", works = True, filter = {'from_pub_date': '2014-03-03'})
            cr.journals(ids = '1803-2427', works = True)
            cr.journals(ids = '1803-2427', works = True, sample = 1)
            cr.journals(limit: 2)

            # cursor - deep paging
            res = cr.funders(ids = '10.13039/100000001', works = True, cursor = "*", limit = 200)
            sum([ len(z['message']['items']) for z in res ])
            items = [ z['message']['items'] for z in res ]
            items = [ item for sublist in items for item in sublist ]
            [ z['DOI'] for z in items ][0:50]

            # field queries
            res = cr.journals(ids = "2167-8359", works = True, query_title = 'fish', filter = {'type': 'journal-article'})
            [ x.get('title') for x in res['message']['items'] ]
        '''
        return request(self.base_url, "/journals/", ids,
          query, filter, offset, limit, sample, sort,
          order, facet, works, cursor, cursor_max, **kwargs)

    def types(self, ids = None, query = None, filter = None, offset = None,
              limit = None, sample = None, sort = None,
              order = None, facet = None, works = False,
              cursor = None, cursor_max = 5000, **kwargs):
        '''
        Search Crossref types

        :param ids: [Array] Type identifier, e.g., journal
        :param query: [String] A query string
        :param filter: [Hash] Filter options. See ...
        :param offset: [Fixnum] Number of record to start at, from 1 to infinity.
        :param limit: [Fixnum] Number of results to return. Not relavant when searching with specific dois. Default: 20. Max: 1000
        :param sample: [Fixnum] Number of random results to return. when you use the sample parameter,
            the limit and offset parameters are ignored. This parameter only used when works requested.
        :param sort: [String] Field to sort on, one of score, relevance,
            updated (date of most recent change to metadata. Currently the same as deposited),
            deposited (time of most recent deposit), indexed (time of most recent index), or
            published (publication date). Note: If the API call includes a query, then the sort
            order will be by the relevance score. If no query is included, then the sort order
            will be by DOI update date.
        :param order: [String] Sort order, one of 'asc' or 'desc'
        :param facet: [Boolean] Include facet results. Default: false
        :param works: [Boolean] If true, works returned as well. Default: false
        :param kwargs: any additional arguments will be passed on to
            `requests.get`

        :return: A dict

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.types()
            cr.types(ids = "journal")
            cr.types(ids = "journal-article")
            cr.types(ids = "journal", works = True)

            # field queries
            res = cr.types(ids = "journal-article", works = True, query_title = 'gender', rows = 100)
            [ x.get('title') for x in res['message']['items'] ]
        '''
        return request(self.base_url, "/types/", ids,
            query, filter, offset, limit, sample, sort,
            order, facet, works, cursor, cursor_max, **kwargs)

    def licenses(self, query = None, offset = None,
              limit = None, sample = None, sort = None,
              order = None, facet = None, **kwargs):
        '''
        Search Crossref licenses

        :param query: [String] A query string
        :param offset: [Fixnum] Number of record to start at, from 1 to infinity.
        :param limit: [Fixnum] Number of results to return. Not relavant when searching with specific dois. Default: 20. Max: 1000
        :param sort: [String] Field to sort on, one of score, relevance,
            updated (date of most recent change to metadata. Currently the same as deposited),
            deposited (time of most recent deposit), indexed (time of most recent index), or
            published (publication date). Note: If the API call includes a query, then the sort
            order will be by the relevance score. If no query is included, then the sort order
            will be by DOI update date.
        :param order: [String] Sort order, one of 'asc' or 'desc'
        :param facet: [Boolean] Include facet results. Default: false
        :param kwargs: any additional arguments will be passed on to
            `requests.get`

        :return: A dict

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.licenses()
            cr.licenses(query = "creative")
        '''
        check_kwargs(["ids", "filter", "works"], kwargs)
        res = request(self.base_url, "/licenses/", None,
            query, None, offset, limit, None, sort,
            order, facet, None, None, None, None, **kwargs)
        return res

    def registration_agency(self, ids, **kwargs):
        '''
        Determine registration agency for DOIs

        :param ids: [Array] DOIs (digital object identifier) or other identifiers
        :param kwargs: any additional arguments will be passed on to
            `requests.get`

        :return: list of DOI minting agencies

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.registration_agency('10.1371/journal.pone.0033693')
            cr.registration_agency(ids = ['10.1007/12080.1874-1746','10.1007/10452.1573-5125', '10.1111/(issn)1442-9993'])
        '''
        check_kwargs(["query", "filter", "offset", "limit", "sample", "sort",
            "order", "facet", "works"], kwargs)
        res = request(self.base_url, "/works/", ids,
            None, None, None, None, None, None,
            None, None, None, None, None, True, **kwargs)
        if res.__class__ != list:
            k = []
            k.append(res)
        else:
            k = res
        return [ z['message']['agency']['label'] for z in k ]

    def random_dois(self, sample = 10, **kwargs):
        '''
        Get a random set of DOIs

        :param sample: [Fixnum] Number of random DOIs to return. Default: 10
        :param kwargs: any additional arguments will be passed on to
            `requests.get`

        :return: [Array] of DOIs

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.random_dois(1)
            cr.random_dois(10)
            cr.random_dois(50)
            cr.random_dois(100)
        '''
        res = request(self.base_url, "/works/", None,
            None, None, None, None, sample, None,
            None, None, True, **kwargs)
        return [ z['DOI'] for z in res['message']['items'] ]

    @staticmethod
    def filter_names():
        '''
        Filter names - just the names of each filter

        Filters are used in the Crossref search API to modify searches

        :return: dict

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.filter_names()
        '''
        return filter_names

    @staticmethod
    def filter_details():
        '''
        Filter details - filter names, possible values, and description

        Filters are used in the Crossref search API to modify searches

        :return: dict

        Usage::

            from habanero import Crossref
            cr = Crossref()
            cr.filter_details()
            # Get descriptions for each filter
            x = cr.filter_details()
            [ z['description'] for z in x.values() ]
        '''
        return filter_details
