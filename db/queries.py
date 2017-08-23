all_summoners = [
        #{"$skip": skip},
        #{"$limit": 1},

        # Gathers elos
        { '$unwind': '$leagues'},
        { '$unwind': '$leagues.entries'},
        {
            '$redact': {
                '$cond': {
                    'if': {'$eq': ['$leagues.entries.playerOrTeamName', '$nick']},
                    'then': '$$KEEP',
                    'else': '$$PRUNE'
                }
            }
        },
        {
        '$group': {
            '_id': '$nick',
            'leagues': {'$push': '$leagues'},
            'matches': {'$first': '$matches'},
            'ranked_stats': {'$first': '$ranked_stats'}
        }
        },

        # Project matches
        { '$unwind': '$matches'},
        { '$match': {'matches.season': 8}},

        {
            '$project': {
                'soloq': {'$arrayElemAt': ['$leagues', 0]},
                'flex': {'$arrayElemAt': ['$leagues', 1]},
                'matches': {
                    'gameId': '$matches.gameId',
                    'champion': '$matches.champion',
                    'role': {
                        '$cond': {
                            'if': { '$eq': ['$matches.lane', 'BOTTOM']},
                            'then': '$matches.role',
                            'else': '$matches.lane'
                        }
                    },
                },
                'ranked_stats': 1
            }
        },
        {
            '$project': {
                'soloq_tier': '$soloq.tier',
                'soloq_division': '$soloq.entries.rank',
                'flex_tier': '$flex.tier',
                'flex_division': '$flex.entries.rank',
                'matches': 1,
                'ranked_stats': 1
            }
        },
        {
            '$group': {
                '_id': '$_id',
                'nick': { '$first': '$_id' },
                'matches': {'$push': '$matches'},
                'ranked_stats': {'$first': '$ranked_stats'},
                'soloq_tier': {'$first': '$soloq_tier'},
                'soloq_division': {'$first': '$soloq_division'},
                'flex_tier': {'$first': '$flex_tier'},
                'flex_division': {'$first': '$flex_division'},
            }
        },
    ]

def all_nicks(skip=0):
    return [
        { "$project": {"_id":0, "nick":1} },
        { "$group": { "_id": "$nick" } }
    ]

def all_joined_summoners(nick):
    return [
		{ '$match': {'nick': nick}},
		# Unwind different queues
		{ '$unwind': '$leagues'},
		# Unwind every league member
		{ '$unwind': '$leagues.entries'},
		# Filtering only player in league
		{
			'$redact': {
				'$cond': {
					'if': {'$eq': ['$leagues.entries.playerOrTeamName', '$nick']},
					'then': '$$KEEP',
					'else': '$$PRUNE'
				}
			}
		},
		# Regrouping unwinded leagues
		{
		'$group': {
			'_id': '$nick',
			'leagues': {'$push': '$leagues'},
			'matches': {'$first': '$matches'},
			'ranked_stats': {'$first': '$ranked_stats'}
		}
		},

		# Unwind player s8 matches
		{ '$unwind': '$matches'},
		{ '$match': {'matches.season': 8}},

		# Performing join and unwinding joined array
		{
			'$lookup': {
					'from':'matches',
					'localField':'matches.gameId',
					'foreignField':'gameId',
					'as':'sumMatches'
			}
		},
		{ '$unwind': '$sumMatches' },
        # Compute the participantId field
        {
            '$project': {
                '_id': 1,
                'leagues': 1,
                'matches': 1,
                'ranked_stats': 1,
                'sumMatches': 1,
                'player': {
                    '$arrayElemAt': [
                        {
                            '$filter': {
                                'input':'$sumMatches.participantIdentities',
                                'as':'playerOnly',
                                'cond': { '$eq': ['$$playerOnly.player.summonerName','$_id'] }
                            }
                        },0]
                }
            }
        },
        # Compute the participants field
        {
            '$project': {
                '_id': 1,
                'leagues': 1,
                'matches': 1,
                'ranked_stats': 1,
                'sumMatches': 1,
                'participant': 	{
                    '$arrayElemAt': [ {
                        '$filter': {
                            'input':'$sumMatches.participants',
                            'as':'playerOnly',
                            'cond': { '$eq': ['$$playerOnly.participantId','$player.participantId'] }
                        }
                    },0]
                },
            }
        },
		# Projecting only convenient fields
		{
			'$project': {
				'soloq': {'$arrayElemAt': ['$leagues', 0]},
				'flex': {'$arrayElemAt': ['$leagues', 1]},
				'matches': {
					'gameId': '$matches.gameId',
					'champion': '$matches.champion',
					'role': {
                        '$cond': {
                            'if': { '$eq': ['$matches.lane', 'BOTTOM']},
                            'then': '$matches.role',
                            'else': '$matches.lane'
                        }
					},
                    'participant': {
                        'stats': '$participant.stats',
                        'timeline': '$participant.timeline',
                        'team': {
                            '$arrayElemAt': [ {
                                '$filter': {
                                    'input':'$sumMatches.teams',
                                    'as':'playerTeam',
                                    'cond': { '$eq': ['$$playerTeam.teamId','$participant.teamId'] }
                                }
                            }, 0]
                        }
                    },
					'gameDuration': '$sumMatches.gameDuration',
				},
				'ranked_stats': 1
			}
		},
		 {
			 '$project': {
				 'soloq_tier': '$soloq.tier',
				 'soloq_division': '$soloq.entries.rank',
				 'flex_tier': '$flex.tier',
				 'flex_division': '$flex.entries.rank',
				 'matches': 1,
				 'ranked_stats': 1
			 }
		 },
		 # Regrouping unwinded matches
		 {
			 '$group': {
				 '_id': '$_id',
				 'nick': { '$first': '$_id' },
				 'matches': {'$push': '$matches'},
				 'ranked_stats': {'$first': '$ranked_stats'},
				 'soloq_tier': {'$first': '$soloq_tier'},
				 'soloq_division': {'$first': '$soloq_division'},
				 'flex_tier': {'$first': '$flex_tier'},
				 'flex_division': {'$first': '$flex_division'},
			 }
		 },
]

def summoner_by_nick(nick):
    return [
            { "$match": { "nick":nick } },
            { "$project": {"_id": 0 } },
        ]