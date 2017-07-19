summoners_pipeline = [
        #{"$skip": skip},
        #{"$limit": limit},

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
