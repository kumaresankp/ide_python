import pytest
from unittest.mock import patch
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200


@patch('subprocess.check_output')
def test_execute_success(mock_check_output, client):
    mock_check_output.return_value = b'Hello World\n'

    response = client.post(
        '/execute',
        data={
            'language': 'python',
            'code': 'print("Hello World")'
        }
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['output'] == 'Hello World\n'


@patch('subprocess.check_output')
def test_execute_error(mock_check_output, client):
    from subprocess import CalledProcessError

    mock_check_output.side_effect = CalledProcessError(
        returncode=1,
        cmd='python',
        output=b'Traceback (most recent call last):\nError'
    )

    response = client.post(
        '/execute',
        data={
            'language': 'python',
            'code': 'print(1/0)'
        }
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'Traceback' in data['output']


@patch('os.remove')
@patch('subprocess.check_output')
def test_temp_file_cleanup(mock_check_output, mock_remove, client):
    mock_check_output.return_value = b'Success'

    response = client.post(
        '/execute',
        data={
            'language': 'python',
            'code': 'print("test")'
        }
    )

    assert response.status_code == 200
    mock_remove.assert_called_once()
