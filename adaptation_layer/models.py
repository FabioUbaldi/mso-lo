#  Copyright 2019 CNIT, Francesco Lombardo, Matteo Pergolesi
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import datetime

from config import db


class NFVO(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(128), nullable=False)
    type = db.Column('type', db.String(128), nullable=False)
    site = db.Column('site', db.String(128), nullable=False)
    uri = db.Column('uri', db.String(128))
    created_at = db.Column('created_at', db.DateTime,
                           default=datetime.datetime.utcnow())
    updated_at = db.Column('updated_at', db.DateTime,
                           default=datetime.datetime.utcnow())

    @property
    def serialize(self):
        """Return object data in serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'site': self.site,
            'uri': self.uri,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __init__(self, **kwargs):
        super(NFVO, self).__init__(**kwargs)

    def __repr__(self):
        return '<NFVO {}>'.format(self.id)


class NFVO_CREDENTIALS(db.Model):
    nfvo_id = db.Column('nfvo_id', db.Integer, db.ForeignKey(
        'NFVO.id'), primary_key=True)
    host = db.Column('host', db.String(128), nullable=False)
    project = db.Column('project', db.String(128), nullable=False)
    user = db.Column('user', db.String(128), nullable=False)
    password = db.Column('password', db.String(128), nullable=False)

    @property
    def serialize(self):
        """Return object data in serializeable format"""
        return {
            'nfvo_id': self.nfvo_id,
            'host': self.host,
            'project': self.project,
            'user': self.user,
            'password': self.password
        }
