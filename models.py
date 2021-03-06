from app import db

class Fixture(db.Model):
    __tablename__ = 'fixture'

    fixture_id = db.Column(db.BigInteger, primary_key=True)
    league_id = db.Column(db.Integer, index=True, unique=False)
    shots_on_goal_home = db.Column(db.Integer, index=False, unique=False)
    shots_on_goal_away = db.Column(db.Integer, index=False, unique=False)
    shots_off_goal_home = db.Column(db.Integer, index=False, unique=False)
    shots_off_goal_away = db.Column(db.Integer, index=False, unique=False)
    total_shots_home = db.Column(db.Integer, index=False, unique=False)
    total_shots_away = db.Column(db.Integer, index=False, unique=False)
    blocked_shots_home = db.Column(db.Integer, index=False, unique=False)
    blocked_shots_away = db.Column(db.Integer, index=False, unique=False)
    shots_insidebox_home = db.Column(db.Integer, index=False, unique=False)
    shots_insidebox_away = db.Column(db.Integer, index=False, unique=False)
    shots_outsidebox_home = db.Column(db.Integer, index=False, unique=False)
    shots_outsidebox_away = db.Column(db.Integer, index=False, unique=False)
    fouls_home = db.Column(db.Integer, index=False, unique=False)
    fouls_away = db.Column(db.Integer, index=False, unique=False)
    corner_kicks_home = db.Column(db.Integer, index=False, unique=False)
    corner_kicks_away = db.Column(db.Integer, index=False, unique=False)
    offsides_home = db.Column(db.Integer, index=False, unique=False)
    offsides_away = db.Column(db.Integer, index=False, unique=False)
    ball_possession_home = db.Column(db.Float, index=False, unique=False)
    ball_possession_away = db.Column(db.Float, index=False, unique=False)
    yellow_cards_home = db.Column(db.Integer, index=False, unique=False)
    yellow_cards_away = db.Column(db.Integer, index=False, unique=False)
    red_cards_home = db.Column(db.Integer, index=False, unique=False)
    red_cards_away = db.Column(db.Integer, index=False, unique=False)
    goalkeeper_saves_home = db.Column(db.Integer, index=False, unique=False)
    goalkeeper_saves_away = db.Column(db.Integer, index=False, unique=False)
    total_passes_home = db.Column(db.Integer, index=False, unique=False)
    total_passes_away = db.Column(db.Integer, index=False, unique=False)
    passes_accurate_home = db.Column(db.Integer, index=False, unique=False)
    passes_accurate_away = db.Column(db.Integer, index=False, unique=False)
    passes_perc_home = db.Column(db.Float, index=False, unique=False)
    passes_perc_away = db.Column(db.Float, index=False, unique=False)

    def __repr__(self):
        return '<Fixture #{}>'.format(self.fixture_id)

class League(db.Model):
    __tablename__ = 'league'

    fixture_id = db.Column(db.BigInteger, primary_key=True)
    league_id = db.Column(db.Integer, index=True, unique=False)
    event_date = db.Column(db.DateTime, index=False, unique=False)
    event_timestamp = db.Column(db.BigInteger, index=False, unique=False)
    first_half_start = db.Column(db.BigInteger, index=False, unique=False)
    second_half_start = db.Column(db.BigInteger, index=False, unique=False)
    round = db.Column(db.String(64), index=False, unique=False)
    status = db.Column(db.String(64), index=False, unique=False)
    status_short = db.Column(db.String(2), index=False, unique=False)
    venue = db.Column(db.String(128), index=False, unique=False)
    home_goals = db.Column(db.Integer, index=False, unique=False)
    away_goals = db.Column(db.Integer, index=False, unique=False)
    away_team_id = db.Column(db.Integer, index=False, unique=False)
    away_team = db.Column(db.String(128), index=False, unique=False)
    home_team_id = db.Column(db.Integer, index=False, unique=False)
    home_team = db.Column(db.String(128), index=False, unique=False)
    halftime = db.Column(db.String(64), index=False, unique=False)
    fulltime = db.Column(db.String(64), index=False, unique=False)
    game_date = db.Column(db.DateTime, index=False, unique=False)
    league_day = db.Column(db.Integer, index=False, unique=False)

    def __repr__(self):
        return '<League #{}>'.format(self.fixture_id)