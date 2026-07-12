from app.models.audit_log import AuditLog


class TestAuditLogModel:

    def test_create(self, db):
        log = AuditLog(user_id=1, action='login', target_type='auth', ip_address='127.0.0.1')
        db.add(log)
        db.commit()
        assert log.id is not None
        assert log.action == 'login'

    def test_to_dict(self, db):
        log = AuditLog(user_id=1, action='login', target_type='auth', ip_address='127.0.0.1', details={'key': 'val'})
        db.add(log)
        db.commit()
        d = log.to_dict()
        assert d['action'] == 'login'
        assert d['target_type'] == 'auth'
        assert d['ip_address'] == '127.0.0.1'
        assert d['details'] == {'key': 'val'}
        assert d['created_at'] is not None

    def test_to_dict_no_details(self, db):
        log = AuditLog(user_id=1, action='test')
        db.add(log)
        db.commit()
        d = log.to_dict()
        assert d['details'] is None

    def test_repr(self, db):
        log = AuditLog(user_id=1, action='login')
        db.add(log)
        db.commit()
        assert 'AuditLog' in repr(log)
        assert 'login' in repr(log)
