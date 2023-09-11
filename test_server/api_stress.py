#!/usr/bin/env python3
# coding:utf-8

import os
import json
import time
import asyncio
import argparse
import aiohttp
import statistics


def get_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-u', '--api_uri',
        default='http://192.168.10.10:8000/v1/chat/completions',  # Update this to the new API endpoint
        help="Large Language Model API server's URI, default: http://192.168.10.10:8000/v1/chat/completions")
    parser.add_argument(
        '-t', '--texts', type=str, required=True,
        help='test texts')
    parser.add_argument(
        '-c', '--num_concurrence', type=int, required=True,
        help='Number of concurrent queries')
    # parser.add_argument(
    #     '-n', '--num_query', type=int, default=0,
    #     help='Total number of queries (0 for all)')
    args = parser.parse_args()
    return args


def print_result(info):
    length = max([len(k) for k in info])
    for k, v in info.items():
        print(f'\t{k: >{length}} : {v}')
        
        
async def test_coro(api, text, times):
    begin = time.time()
    query = {
        'content': text,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(api, json=query) as resp:
            response_text = await resp.text()
    end = time.time()
    times.append(end-begin)
    # result.append({
    #     'taskid': taskid,
    #     'begin': begin,
    #     'end': end,
    #     'response_text': response_text
    # })



async def main(args):
    tasks = set()
    request_times = []
    print('starting...')
    begin = time.time()
    for i in args.texts:
        task = asyncio.create_task(test_coro(args.api_uri, i, request_times))
        tasks.add(task)
        task.add_done_callback(tasks.discard)
        if len(tasks) < args.num_concurrence:
            continue
        print((f'{i=}, start {args.num_concurrence} '
               f'queries @ {time.strftime("%m-%d %H:%M:%S")}'))
        await asyncio.sleep(0.1)
        while len(tasks) >= args.num_concurrence:
            await asyncio.sleep(0.1)
    while tasks:
        await asyncio.sleep(0.1)
    request_time = time.time() - begin
    concur_info = {
        'request_time': request_time,
    }
    request_info = {
        'mean': statistics.mean(request_times),
        'median': statistics.median(request_times),
        'max_time': max(request_times),
        'min_time': min(request_times),
    }
    print('For all concurrence:')
    print_result(concur_info)
    print('For one request:')
    print_result(request_info)
    
    print('done')


if __name__ == '__main__':
    args = get_args()
    asyncio.run(main(args))

