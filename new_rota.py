import pandas as pd
import random
import calendar

# List of task columns to scan for capabilities
TASK_COLUMNS = ['Producer', 'Pro-presenter', 'Camera 1', 'Roaming', 'Live Streaming', 
                'Stage Management', 'Directing']
PRODUCER_ONLY =['Promise Ekeh', 'Seyi Adedeji']

def load_team_from_csv(file_path):
    '''
    Load team members from CSV and structure their capabilities as task-specific scores
    '''
    df = pd.read_csv(file_path)
    df=df.loc[df['NAME']!='Seye Oluwole'].reset_index(drop=True)
    df=df.loc[df['NAME'].notna()].reset_index(drop=True)
    df['NAME']=df['NAME'].str.strip()
    team = []

    for _, row in df.iterrows():
        name = row['NAME']
        task_scores = {}
        for task in TASK_COLUMNS:
            try:
                score = int(row[task])
                task_scores[task] = score
            except:
                task_scores[task] = 0  # default to 0 if missing or non-integer
        team.append({'name': name, 'task_scores': task_scores})
    
    return team




def create_rota(tasks, people):
    '''
    Assigns people to tasks per service, ensuring strong/weak pairing logic and trainee support.
    '''
    rota = {task: {'first': [], 'second': []} for task in tasks}

    for service in ['first', 'second']:
        assigned_names = set()
        available_people = people.copy()

        for task in tasks:
            service_size = 2
            if task == 'Producer':
                service_size = 1  # Only 1 person, must be strong
            elif task == 'Live Streaming':
                service_size = 2  # Prefer 2, allow 1 if not enough

            if task == 'Producer':
                # Allow anyone with ≥4 in Producer, including PRODUCER_ONLY people
                capable = [p for p in available_people if p['task_scores'].get('Producer', 0) >= 4]
            else:
                # Exclude PRODUCER_ONLY people from all other tasks
                capable = [
                    p for p in available_people
                    if p['name'] not in PRODUCER_ONLY and p['task_scores'].get(task, 0) > 0
                ]

            capable = [p for p in capable if p['name'] not in assigned_names]

            strong = [p for p in capable if p['task_scores'][task] >= 4]
            mid    = [p for p in capable if p['task_scores'][task] == 3]
            weak   = [p for p in capable if p['task_scores'][task] <= 2]

            selected = []

            # --- PRODUCER ---
            if task == 'Producer':
                if strong:
                    selected = [random.choice(strong)]
                else:
                    selected = []

            # --- LIVE STREAMING ---
            elif task == 'Live Streaming':
                if len(capable) >= 2:
                    selected = pair_people(strong, mid, weak)
                elif capable:
                    selected = [capable[0]]

            # --- ALL OTHER TASKS ---
            else:
                if len(capable) >= 2:
                    selected = pair_people(strong, mid, weak)
                elif len(capable) == 1:
                    selected = [capable[0]]

            for person in selected:
                rota[task][service].append(person['name'])
                assigned_names.add(person['name'])

            # --- Add a trainee (score = 0) ---
            if task in ['Camera 1', 'Roaming', 'Pro-presenter', 'Live Streaming']:
                trainees = [p for p in available_people if p['task_scores'].get(task, 0) == 0 and p['name'] not in assigned_names]
                if trainees:
                    trainee = random.choice(trainees)
                    rota[task][service].append(trainee['name'] + " (Trainee)")
                    assigned_names.add(trainee['name'])

            available_people = [p for p in available_people if p['name'] not in assigned_names]

    return pd.DataFrame(rota).T


def pair_people(strong, mid, weak):
    '''
    Handles pairing logic based on allowed combinations.
    '''
    random.shuffle(strong)
    random.shuffle(mid)
    random.shuffle(weak)

    # 1 strong + 1 weak
    if strong and weak:
        return [weak[0], strong[0]]
    # 1 mid + 1 weak
    elif mid and weak:
        return [weak[0], mid[0]]
    # 1 mid + 1 strong
    elif mid and strong:
        return [mid[0], strong[0]]
    # 2 mids
    elif len(mid) >= 2:
        return mid[:2]
    # 1 strong + 1 mid (fallback, less preferred)
    elif len(strong) >= 1 and len(mid) >= 1:
        return [strong[0], mid[0]]
    # if all else fails: pick any 2
    elif len(strong + mid + weak) >= 2:
        return (strong + mid + weak)[:2]
    else:
        return []

def remove_absences(absences, sunday, people):
    '''Removes people absent for each sunday from the list'''
    for date, persons in absences.items():
        if date == sunday:
            return [p for p in people if p['name'] not in persons]
    return people


def sundays_in_month(year, month):
    '''Gets dates for Sundays in the month'''
    cal = calendar.monthcalendar(year, month)
    return [week[6] for week in cal if week[6] != 0]


def create_monthly_rota(csv_file, absences, month, year, tasks=TASK_COLUMNS  ):
    '''Creates rota from CSV input'''
    months_numbers = {'January': 1, 'Jan':1, 'February': 2, 'Feb':2,
                      'March': 3, 'Mar':3, 'April': 4, 'Apr':4,
                      'May': 5, 'June': 6, 'Jun':6,
                      'July': 7, 'Jul':7, 'August': 8, 'Aug':8,
                      'September': 9, 'Sep':9, 'October': 10, 'Oct':10,
                      'November': 11, 'Nov':11, 'December': 12, 'Dec':12}

    if isinstance(month, str):
        month = month.title()
        month = months_numbers[month]

    sundays = sundays_in_month(year, month)
    media_team = load_team_from_csv(csv_file)
    monthly_rota = {}

    for sunday in sundays:
        people = remove_absences(absences, sunday, media_team)
        monthly_rota[sunday] = create_rota(tasks, people)

    monthly_rota = pd.concat(monthly_rota, axis=1)
    for col in monthly_rota.columns:
        monthly_rota[col] = monthly_rota[col].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

    return monthly_rota


# Example usage:

# file_path='Team Evaluation - LP.csv'
# absences = {
#     5: ['John Doe', 'Jane Smith'],  # Absent on 5th
#     12: ['Alice Johnson'],           # Absent on 12th
#     # Add more absences as needed
# }
# rota_df = create_monthly_rota(file_path, absences, 'Oct', 2025)

# print(rota_df)