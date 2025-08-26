import csv
from collections import defaultdict
import argparse

SHIFT_CYCLE = ['D', 'N', 'O', 'O']


def read_employees(path):
    """Read input CSV and return days list and team->list of employees."""
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        if len(header) < 3:
            raise ValueError("CSV must contain TEAM, Full Name and at least one day column")
        days = header[2:]
        teams = defaultdict(list)
        for row in reader:
            if not row:
                continue
            team = row[0].strip()
            name = row[1].strip()
            teams[team].append({'name': name, 'schedule': [''] * len(days),
                                'total': 0, 'nights': 0})
    return days, teams


def generate_schedule(days, teams, start_offset=0):
    team_names = sorted(teams.keys())
    for team_idx, team in enumerate(team_names):
        offset = (start_offset + team_idx) % len(SHIFT_CYCLE)
        for day_idx in range(len(days)):
            shift = SHIFT_CYCLE[(offset + day_idx) % len(SHIFT_CYCLE)]
            team_members = teams[team]
            # Check whether every member can take this shift
            valid = True
            if shift in ('D', 'N'):
                for emp in team_members:
                    if emp['total'] >= 15:
                        valid = False
                        break
                    if shift == 'N':
                        if emp['nights'] >= 4 or '[D]' in emp['name']:
                            valid = False
                            break
            if not valid:
                shift = 'O'
            # Apply shift to all team members
            for emp in team_members:
                emp['schedule'][day_idx] = shift
                if shift in ('D', 'N'):
                    emp['total'] += 1
                    if shift == 'N':
                        emp['nights'] += 1
    return teams


def write_schedule(path, days, teams):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['TEAM', 'Full Name', *days])
        for team in sorted(teams.keys()):
            for emp in teams[team]:
                writer.writerow([team, emp['name'], *emp['schedule']])


def main():
    parser = argparse.ArgumentParser(description='Team-based monthly schedule generator')
    parser.add_argument('input_csv', help='Input CSV file path')
    parser.add_argument('output_csv', help='Output CSV file path')
    parser.add_argument('--start-offset', type=int, default=0, help='Cycle offset for first team (0-3)')
    args = parser.parse_args()

    days, teams = read_employees(args.input_csv)
    generate_schedule(days, teams, start_offset=args.start_offset)
    write_schedule(args.output_csv, days, teams)


if __name__ == '__main__':
    main()
