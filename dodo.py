# encoding=utf8
from doit import get_var

import os
import logging
import logging.config
logging.config.fileConfig('logging.cfg', )
logger = logging.getLogger(__name__)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('rdflib').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('subscriber').setLevel(logging.WARNING)

import data_ub_tasks

config = {
    'dumps_dir': get_var('dumps_dir', '/opt/data.ub/www/default/dumps'),
    'dumps_dir_url': get_var('dumps_dir_url', 'http://data.ub.uio.no/dumps'),
    'basename': 'lskjema',
    'graph': 'http://data.ub.uio.no/lskjema',
    'fuseki': 'http://localhost:3031/ds',
    'git_user': 'ubo-bot',
    'git_email': 'danmichaelo+ubobot@gmail.com',
    'es_index': 'authority',
}

DOIT_CONFIG = {
    'default_tasks': [
        'git-push',
        'publish-dumps',
        'fuseki',
    ]
}


def task_fetch():
    yield data_ub_tasks.fetch_remote_gen(
        'https://app.uio.no/ub/ujur/l-skjema/cgi-bin/export/lskjema.cgi?visalle=xml',
        'dist/%(basename)s.marc21.xml' % config,
        []
    )


def task_build_skos():
    return {
        'doc': 'Build SKOS/Turtle',
        'basename': 'build-skos',
        'actions': [
            'mc2skos --include lskjema.scheme.ttl dist/%s.marc21.xml >| dist/%s.ttl' % (config['basename'], config['basename'])
        ],
        'file_dep': [
            'dist/%s.marc21.xml' % config['basename']
        ],
        'targets': [
            'dist/%s.ttl' % config['basename']
        ]
    }


def task_build_json():
    return data_ub_tasks.gen_solr_json(config, 'lskjema')


def task_git_push():
    return data_ub_tasks.git_push_task_gen(config)


def task_fuseki():
    return data_ub_tasks.fuseki_task_gen(config, ['dist/%(basename)s.ttl'])


def task_publish_dumps():
    return data_ub_tasks.publish_dumps_task_gen(config['dumps_dir'], [
        '%s.marc21.xml' % config['basename'],
        '%s.ttl' % config['basename'],
    ])


def task_elasticsearch():
    return data_ub_tasks.gen_elasticsearch(config, 'lskjema')
