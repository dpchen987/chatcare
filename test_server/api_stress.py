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
        '-c', '--concurrence', type=int, required=True,
        help='Number of concurrent queries')
    parser.add_argument(
        '-n', '--num_query', type=int, default=0,
        help='Total number of queries (0 for all)')
    args = parser.parse_args()
    return args


async def test_coro(api, taskid, text, result):
    begin = time.time()
    query = {
        'task_id': taskid,
        'text': text,
        # Add other query parameters specific to the new API here
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(api, json=query) as resp:
            response_text = await resp.text()
    end = time.time()
    result.append({
        'taskid': taskid,
        'begin': begin,
        'end': end,
        'response_text': response_text
    })



async def main(args):
    texts = args.text
    tasks = set()
    result = []
    begin = time.time()
    now = time.strftime('%Y-%m-%d_%H:%M:%S')

    for i, text in enumerate(texts):
        if args.num_query and args.num_query < i:
            break
        task_id = now + f'{i:012}'
        task = asyncio.create_task(
            test_coro(args.api_uri, task_id, text, result))
        tasks.add(task)
        task.add_done_callback(tasks.discard)

        if len(tasks) < args.concurrence:
            continue

        if i % args.concurrence == 0:
            print(f'{i=}, start {args.concurrence} '
                  f'queries @ {time.strftime("%m-%d %H:%M:%S")}')

        await asyncio.sleep(0.05)

        while len(tasks) >= args.concurrence:
            await asyncio.sleep(0.05)

    while tasks:
        await asyncio.sleep(0.1)

    with open(f'{now}.log', 'w') as f:
        json.dump(result, f, indent=2)

    print('done', time.time() - begin)


if __name__ == '__main__':
    args = get_args()
    asyncio.run(main(args))
