import argparse
import json
from tabulate import tabulate
from datetime import datetime


def parse_line(log_data, date=None):
	url = log_data.get('url', '')
	response_time = log_data.get('response_time', 0)
	if date:
		log_date = datetime.fromisoformat(log_data['@timestamp']).date()
		if log_date == date:
			return url, response_time
		else:
			return None, None
	else:
		return url, response_time


def get_data_report(files, date=None):
	data = {}
	for file_path in files:
		try:
			with open(file_path, 'r', encoding='utf-8') as log_file:
				for line in log_file:
					log_data = json.loads(line)
					url, response_time = parse_line(log_data, date)
					if url:
						if url in data:
							total_time, count = data[url]
							data[url] = (total_time + response_time, count + 1)
						else:
							data[url] = (response_time, 1)
		except Exception as e:
			print(f'Ошибка при чтении лог-файла {file_path}: {e}')
	return data


def main():
	parser = argparse.ArgumentParser(description='Парсер логов')
	parser.add_argument(
		'--file',
		required=True,
		nargs='+',
		help='Пути к лог-файлам (можно несколько)'
	)
	parser.add_argument('--report', required=True, help='Тип отчета')
	parser.add_argument('--date', help='Дата в формате YYYY-MM-DD')
	args = parser.parse_args()

	if args.report == 'average':
		date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else None
		data = get_data_report(args.file, date)
		table = [('', 'handler', 'total', 'avg_response_time')]
		for url, (total_time, count) in data.items():
			table.append((url, count, round(total_time / count, 3)))
		print(tabulate(table, headers='firstrow'))
	else:
		print('Неверный тип отчета')


if __name__ == '__main__':
	main()
