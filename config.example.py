{
	# obtained from https://my.telegram.org
	'api_id': ...,
	'api_hash': ...,
	# obtained from the BotFather
	'api_token': ...,
	# pick anything, it doesn't matter
	'session_name': 'anon',

	# the ID of your AdventOfCode user
	# get this from https://adventofcode.com/2020/leaderboard/private, and [View] your own leaderboard.
	# Your user ID is the last part of the URL.
	'owner_id': ...,

	# the ID of a private leaderboard
	# get this from https://adventofcode.com/2020/leaderboard/private, and [View] any leaderboard you're a member of.
	# The leaderboard ID is the last part of the URL.
        # (it may be the same as your owner_id, if you are the owner of that leaderboard)
	'aoc_leaderboard_id': ...,
	# your session cookie obtained after signing in to AoC
	'aoc_session_cookie': ...,
	# Only members of this chat ID will be able to access score commands.
	# If set to None, or not set, anyone will be able to access the configured private leaderboard.
        # get this from https://api.telegram.org/bot1111111111:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/getUpdates
	'aoc_chat_id': None, # "chat":{"id":-999999999,"title":"our adventOfCode group","type":"group","all_members_are_administrators":true}
	# Whether to send a message to the above chat ID whenever a new puzzle is expected to release.
	'aoc_notify': True
}
