import re
import unittest
from app import create_app, db
from app.models import User, Role


class FlaskClientTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    def test_register_and_login(self):
        # 注册新用户
        response = self.client.post('/auth/register', data={
            'email': 'faiz_xie@163.com',
            'username': 'xxz163',
            'password': 'zxc12366',
            'password2': 'zxc12366'
        })
        self.assertEqual(response.status_code, 302)

        # 用新账号登陆
        response = self.client.post('/auth/login', data={
            'email': 'faiz_xie@163.com',
            'password': 'zxc12366'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search('Hello,\s+xxz163!',
                                  response.get_data(as_text=True)))
        self.assertTrue('You have not confirmed your account yet' in response.get_data(
            as_text=True))

        # 发送确认令牌
        user = User.query.filter_by(email='faiz_xie@163.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(f'/auth/confirm/{token}', follow_redirects=True)
        user.confirm(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('You have confirmed your account' in response.get_data(
            as_text=True
        ))

        # 退出
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('You have been logged out' in response.get_data(
            as_text=True
        ))

