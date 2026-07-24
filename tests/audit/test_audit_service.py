from src.audit.service import AuditService


class TestAuditService:

    def test_log(self, db):
        entry = AuditService(db).log(
            action='test.action', user_id=1, target_type='device',
            target_id=5, ip_address='10.0.0.1', details={'rows': 10}
        )
        assert entry.id is not None
        assert entry.action == 'test.action'
        assert entry.user_id == 1
        assert entry.target_type == 'device'
        assert entry.target_id == 5
        assert entry.ip_address == '10.0.0.1'
        assert entry.details == {'rows': 10}

    def test_log_minimal(self, db):
        entry = AuditService(db).log(action='minimal')
        assert entry.id is not None
        assert entry.user_id is None
        assert entry.target_type is None

    def test_get_paginated(self, db):
        AuditService(db).log(action='a1')
        AuditService(db).log(action='a2')
        AuditService(db).log(action='a3')
        result = AuditService(db).get_paginated(page=1, per_page=2)
        assert len(result.items) == 2
        assert result.total == 3
        assert result.pages == 2

    def test_get_paginated_filter_action(self, db):
        AuditService(db).log(action='login')
        AuditService(db).log(action='logout')
        AuditService(db).log(action='login')
        result = AuditService(db).get_paginated(page=1, per_page=10, action='login')
        assert result.total == 2

    def test_get_paginated_filter_target_type(self, db):
        AuditService(db).log(action='create', target_type='device')
        AuditService(db).log(action='create', target_type='session')
        result = AuditService(db).get_paginated(page=1, per_page=10, target_type='device')
        assert result.total == 1

    def test_get_actions(self, db):
        AuditService(db).log(action='alpha')
        AuditService(db).log(action='beta')
        AuditService(db).log(action='alpha')
        actions = AuditService(db).get_actions()
        assert 'alpha' in actions
        assert 'beta' in actions
        assert len(actions) == 2
