import argparse
import json
from tabulate import tabulate


def get_average_report(files):
	data = {}
	for file_path in files:
		try:
			with open(file_path, 'r', encoding='utf-8') as log_file:
				for line in log_file:
					log_data = json.loads(line)
					url = log_data.get('url', '')
					response_time = log_data.get('response_time', 0)
					if url and response_time:
						if url in data:
							total_time, count = data[url]
							data[url] = (total_time + response_time, count + 1)
						else:
							data[url] = (response_time, 1)
		except Exception as e:
			print(f"Ошибка при чтении лог-файла {file_path}: {e}")
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
	args = parser.parse_args()

	if args.report == 'average':
		data = get_average_report(args.file)
		table = [('', 'handler', 'total', 'avg_response_time')]
		for url, (total_time, count) in data.items():
			table.append((url, count, round(total_time / count, 3)))
		print(tabulate(table, headers='firstrow'))
	else:
		print('Неверный тип отчета')


if __name__ == "__main__":
	main()
