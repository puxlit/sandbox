#!/usr/bin/env python3


########################################################################################################################
# Imports and exports
########################################################################################################################

import contextlib
from datetime import timedelta
import hashlib
from itertools import count
import json
import logging
import os
import tempfile
from time import sleep
from typing import NamedTuple, Optional, Union

import requests

__all__ = (
    'newdir', 'newfile',
    'scrape',
)


########################################################################################################################
# Utils
########################################################################################################################

def break_into_debugger():
    import pdb
    pdb.set_trace()


########################################################################################################################
# File system context managers
########################################################################################################################

@contextlib.contextmanager
def newdir(path, name: Optional[str], mode):
    temp_path = tempfile.mkdtemp() if name is None else name
    fd = os.open(temp_path, os.O_DIRECTORY)
    logging.debug(f'newdir: fd is {fd}; temp path is {temp_path}')
    yield fd  # Maybe we should delete the temp directory if the block throws an exception… ¯\_(ツ)_/¯
    os.close(fd)
    os.rename(temp_path, path)
    os.chmod(path, mode)


@contextlib.contextmanager
def newfile(dir_fd, name, file_mode, open_mode, open_buffering):
    def opener(path, flags):
        return os.open(path, flags, mode=file_mode, dir_fd=dir_fd)
    fh = open(name, mode=open_mode, buffering=open_buffering, opener=opener)
    logging.debug(f'newfile: fd is {fh.fileno()}')
    yield fh


########################################################################################################################
# Twitch API
########################################################################################################################

# Client ID `kimne78kx3ncx6brgo4mv6wki5h1ko` is baked into HTML; search for /,clientId="([^"]+)",commonOptions=/ in
# <https://www.twitch.tv/>. However, it looks like other client IDs might be less restricted; see
# <https://github.com/ihabunek/twitch-dl/issues/124#issuecomment-1537030937>.
CLIENT_ID = 'kd1unb4b3q4t58fwlpcbzcbnm76a8fp'
GRAPHQL_ENDPOINT = 'https://gql.twitch.tv/gql'


class VideoMetadataQueryOp(NamedTuple):
    channel_login: str
    video_id: int

    @property
    def serialised(self) -> dict:
        return {
            'operationName': 'VideoMetadata',
            'variables': {
                'channelLogin': self.channel_login,
                'videoID': str(self.video_id),
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': 'c25707c1e5176320ceac6b447d052480887e23bc794ca1d02becd0bcc91844fe',
                },
            },
        }


class VideoCommentsQueryOp(NamedTuple):
    video_id: int

    @property
    def serialised(self) -> dict:
        return {
            'operationName': 'VideoComments',
            'variables': {
                'videoID': str(self.video_id),
                'hasVideoID': True,
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': 'be06407e8d7cda72f2ee086ebb11abb6b062a7deb8985738e648090904d2f0eb',
                },
            },
        }


class VideoCommentsByOffsetQueryOp(NamedTuple):
    video_id: int
    content_offset_seconds: int

    @property
    def serialised(self) -> dict:
        return {
            'operationName': 'VideoCommentsByOffsetOrCursor',
            'variables': {
                'videoID': str(self.video_id),
                'contentOffsetSeconds': self.content_offset_seconds,
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': 'b70a3591ff0f4e0313d126c6a1502d79a1c02baebb288227c582044aa76adf6a',
                },
            },
        }


class VideoCommentsByCursorQueryOp(NamedTuple):
    video_id: int
    cursor: str

    @property
    def serialised(self) -> dict:
        return {
            'operationName': 'VideoCommentsByOffsetOrCursor',
            'variables': {
                'videoID': str(self.video_id),
                'cursor': self.cursor,
            },
            'extensions': {
                'persistedQuery': {
                    'version': 1,
                    'sha256Hash': 'b70a3591ff0f4e0313d126c6a1502d79a1c02baebb288227c582044aa76adf6a',
                },
            },
        }


