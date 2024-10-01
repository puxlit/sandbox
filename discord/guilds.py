#!/usr/bin/env python3


########################################################################################################################
# Imports
########################################################################################################################

from base64 import b64decode

from discord_protos import PreloadedUserSettings
import requests
import yaml


########################################################################################################################
# Discord stuff
########################################################################################################################

API_BASE_URL = 'https://discord.com/api/v9'


def get_user_guilds(token):
    response = requests.get(f'{API_BASE_URL}/users/@me/guilds', headers={'Authorization': token})
    assert(response.status_code == 200)
    guilds = response.json()
    return {int(guild['id']): guild for guild in guilds}


def get_user_settings(token):
    response = requests.get(f'{API_BASE_URL}/users/@me/settings-proto/1', headers={'Authorization': token})
    assert(response.status_code == 200)
    settings = PreloadedUserSettings.FromString(b64decode(response.json()['settings']))
    return settings


def transform_to_guild_positions(settings, guilds):
    direct_messages_restricted_guild_ids = set(settings.privacy.restricted_guild_ids)
    message_request_restricted_guild_ids = set(settings.privacy.message_request_restricted_guild_ids)
    activity_status_restricted_guild_ids = set(settings.privacy.activity_restricted_guild_ids)
    activity_joining_restricted_guild_ids = set(settings.privacy.activity_joining_restricted_guild_ids)
    for folder in settings.guild_folders.folders:
        folder_guilds = list({
            'guild': guild_id,
            'name': guilds[guild_id]['name'],
            'privacy_settings': {
                'allow_direct_messages': guild_id not in direct_messages_restricted_guild_ids,
                'filter_direct_messages': guild_id not in message_request_restricted_guild_ids,
                'share_activity_status': guild_id not in activity_status_restricted_guild_ids,
                'allow_activity_joining': guild_id not in activity_joining_restricted_guild_ids,
            },
        } for guild_id in folder.guild_ids)
        if not folder.HasField('id'):
            assert not folder.HasField('name')
            yield from folder_guilds
        else:
            yield {'folder': folder.id.value, 'name': folder.name.value, 'guilds': folder_guilds}


########################################################################################################################
# CLI bootstrap
########################################################################################################################

def main():
    from getpass import getpass

    token = getpass('Token: ')
    settings = get_user_settings(token)
    guilds = get_user_guilds(token)
    guild_positions = list(transform_to_guild_positions(settings, guilds))
    print(yaml.dump(guild_positions, sort_keys=False), end='')


if __name__ == '__main__':
    main()
