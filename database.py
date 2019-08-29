from clasfw.extensions import db

Base = db.Model

Column       = db.Column
Boolean      = db.Boolean
Integer      = db.Integer
SmallInteger = db.SmallInteger
DateTime     = db.DateTime
TIMESTAMP    = db.TIMESTAMP
Float        = db.Float
String       = db.String
Text         = db.Text
LargeBinary  = db.LargeBinary

ForeignKey   = db.ForeignKey
ForeignKeyConstraint = db.ForeignKeyConstraint
UniqueConstraint     = db.UniqueConstraint
func         = db.func
desc         = db.desc

relationship = db.relationship
backref      = db.backref
deferred     = db.deferred
composite    = db.composite
load_only    = db.load_only
