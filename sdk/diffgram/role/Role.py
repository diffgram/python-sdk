from diffgram.core.directory import Directory


class Role:
    id: int
    name: int
    project_id: int
    permissions_list: list

    def __init__(self,
                 client,
                 role_dict = None):

        self.client = client

        if self.client.project_string_id is None:
            raise Exception("\n No project string id in client.")

        self.refresh_from_dict(
            role_dict = role_dict)

    def refresh_from_dict(self, role_dict: dict = None):

        if not role_dict:
            return

        for key, value in role_dict.items():
            setattr(self, key, value)

    def __repr__(self):
        return f'Role<{str(self.serialize())}>'

    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'permissions_list': self.permissions_list,
        }

    def new(self, name: str = None) -> 'Role':
        """
            Creates a new Role
        :param name:
        :return:
        """
        endpoint = "/api/v1/project/{}/roles/new".format(self.client.project_string_id)

        response = self.client.session.post(
            self.client.host + endpoint,
            json = {'name': name})

        self.client.handle_errors(response)

        data = response.json()
        role = Role(client = self.client, role_dict = data)
        return role

    def delete(self) -> 'Role':
        """
            Creates a new Role
        :param name:
        :return:
        """
        if not self.id:
            raise Exception('Role has no ID. Cannot be deleted.')

        endpoint = f"/api/v1/project/{self.client.project_string_id}/roles/{self.id}/delete"

        response = self.client.session.delete(
            self.client.host + endpoint, json = {})

        self.client.handle_errors(response)

        data = response.json()
        role = Role(client = self.client, role_dict = data)
        return role

    def add_permission(self, perm: str, object_type: str):
        endpoint = f"/api/v1/project/{self.client.project_string_id}/roles/{self.id}/add-perm"

        response = self.client.session.patch(
            self.client.host + endpoint, json = {
                'permission': perm,
                'object_type': object_type,
            })

        self.client.handle_errors(response)

        data = response.json()
        role = Role(client = self.client, role_dict = data)
        self.permissions_list = role.permissions_list
        return role

    def list(self) -> list:

        endpoint = f"/api/v1/project/{self.client.project_string_id}/roles"

        response = self.client.session.get(self.client.host + endpoint)

        self.client.handle_errors(response)
        roles = response.json()
        result = []
        for r in roles:
            role_obj = Role(client = self.client, role_dict = r)
            result.append(role_obj)
        return result
