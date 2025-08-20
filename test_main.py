import json
import os
import sys
import tempfile
from main import main, get_data_report


def create_log_file(logs):
    '''
    Создает временный лог-файл с заданными записями.
    '''
    fd, path = tempfile.mkstemp(suffix='.log')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        for log in logs:
            f.write(json.dumps(log) + '\n')
    return path


def test_single_file(capsys):
    logs = [
        {'url': '/want/to/join', 'response_time': 100},
        {'url': '/your/company', 'response_time': 200},
        {'url': '/your/company', 'response_time': 300}
    ]
    log_path = create_log_file(logs)
    sys.argv = ['main.py', '--file', log_path, '--report', 'average']
    main()
    captured = capsys.readouterr()
    assert '/want/to/join' in captured.out
    assert '/your/company' in captured.out
    os.remove(log_path)


def test_multiple_files(monkeypatch, capsys):
    logs1 = [
        {'url': '/want/to/join', 'response_time': 100}
    ]
    logs2 = [
        {'url': '/your/company', 'response_time': 200},
        {'url': '/your/company', 'response_time': 300}
    ]
    log_path1 = create_log_file(logs1)
    log_path2 = create_log_file(logs2)
    sys.argv = [
        'main.py',
        '--file',
        log_path1,
        log_path2,
        '--report',
        'average'
    ]
    main()
    captured = capsys.readouterr()
    assert '/want/to/join' in captured.out
    assert '/your/company' in captured.out
    os.remove(log_path1)
    os.remove(log_path2)


def test_invalid_json(capsys):
    fd, path = tempfile.mkstemp(suffix='.log')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write('{invalid json}\n')
    sys.argv = ['main.py', '--file', path, '--report', 'average']
    main()
    captured = capsys.readouterr()
    assert 'Ошибка при чтении лог-файла' in captured.out
    os.remove(path)


def test_invalid_report(capsys):
    sys.argv = ['main.py', '--file', 'anyfile.log', '--report', 'invalid']
    main()
    captured = capsys.readouterr()
    assert 'Неверный тип отчета' in captured.out


def test_valid_data():
    logs = [
        {'url': '/want/to/join', 'response_time': 100},
        {'url': '/your/company', 'response_time': 200},
        {'url': '/your/company', 'response_time': 300}
    ]
    log_path = create_log_file(logs)
    data = get_data_report([log_path])
    assert data == {
        '/want/to/join': (100, 1),
        '/your/company': (500, 2)
    }
    os.remove(log_path)
