class TestProjectsAPI:
    def test_create_project(self, client):
        resp = client.post('/api/v1/projects', json={'name': 'New Project', 'description': 'Desc'})
        assert resp.status_code == 201
        data = resp.json()
        assert data['name'] == 'New Project'
        assert data['description'] == 'Desc'

    def test_create_project_no_name(self, client):
        resp = client.post('/api/v1/projects', json={'description': 'No name'})
        assert resp.status_code == 422

    def test_list_projects(self, client):
        client.post('/api/v1/projects', json={'name': 'Project A'})
        client.post('/api/v1/projects', json={'name': 'Project B'})
        resp = client.get('/api/v1/projects')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] >= 2
        assert len(data['projects']) >= 2

    def test_list_projects_unauthorized(self, unauth_client):
        resp = unauth_client.get('/api/v1/projects')
        assert resp.status_code == 401

    def test_get_project(self, client):
        created = client.post('/api/v1/projects', json={'name': 'Get Me'}).json()
        resp = client.get(f'/api/v1/projects/{created["id"]}')
        assert resp.status_code == 200
        assert resp.json()['name'] == 'Get Me'

    def test_get_project_not_found(self, client):
        resp = client.get('/api/v1/projects/99999')
        assert resp.status_code == 404

    def test_update_project(self, client):
        created = client.post('/api/v1/projects', json={'name': 'Old'}).json()
        resp = client.put(f'/api/v1/projects/{created["id"]}', json={'name': 'New'})
        assert resp.status_code == 200
        assert resp.json()['name'] == 'New'

    def test_update_project_not_found(self, client):
        resp = client.put('/api/v1/projects/99999', json={'name': 'Ghost'})
        assert resp.status_code == 404

    def test_update_project_no_json(self, client):
        created = client.post('/api/v1/projects', json={'name': 'No JSON'}).json()
        resp = client.put(f'/api/v1/projects/{created["id"]}', content=b'{}')
        assert resp.status_code == 422

    def test_delete_project(self, client):
        created = client.post('/api/v1/projects', json={'name': 'Delete Me'}).json()
        resp = client.delete(f'/api/v1/projects/{created["id"]}')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'deleted'

    def test_delete_project_not_found(self, client):
        resp = client.delete('/api/v1/projects/99999')
        assert resp.status_code == 404

    def test_list_page_zero(self, client, app):
        from sqlalchemy import insert
        from app.database import SessionLocal
        from app.models import Project
        db = SessionLocal()
        db.execute(insert(Project), [{'name': f'Project {i}'} for i in range(3)])
        db.commit()
        db.close()
        resp = client.get('/api/v1/projects?page=0')
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    def test_pagination(self, client, app):
        from sqlalchemy import insert
        from app.database import SessionLocal
        from app.models import Project
        db = SessionLocal()
        db.execute(insert(Project), [{'name': f'Pagination {i}'} for i in range(15)])
        db.commit()
        db.close()
        resp = client.get('/api/v1/projects?page=1&per_page=5')
        assert resp.status_code == 200
        data = resp.json()
        assert data['pages'] == 3
