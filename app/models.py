from app import db


class Data(db.Model):
    entryId = db.Column(db.Integer, primary_key=True)
    entryType = db.Column(db.String(64))
    entryName = db.Column(db.String(64))
    entryData = db.Column(db.String(255))
    entryDate = db.Column(db.String(32))

    def __repr__(self):
        return '<SQL Date %r>' % (self.entryType)


class Notification(db.Model):
    nId = db.Column(db.Integer, primary_key=True)
    nType = db.Column(db.String(64))
    name = db.Column(db.String(255))
    entry = db.Column(db.String(255))

    def __repr__(self):
        return '<SQL Notification %r>' % (self.nType)


class Module(db.Model):
    mId = db.Column(db.Integer, primary_key=True)
    slugName = db.Column(db.String(64))
    name = db.Column(db.String(120))
    description = db.Column(db.String(1024))

    def __repr__(self):
        return '<SQL Module %r>' % (self.slugName)
