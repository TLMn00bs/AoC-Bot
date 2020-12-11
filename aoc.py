# Copyright © 2018–2019 Io Mintz <io@mintz.cc>
#
# AoC Bot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AoC Bot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with AoC Bot.  If not, see <https://www.gnu.org/licenses/>.

import asyncio
import collections
import datetime as dt
import io
import json
import logging
import operator
import os
import sys
import time
import typing
from pathlib import Path

from yarl import URL

RATE_LIMIT = 15 * 60

logger = logging.getLogger(__name__)

def score_leaderboard(leaderboard: dict) -> typing.Dict[int, typing.List[dict]]:
	scores = collections.defaultdict(list)
	for member in leaderboard['members'].values():
		partial = partial_member(member)
		scores[member['stars']].append(member)

	return sorted_dict(scores, reverse=True)

def owner(leaderboard: dict) -> dict:
	return partial_member(leaderboard['members'][leaderboard['owner_id']])

def partial_member(member: dict) -> dict:
	return {k: member[k] for k in ('id', 'name')}

def sorted_dict(d: dict, *, key=None, reverse=False) -> dict:
	return {k: d[k] for k in sorted(d, key=key, reverse=reverse)}

def format_leaderboard(leaderboard):
	out = io.StringIO()

	scores = score_leaderboard(leaderboard)
	year = leaderboard['event']

	out.write('[tlmn00bs ')
	#out.write(owner(leaderboard)['name'])
	#out.write("'s ")
	out.write(str(year))
	out.write(' leaderboard](')
	out.write('https://adventofcode.com/')
	out.write(year)
	out.write('/leaderboard/private/view/')
	out.write(leaderboard['owner_id'])
	out.write('?order=stars)\n')

	for score, members in scores.items():
		sorted_members = sorted(members, key=lambda member: int(member['id']))
		out.write('**')
		out.write(str(score))
		out.write('** ⭐ ')
		out.write(', '.join(map(operator.itemgetter('name'), sorted_members)))
		out.write('\n')

	return out.getvalue()

async def leaderboard(client, event=None):
	"""Fetch the latest leaderboard from the web if and only if it has not been fetched recently.
	Otherwise retrieve from disk.
	"""

	now = time.time()
	event = event or most_recent_event()
	try:
		last_modified = os.stat(f'leaderboards/{event}.json').st_mtime
	except FileNotFoundError:
		return await refresh_saved_leaderboard(client, event)

	if now - last_modified > RATE_LIMIT:
		return await refresh_saved_leaderboard(client, event)

	# we've fetched it recently
	return load_leaderboard(event)

async def refresh_saved_leaderboard(client, event=None):
	"""save the latest leaderboard to disk"""
	leaderboard = await fetch_leaderboard(client, event)
	save_leaderboard(leaderboard)
	return leaderboard

def save_leaderboard(leaderboard):
	with open(Path('leaderboards') / (leaderboard['event'] + '.json'), 'w') as f:
		json.dump(leaderboard, f, indent=4, ensure_ascii=False)
		f.write('\n')

def load_leaderboard(event):
	with open(Path('leaderboards') / (event + '.json')) as f:
		return json.load(f)

def validate_headers(resp):
	if resp.status == 302:
		url = URL(resp.headers['Location'])
		if url.parts[-2:] == ('leaderboard', 'private'):
			raise RuntimeError('You are not a member of the configured leaderboard.')
		if url.parts[-1] == 'leaderboard':
			raise RuntimeError('An improper session cookie has been configured.')
	elif resp.status != 200:
		resp.raise_for_status()

async def login(client):
	async with client.http.head(leaderboard_url(client), allow_redirects=False) as resp:
		validate_headers(resp)

async def fetch_leaderboard(client, event=None):
	logger.debug('Fetching {event or "most recent"} leaderboard over HTTP')
	async with client.http.get(
		leaderboard_url(client, event),
		allow_redirects=False,  # redirects are used as error codes
	) as resp:
		validate_headers(resp)
		return await resp.json()

def most_recent_event():
	now = dt.datetime.utcnow() - dt.timedelta(hours=5)  # ehh, who cares about DST
	return str(now.year if now.month == 12 else now.year - 1)

def leaderboard_url(client, event=None):
	event = event or most_recent_event()
	return f'https://adventofcode.com/{event}/leaderboard/private/view/{client.config["aoc_leaderboard_id"]}.json'

if __name__ == '__main__':
	main()
