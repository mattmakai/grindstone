from datetime import datetime, timedelta

from grindstone.models import User, Follower, Service

def load(db):
    services = [Service("GitHub", "https://github.com/"),
                Service("Google", "https://google.com/"),
                Service("Twitter", "https://twitter.com/"),]
    for s in services:
        db.session.add(s)
    db.session.commit()
    """
    github = Service.query.all()[0]
    dt = datetime.now()
    followers = []
    for r in range(0, 99):
        f = Follower(github, 100+r, dt-timedelta(days=(100-r)))
        followers.append(f)
        db.session.add(f)
    """
    db.session.commit()
