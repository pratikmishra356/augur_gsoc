#SPDX-License-Identifier: MIT
"""
Augur library script for generating a config file
"""

import os
import click
import json
import logging

from augur.config import default_config, ENVVAR_PREFIX
from augur.cli import pass_config
from augur.logging import ROOT_AUGUR_DIRECTORY

logger = logging.getLogger("augur.cli")

@click.group('configure', short_help='Generate an augur.config.json')
def cli():
    pass

@cli.command('generate')
@click.option('--db_name', help="Database name for your data collection database", envvar=ENVVAR_PREFIX + 'DB_NAME')
@click.option('--db_host', help="Host for your data collection database", envvar=ENVVAR_PREFIX + 'DB_HOST')
@click.option('--db_user', help="User for your data collection database", envvar=ENVVAR_PREFIX + 'DB_USER')
@click.option('--db_port', help="Port for your data collection database", envvar=ENVVAR_PREFIX + 'DB_PORT')
@click.option('--db_password', help="Password for your data collection database", envvar=ENVVAR_PREFIX + 'DB_PASSWORD')
@click.option('--github_api_key', help="GitHub API key for data collection from the GitHub API", envvar=ENVVAR_PREFIX + 'GITHUB_API_KEY')
@click.option('--facade_repo_directory', help="Directory on the database server where Facade should clone repos", envvar=ENVVAR_PREFIX + 'FACADE_REPO_DIRECTORY')
@click.option('--rc-config-file', help="File containing existing config whose values will be used as the defaults", type=click.Path(exists=True))
@click.option('--gitlab_api_key', help="GitLab API key for data collection from the GitLab API", envvar=ENVVAR_PREFIX + 'GITLAB_API_KEY')
@pass_config
def generate(augur_config, db_name, db_host, db_user, db_port, db_password, github_api_key, facade_repo_directory, rc_config_file, gitlab_api_key):
    """
    Generate an augur.config.json
    """

    config = default_config
    rc_config = None

    if rc_config_file != None:
        try:
            with open(os.path.abspath(rc_config_file), 'r') as f:
                rc_config = json.load(f)
                for item in rc_config.items():
                    if item[0] == 'Workers':
                        for index in range(0, len(item[1])):
                            key = list(item[1].keys())[index]
                            secondary_dict = list(item[1].values())[index]

                            for secondary_dict_index in range(0, len(secondary_dict)):
                                secondary_key = list(secondary_dict.keys())[secondary_dict_index]
                                value = list(secondary_dict.values())[secondary_dict_index]

                                config[item[0]][key][secondary_key] = value
                    else:
                        for index, key in enumerate(list(item[1].keys())):
                            config[item[0]][key] = list(item[1].values())[index]

                logger.info('Predefined config successfully loaded')

        except Exception as e:
            logger.error(f"Error opening {rc_config_file}: {str(e)}")

    if db_name is not None:
        config['Database']['database'] = db_name # this is for backwards compatibility
    if db_name is not None:
        config['Database']['name'] = db_name
    if db_host is not None:
        config['Database']['host'] = db_host
    if db_port is not None:
        config['Database']['port'] = int(db_port)
    if db_user is not None:
        config['Database']['user'] = db_user
    if db_password is not None:
        config['Database']['password'] = db_password
    if github_api_key is not None:
        config['Database']['key'] = github_api_key
    if gitlab_api_key is not None:
        config['Database']['gitlab_api_key'] = gitlab_api_key
    if facade_repo_directory is not None:
        config['Workers']['facade_worker']['repo_directory'] = facade_repo_directory

    try:
        with open(os.path.abspath(ROOT_AUGUR_DIRECTORY + '/augur.config.json'), 'w') as f:
            json.dump(config, f, indent=4)
            logger.info('augur.config.json successfully created')
    except Exception as e:
        logger.error("Error writing augur.config.json " + str(e))