def get_rechat_response(referrer_url: str, query_ops: list[Union[VideoMetadataQueryOp, VideoCommentsQueryOp, VideoCommentsByOffsetQueryOp, VideoCommentsByCursorQueryOp]]) -> tuple[str, bytes, dict]:
    request_payload = json.dumps([query_op.serialised for query_op in query_ops], sort_keys=False, separators=(',', ':'))
    headers = {
        'Accept': '*/*',
        'Client-Id': CLIENT_ID,
        'Content-Type': 'text/plain;charset=UTF-8',
        'Referer': referrer_url,
    }
    curl_request = f'''curl \'{GRAPHQL_ENDPOINT}\' {' '.join(f"-H '{k}: {v}'" for (k, v) in headers.items())} --data-raw \'{request_payload}\''''
    response = requests.post(GRAPHQL_ENDPOINT, data=request_payload, headers=headers)
    if response.status_code != 200:
        break_into_debugger()
    binary_response = response.content
    json_response = response.json()
    if not ((len(json_response) == len(query_ops)) and all((op_response['extensions']['operationName'] == query_op.serialised['operationName']) for (query_op, op_response) in zip(query_ops, json_response))):
        break_into_debugger()
    return (curl_request, binary_response, json_response)


def scrape(channel_login: str, video_id: int, resume: Optional[tuple[str, str, int]]) -> None:
    referrer_url = f'https://www.twitch.tv/videos/{video_id}'

    temp_dir_path: Optional[str] = None if resume is None else resume[0]
    cursor: Optional[str] = None if resume is None else resume[1]
    starting_index = 0 if resume is None else resume[2]
    assert (cursor is None and starting_index == 0) or (cursor is not None and starting_index >= 1)
    newfile_open_mode = 'w' if resume is None else 'a'
    total_duration = '???'

    dir_name = f'v{video_id}-rechat'
    with newdir(dir_name, temp_dir_path, 0o555) as dir_fd, newfile(dir_fd, 'scrape.sh', 0o555, newfile_open_mode, 1) as scrape_fh, newfile(dir_fd, 'sha1sum.txt', 0o444, newfile_open_mode, 1) as sha1sum_fh:
        if resume is None:
            scrape_fh.write('#!/bin/bash -eux\n\n')
        for i in count(starting_index):
            query_ops: list[Union[VideoMetadataQueryOp, VideoCommentsQueryOp, VideoCommentsByOffsetQueryOp, VideoCommentsByCursorQueryOp]] = []
            if i == 0:
                query_ops.extend([
                    VideoMetadataQueryOp(channel_login, video_id),
                    VideoCommentsQueryOp(video_id),
                    VideoCommentsByOffsetQueryOp(video_id, 0),
                ])
            else:
                assert cursor is not None
                query_ops.append(VideoCommentsByCursorQueryOp(video_id, cursor))
            (curl_request, binary_response, json_response) = get_rechat_response(referrer_url, query_ops)
            file_name = f'{i}.json'
            with newfile(dir_fd, file_name, 0o444, 'wb', 0) as file_fh:
                file_fh.write(binary_response)
            scrape_fh.write(f'{curl_request} -o \'{file_name}\'\n')
            sha1sum_fh.write(f'{hashlib.sha1(binary_response).hexdigest()}  {file_name}\n')

            edges = json_response[-1]['data']['video']['comments']['edges']

            if i == 0:
                total_duration = str(timedelta(seconds=json_response[0]['data']['video']['lengthSeconds']))
            scanned_min = str(timedelta(seconds=min(edge['node']['contentOffsetSeconds'] for edge in edges)))
            scanned_max = str(timedelta(seconds=max(edge['node']['contentOffsetSeconds'] for edge in edges)))
            logging.debug(f'progress: [{i}] {len(edges)} comments from {scanned_min} to {scanned_max} out of {total_duration}')

            if not json_response[-1]['data']['video']['comments']['pageInfo']['hasNextPage']:
                break
            cursors = set(edge['cursor'] for edge in edges)
            if len(cursors) != 1:
                break_into_debugger()
            cursor = cursors.pop()

            sleep(1)


########################################################################################################################
# CLI bootstrap
########################################################################################################################

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('channel_login')
    parser.add_argument('video_id', type=int)
    parser.add_argument('--temp-dir-path', required=False)
    parser.add_argument('--cursor', required=False)
    parser.add_argument('--index', type=int, required=False)
    args = parser.parse_args()
    assert (args.temp_dir_path is None) == (args.cursor is None) == (args.index is None)
    if (args.temp_dir_path is not None) and (args.cursor is not None) and (args.index is not None):
        resume = (args.temp_dir_path, args.cursor, args.index)
    else:
        resume = None

    logging.basicConfig(level=logging.DEBUG)
    scrape(args.channel_login, args.video_id, resume)


if __name__ == '__main__':
    main()
