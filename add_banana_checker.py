#!/usr/bin/env python3

from collections import OrderedDict
import json
import os
import subprocess
import sys

import lib

if os.path.exists('package.json'):
    print('package.json already exists')
    sys.exit(1)

ext = os.getcwd().split('/')[-1]
print('Configuring banana checker for %s extension...' % ext)

grunt_file = """/*!
 * Grunt file
 *
 * @package %s
 */

/*jshint node:true */
module.exports = function ( grunt ) {
	grunt.loadNpmTasks( 'grunt-banana-checker' );
	grunt.loadNpmTasks( 'grunt-jsonlint' );

	var conf = grunt.file.readJSON( 'extension.json' );
	grunt.initConfig( {
		banana: conf.MessagesDirs,
		jsonlint: {
			all: [ '!(node_modules)/**/*.json' ]
		}
	} );

	grunt.registerTask( 'test', [ 'jsonlint', 'banana' ] );
	grunt.registerTask( 'default', 'test' );
};
"""

if not os.path.exists('extension.json'):
    print('No extension.json, cannot add banana-checker')
    sys.exit(1)
with open('Gruntfile.js', 'w') as f:
    f.write(grunt_file % ext)


package_data = OrderedDict([
    ('name', ext.lower()),
    ('version', '0.0.0'),
    ('private', True),
    ('description', 'Build tools for the %s extension.' % ext),
    ('scripts', {'test': 'grunt test'}),
    ('devDependencies', OrderedDict())
])
for i in ['grunt', 'grunt-cli', 'grunt-banana-checker', 'grunt-jsonlint']:
    package_data['devDependencies'][i] = lib.get_npm_version(i)
with open('package.json', 'w') as f:
    f.write(json.dumps(package_data, indent='  ') + '\n')
subprocess.call(['npm', 'install'])
res = subprocess.call(['npm', 'test'])
if res != 0:
    print('Error: npm test failed.')
    sys.exit(1)
else:
    print('Yay, npm test passed!')
# Add node_modules to gitignore...
if os.path.exists('.gitignore'):
    add = True
    with open('.gitignore') as f:
        for line in f.read().splitlines():
            if line.strip().startswith('node_modules'):
                add = False
                break
        if add:
            with open('.gitignore', 'a') as f:
                f.write('node_modules/\n')
            print('Added "node_modules/" to .gitignore')
else:
    with open('.gitignore', 'w') as f:
        f.write('node_modules/\n')
        print('Created .gitignore with "node_modules/"')
msg = 'build: Configuring banana-checker and jsonlint'
if len(sys.argv) > 1:
    msg += '\n\nChange-Id: %s' % sys.argv[1]
lib.commit_and_push(files=['package.json', 'Gruntfile.js', '.gitignore'], msg=msg, branch='master', topic='banana')
sha1 = subprocess.check_output(['git', 'log', '--oneline', '-n', '1']).decode().split(' ', 1)[0]
subprocess.call(['ssh', '-p' , '29418', 'gerrit.wikimedia.org', 'gerrit', 'review', '-m', '"check experimental"', sha1])
