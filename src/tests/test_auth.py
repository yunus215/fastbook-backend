from src.auth.schemas import UserCreateModel

auth_prefix = "api/v1/auth"


def test_user_creation(test_client, fake_user_service, fake_session):
    signup_data = {
        "username": "louis12",
        "email": "louisfernando1204@gmail.com",
        "first_name": "Louis",
        "last_name": "Fernando",
        "password": "Louis.12",
    }
    response = test_client.post(f"/{auth_prefix}/signup", json=signup_data)
    user_data = UserCreateModel(**signup_data)
    assert fake_user_service.user_exists_called_once()
    assert fake_user_service.user_exists_called_once_with(
        signup_data["email"], fake_session
    )
    assert fake_user_service.create_user_called_once()
    assert fake_user_service.create_user_called_once_with(user_data, fake_session)
