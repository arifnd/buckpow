from app.services.audit_service import AuditService


class TestAuditService:

    def test_log(self, db):
        entry = AuditService.log(db, action='test.action', user_id=1, target_type='device', target_id=5, ip_address='10.0.0.1', details={'rows': 10})
        assert entry.id is not None
        assert entry.action == 'test.action'
        assert entry.user_id == 1
        assert entry.target_type == 'device'
        assert entry.target_id == 5
        assert entry.ip_address == '10.0.0.1'
        assert entry.details == {'rows': 10}

    def test_log_minimal(self, db):
        entry = AuditService.log(db, action='minimal')
        assert entry.id is not None
        assert entry.user_id is None
        assert entry.target_type is None

    def test_get_paginated(self, db):
        AuditService.log(db, action='a1')
        AuditService.log(db, action='a2')
        AuditService.log(db, action='a3')
        result = AuditService.get_paginated(db, page=1, per_page=2)
        assert len(result.items) == 2
        assert result.total == 3
        assert result.pages == 2

    def test_get_paginated_filter_action(self, db):
        AuditService.log(db, action='login')
        AuditService.log(db, action='logout')
        AuditService.log(db, action='login')
        result = AuditService.get_paginated(db, page=1, per_page=10, action='login')
        assert result.total == 2

    def test_get_paginated_filter_target_type(self, db):
        AuditService.log(db, action='create', target_type='device')
        AuditService.log(db, action='create', target_type='session')
        result = AuditService.get_paginated(db, page=1, per_page=10, target_type='device')
        assert result.total == 1

    def test_get_actions(self, db):
        AuditService.log(db, action='alpha')
        AuditService.log(db, action='beta')
        AuditService.log(db, action='alpha')
        actions = AuditService.get_actions(db)
        assert 'alpha' in actions
        assert 'beta' in actions
        assert len(actions) == 2
