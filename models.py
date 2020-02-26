from Main import db

class League(db.Model):
    fixture_id = db.Column(db.BigInteger, primary_key=True)
    league_id = db.Column(db.Integer, index=True, unique=True)
    event_date = db.Column(db.DateTime, index=True, unique=False)
    event_timestamp = db.Column(db.BigInteger, index=True, unique=False)
    first_half_start = db.Column(db.BigInteger, index=True, unique=False)
    second_half_start = db.Column(db.BigInteger, index=True, unique=False)
    round = db.Column(db.String(64), index=True, unique=False)
    status = db.Column(db.String(64), index=True, unique=False)
    status_short = db.Column(db.String(2), index=True, unique=False)
    venue = db.Column(db.String(128), index=True, unique=False)
    home_goals = db.Column(db.Integer, index=True, unique=True)
    away_goals = db.Column(db.Integer, index=True, unique=True)
    away_team_id = db.Column(db.Integer, index=True, unique=True)
    away_team = db.Column(db.String(128), index=True, unique=False)
    home_team_id = db.Column(db.Integer, index=True, unique=True)
    home_team = db.Column(db.String(128), index=True, unique=False)
    halftime = db.Column(db.String(64), index=True, unique=False)
    fulltime = db.Column(db.String(64), index=True, unique=False)
    game_date = db.Column(db.DateTime, index=True, unique=False)
    league_day = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return '<Fixture #{}>'.format(self.fixture_id)