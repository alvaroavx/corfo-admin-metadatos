import requests

class DSpaceClient:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.csrf_token = None
        self.auth_token = None

    def get_csrf_token(self):
        response = requests.get(f"{self.base_url}/server/api")
        if response.status_code == 200:
            self.csrf_token = response.headers.get("DSPACE-CSRF-TOKEN")
            return self.csrf_token
        else:
            raise Exception("Error obteniendo el token CSRF: " + response.text)

    def login(self):
        if not self.csrf_token:
            self.get_csrf_token()

        headers = {
            "Content-Type": "application/json",
            "X-CSRF-TOKEN": self.csrf_token,
        }
        data = {
            "email": self.email,
            "password": self.password,
        }
        response = requests.post(f"{self.base_url}/server/api/authn/login", json=data, headers=headers)

        if response.status_code == 200:
            self.auth_token = response.headers.get("Authorization")
            return self.auth_token
        else:
            raise Exception("Error al autenticar: " + response.text)

    def get(self, endpoint):
        headers = {"Authorization": self.auth_token}
        response = requests.get(f"{self.base_url}/{endpoint}", headers=headers)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data):
        headers = {
            "Authorization": self.auth_token,
            "Content-Type": "application/json",
        }
        response = requests.post(f"{self.base_url}/{endpoint}", json=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def logout(self):
        headers = {"Authorization": self.auth_token}
        response = requests.post(f"{self.base_url}/server/api/authn/logout", headers=headers)
        if response.status_code != 200:
            raise Exception("Error al cerrar sesión: " + response.text)
