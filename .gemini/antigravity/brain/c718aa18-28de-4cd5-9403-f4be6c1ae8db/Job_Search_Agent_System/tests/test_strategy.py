from datetime import datetime, timedelta
from agents.strategy import CanalApplication, FollowUpStrategy

def test_canal_application_with_email():
    agent = CanalApplication()
    res = agent.process({'email_trouve': 'test@test.com'})
    assert res['canal_recommande'] == 'Email direct'
    assert res['contact_cible'] == 'test@test.com'

def test_canal_application_no_email():
    agent = CanalApplication()
    res = agent.process({})
    assert res['canal_recommande'] == 'Formulaire ou LinkedIn'
    assert res['contact_cible'] == ''

def test_follow_up_strategy_valid_date():
    agent = FollowUpStrategy()
    res = agent.process('2024-01-01')
    assert res['date_relance_j4'] == '2024-01-05'
    assert res['date_relance_j10'] == '2024-01-11'

def test_follow_up_strategy_today():
    agent = FollowUpStrategy()
    res = agent.process('aujourd')
    now_j4 = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')
    assert res['date_relance_j4'] == now_j4

def test_follow_up_strategy_invalid_date():
    agent = FollowUpStrategy()
    res = agent.process('invalid-date')
    now_j4 = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d')
    assert res['date_relance_j4'] == now_j4
