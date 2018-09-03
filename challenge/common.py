from challenge import db
from challenge.models import Sku

def create_or_update_sku(data):
    integrity_check = None
    if data.get('id'):
        integrity_check = Sku.query.get(data['id'])
    if integrity_check:
        for key, value in data.iteritems():
            setattr(integrity_check, key, value)
    else:
        sku = Sku(**data)
        db.session.add(sku)
    db.session.commit()

def serialize_json(query_object):
    resp_list = []
    for obj in query_object:
        ret_obj = {}
        for key in obj.__mapper__.c.keys():
            ret_obj[key] = getattr(obj, key)
        resp_list.append(ret_obj)

    return resp_list