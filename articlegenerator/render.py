#!/usr/bin/env python

from jinja2 import Environment, PackageLoader

# Load the template store
env = Environment(loader=PackageLoader('articlegenerator', 'templates'))

template = env.get_template('example_template.html')


article_data = {
                'xsversion': '1.0',
                'ctx': 'CTX1111',
                'vendor_name': 'Coorp',
                'kernel_version': '2.6.32.x',
                'iso': {
                        'name':'test.iso',
                        'md5' :'124391240',
                       },

                'drivers': [
                              {'name': 'drivera', 'version': '2.1'},
                              {'name': 'driverb', 'version': '2.0'},
                           ],   
    
                'rpms': [
                            {'module_name':'rpm1', 'version': '1.0', 'file_name':'rpm1-test.rpm'},
                            {'module_name':'rpm2', 'version': '2.0', 'file_name':'rpm2-test.rpm'},

                        ],

                'zip': {
                        'name':'test.zip',
                        'md5' : '23525323',
                       },
                'meta_md5': '2135235',
                'supppackguide': 'CTX12354',

                # Hotfix specific
                'hfx_name': 'HFX60201',
                'originalctx': 'CTX12541',
                }




print template.render(**article_data) 



