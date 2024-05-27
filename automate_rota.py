'''
This python script automate team monthly rota creation

Author: Promise Ekeh
Date: March 20, 2024

Future Development:
    Incorporate learning path/plan
    create third service for a particular sunday (might change structure a bit, include num_service as parameter
                                                    to create_rota and include conditional statement to
                                                    create_monthly_rota)
''' 

import pandas as pd
import random
import calendar


def create_rota(tasks, people):
    ''' 
    Randomly assigns people to different task for two services per day.
    it ensures that no name appears twice per service

    Parameters: 
        tasks (list): List of tasks rquired for each service
        people(list): diction of team members and their capabilities)

    Returns:
        DataFrame: of people randomly assigned to different tasks for two services for a day.  
    '''
    rota = {task: {'first': [], 'second': []} for task in tasks}  # this rota accounts for 2 services
    
    for service in ['first', 'second']:
        Service_size = 2 # this ensure maximun of 2 people per task

        assigned_people= list()
        people_available_for_service= [person['name'] for person in people]
        
        for task in tasks:
            people_available_for_task=list()
            if task== 'Producer' or task=='Live-streaming': Service_size=1 #ensures we have 1 producer per service

            for person_ in people_available_for_service:
                person_index= None
                for i, person in enumerate(people):
                    if person['name'] == person_: #get index of person index
                        person_index = i
                        break
                                
                person = people[person_index]
                if task in person['capabilities']:
                    people_available_for_task.append(person['name'])

            if len(people_available_for_task) >1:
                # random_name = random.choice(people_available_for_task)
                random_name=random.sample(people_available_for_task, Service_size) # randomly select service size
                for name in random_name:
                    rota[task][service].append(name)
                    assigned_people.append(name)
                    people_available_for_service.remove(name)
                    people_available_for_task.remove(name)
            elif len(people_available_for_task) ==1:
                name=people_available_for_task[0]
                rota[task][service].append(name)
                assigned_people.append(name)
                people_available_for_service.remove(name)
                people_available_for_task.remove(name)
    return pd.DataFrame(rota).T

def remove_absences (absences, sunday, people):
    '''
    Removes people absent for each sunday from the list
    Parameters:
        absences (dict): dictionary of absences for the month
        sunday (int): date (day)
        people (list): List of people (media team)
            
    '''
    for date, persons in absences.items():
        if date==sunday:
            for person_ in persons:
                for i, person in enumerate(people):
                    if person['name'] == person_:
                        people.pop(i)


def sundays_in_month(year, month):
    '''
    Gets the dates for sundays in the month 

    Parameters:
        year (int): year
        month (int): value of year
    Returns:
      list: a list of sundays in a month'''
    cal = calendar.monthcalendar(year, month)
    sundays = [week[6] for week in cal if week[6] != 0]
    return sundays

def create_monthly_rota (media_team, tasks, absences, month, year):
    ''' 
    Aggregates the above functions to create monthly rota

    Parameters:
        media_team (list): List of dictionary of the team and their capabilities
        tasks (list): List of the tasks required
        absences (dict): dictionary of team absences for the month
        month (int, str): 
        year (int)
    Returns:
        Rota for the month
    '''
    months_numbers = {'January': 1, 'February': 2, 'March': 3, 'April': 4,
                      'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
    if isinstance(month, str):
        ''' 
        converts months given as string to integer
        '''
        month=month.title()
        month=months_numbers[month]
    sundays = sundays_in_month(year, month)
    monthly_rota= {}
    for sunday in sundays:

        people=media_team.copy()
        if remove_absences(absences, sunday, people):
            people= remove_absences(absences, sunday, people)


        monthly_rota[sunday]=create_rota(tasks, people)
    return pd.concat(monthly_rota, axis=1)

# Example data
tasks = ['Camera 1', 'Roaming','Pro-presenter',  'Directing', 'Live-streaming', 'Stage Management', 'Producer']
media_team = [
    {'name': 'TJ', 'capabilities': ['Pro-presenter', 'Camera 1', 'Live-streaming']},
    {'name': 'David', 'capabilities': ['Pro-presenter', 'Camera 1', 'Roaming', 'Live-streaming']},
    {'name': 'Tolu', 'capabilities': ['Camera 1', 'Roaming', 'Directing', 'Live-streaming', 'Stage Management']},
    {'name': 'Olayinka', 'capabilities': ['Pro-presenter', 'Live-streaming']},
    {'name': 'Ore', 'capabilities': ['Pro-presenter', 'Roaming', 'Live-streaming']},
    {'name': 'Juwon', 'capabilities': ['Pro-presenter', 'Camera 1', 'Roaming']},
    {'name': 'Joseph', 'capabilities': ['Pro-presenter', 'Camera 1']},
    {'name': 'Priscilia', 'capabilities': ['Live-streaming',  'Pro-presenter', 'Stage Management']},
    {'name': 'Soji', 'capabilities': ['Stage Management', 'Directing', 'Live-streaming']},
    {'name': 'Lady T', 'capabilities': ['Stage Management','Pro-presenter',   'Live-streaming', 'Camera 1']},
    {'name': 'Bisi', 'capabilities': ['Stage Management']},
    {'name': 'Tobi', 'capabilities': ['Stage Management', 'Pro-presenter', 'Roaming', 'Directing', 'Camera 1']},
    {'name': 'Promise', 'capabilities': ['Producer']},
    {'name': 'Seyi', 'capabilities': ['Producer']},
    {'name': 'Seye', 'capabilities': ['Producer']},
    {'name': 'Kenny', 'capabilities': ['Stage Management', 'Roaming', 'Directing', ]},
    {'name': 'Tunde', 'capabilities': ['Directing', 'Camera 1', 'Roaming', 'Live-streaming']},
    {'name': 'Michael O.', 'capabilities': ['Directing', 'Live-streaming']}
]

# Example absences
april_absences={21: ['Tolu'],
          28: ['Joseph', 'David']}
april_rota=create_monthly_rota (media_team, tasks, april_absences, 'April', 2024)