#!/usr/bin/env python

import yaml
import os
import urllib
import changeme.core

http_schema = {
    'auth': {
        'type': 'dict',
        'required': True,
        'schema': {
            'credentials': {
                'type': 'list',
                'required': True,
                'schema': {
                    'type': 'dict',
                    'schema': {
                        'username': {
                            'type': ['string', 'integer'],
                            'nullable': True,
                            'required': True,
                        },
                        'password': {
                            'type': ['string', 'integer'],
                            'nullable': True,
                            'required': True,
                        },
                        'ref': {'type': 'string', 'required': False},
                        'raw': {'type': 'string', 'required': False},
                    }
                }
            },
            'headers': {
                'type': 'list',
                'required': False,
                'schema': {
                    'type': 'dict'
                }
            },
            'csrf': {
                'type': 'string',
                'nullable': True,
                'required': False,
            },
            'post': {
                'type': 'dict',
                'allow_unknown': True,
                'schema': {
                    'username': {'type': 'string', 'required': True},
                    'password': {'type': 'string', 'required': True},
                }
            },
            'get': {
                'type': 'dict',
                'allow_unknown': True,
                'schema': {
                    'username': {'type': 'string', 'required': True},
                    'password': {'type': 'string', 'required': True},
                }
            },
            'sessionid': {
                'type': 'string',
                'nullable': True,
                'required': False,
            },
            'base64': {
                'type': 'boolean',
                'nullable': False,
                'required': False,
            },
            'success': {
                'type': 'dict',
                'schema': {
                    'body': {
                        'type': 'list',
                        'required': False
                    },
                    'status': {'type': 'integer', 'required': True},
                },
            },
            'type': {
                'type': 'string',
                'regex': 'post|basic_auth|get|raw_post',
                'required': True
            },
            'url': {
                'type': 'list',
                'required': True,
                'schema': {'type': 'string'}
            },
        }
    },
    'category': {'type': 'string', 'required': True},
    'contributor': {'type': 'string', 'required': True},
    'fingerprint': {
        'type': 'dict',
        'required': True,
        'schema': {
            'body': {'type': 'list', 'required': False},
            'server_header': {'type': 'string', 'required': False},
            'cookie': {
                'type': 'list',
                'required': False,
                'schema': {
                    'type': 'dict'
                },
            },
            'headers': {
                'type': 'list',
                'required': False,
                'schema': {
                    'type': 'dict'
                }
            },
            'status': {'type': 'integer', 'required': True},
            'basic_auth_realm': {
                'type': 'string',
                'nullable': True,
                'required': False,
            },
            'url': {
                'type': 'list',
                'required': True,
                'schema': {'type': 'string'}
            },
        },
    },
    'default_port': {'type': 'integer', 'required': True},
    'name': {'type': 'string', 'required': True},
    'ssl': {'type': 'boolean', 'required': True},
    'references': {'type': 'list', 'required': False},
    'versions': {'type': 'list', 'required': False},
}


def mkcred():
    """
    TODO:
        - move credentials under auth
        - move auth url under auth
        - move success under auth
        - move auth url under auth
        - move type under auth
    """

    parameters = dict()
    auth_types = ['post', 'basic_auth', 'get', 'raw_post']

    def get_data(field, prompt, boolean=False, integer=False):
        result = raw_input(prompt).strip()
        if boolean and result.lower() == 'y':
            result = True
        elif boolean:
            result = False

        if integer:
            result = int(result)

        parameters[field] = result

    get_data('contributor', 'Your name or handle: ')
    get_data('name', 'Name of service (JBoss, Tomcat): ')
    get_data('protocol', 'Protocol of service (http, ssh, ftp): ')
    get_data('category', 'Category of service (general, printer, phone): ')
    get_data('default_port', 'Default port: ', integer=True)
    get_data('ssl', 'Does the service use ssl (y/n): ', boolean=True)

    # Fingerprint
    ###############################################################################
    fp = dict()

    # Fingerprint url is confiured as a list so we can have more than one path
    path = raw_input('Path to the fingerprint page (/index.php): ')
    path_list = list()
    path_list.append(path)
    fp['url'] = path_list

    fp_status = raw_input('HTTP status code of fingerprint (401, 200): ')
    fp_body = raw_input('Unique string in the fingerprint page (Welcome to ***): ')
    server_header = raw_input('Server header (if unique): ')
    basic_auth_realm = raw_input('Basic Auth Realm: ')

    fp['status'] = int(fp_status)
    if fp_body:
        fp['body'] = [fp_body]
    if basic_auth_realm:
        fp['basic_auth_realm'] = basic_auth_realm
    if server_header:
        fp['server_header'] = server_header

    parameters['fingerprint'] = fp

    # Authentication
    ###############################################################################
    auth = dict()
    headers = list()
    auth_urls = list()
    url = raw_input('Authentication URL (/login.php): ')
    auth_urls.append(url)
    auth['url'] = auth_urls

    while True:
        t = raw_input('Type of authentication method (post, basic_auth, get, raw_post): ')
        if t in auth_types:
            auth['type'] = t
            break
        else:
            print 'Invalid auth type'

    if auth['type'] == 'post' or auth['type'] == 'get':
        form = dict()
        form['username'] = raw_input('Name of username field: ')
        form['password'] = raw_input('Name of password field: ')
        form_params = raw_input('Post parameters, query string or raw post (json, xml): ')

        if form_params:
            form_params = urllib.unquote_plus(form_params)  # decode the parameters
            for f in form_params.split('&'):
                fname = f.split('=')[0]
                fvalue = f.split('=')[1]
                if fname == form['username'] or fname == form['password']:
                    continue
                else:
                    form[fname] = fvalue

        if auth['type'] == 'raw_post':
            form['raw'] = form_params

        auth[auth['type']] = form
    while True:
        header = raw_input('Pleae enter any custom header needed. Hit enter if done or not needed \n Example: Content-Type: application/json: ')
        if len(header) > 0:
            if len(header.split(':')) == 2:
                h = header.split(':')
                header = {h[0]: h[1]}
                headers.append(header)
            else:
                print 'Invalid header.  Headers must be in the format "Header_name: header_value"\n'
        else:
            break
    csrf = raw_input('Name of csrf field: ')
    if csrf:
        auth['csrf'] = csrf

    sessionid = raw_input('Name of session cookie: ')
    if sessionid:
        auth['sessionid'] = sessionid

    creds = list()
    num_creds = raw_input('How many default creds for this service (1, 2, 3): ')
    for i in range(0, int(num_creds)):
        user = raw_input('Username %i: ' % (i + 1))
        passwd = raw_input('Password %i: ' % (i + 1))

        if auth['type'] == 'raw_post':
            raw = raw_input('Raw post %i: ' % (i + 1))
            creds.append({'username': user, 'password': passwd, 'raw': raw})
        else:
            creds.append({'username': user, 'password': passwd})

    auth['credentials'] = creds
    auth['headers'] = headers

    success = dict()
    success['status'] = int(raw_input('HTTP status code of success (200, 302): '))
    success['body'] = raw_input('Unique string in page of a successful login (Logout</a>): ')

    auth['success'] = success
    parameters['auth'] = auth

    print
    fname = parameters['name'].lower().replace(' ', '_').replace('/', '_') + '.yml'
    print 'Writing config to %s' % fname

    with open(os.path.join('creds', parameters['protocol'], parameters['category'], fname), 'w') as fout:
        fout.write(yaml.dump(parameters, default_flow_style=False))

    print yaml.dump(parameters, default_flow_style=False)

    changeme.core.validate_cred(parameters, fname, parameters['category'])
