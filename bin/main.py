import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

# config
power_consumed_per_day = 35
length_of_autonomy = 1
avg_usage_per_hour = power_consumed_per_day / 24
min_soh = 0.8
# calculations

# weighting ratio
# power rating - capacity rating - cost rating - warranty rating 
weighting = [3,3.0,3.5,0.5]

def cost_rating (total_cost,lifetime):
    return total_cost / lifetime

def capacity_rating (quantity,capacity,dod,rte,power_consumed_per_day,length_of_autonomy):
    return (quantity * capacity * dod * rte) / (power_consumed_per_day * length_of_autonomy)

def warranty_rating (warranty_length,lifetime):
    return (float)(warranty_length / lifetime)

def power_rating (continuous_rating,instantaneous_rating,avg_usage_per_hour):
    res = (continuous_rating * 59 + instantaneous_rating) / 60
    return res * avg_usage_per_hour

def normalized_rating (power_rating,capacity_rating,cost_rating,warranty_rating):
    res = power_rating / 6 * weighting[0] + capacity_rating * weighting[1] + weighting[2] * (1 - (cost_rating / 1000) / 100) + weighting[3] * warranty_rating
    return res / 10

def battery_quantity (power_consumed_per_day,length_of_autonomy,capacity,dod,rte):
    res = round((length_of_autonomy * power_consumed_per_day) / (capacity * dod * rte * min_soh))
    return res

def lifetime(power_consumed_per_day,length_of_autonomy,quantity,capacity,dod,rte,warranty_length,warranty_soh,warranty_cycle):
    soh = (length_of_autonomy * power_consumed_per_day) / (quantity * capacity * dod * rte)
    rate = (1 - warranty_soh) / (365 * warranty_length)
    expected_cycle = (1 - soh) / rate
    return min(warranty_cycle,expected_cycle) / 365
class battery:
    def __init__(self):
        # input data
        self.name = "ok"
    def process(self):
        self.quantity = battery_quantity(self.power_consumed_per_day,self.length_of_autonomy,self.capacity,self.dod,self.rte)
        self.lifetime = lifetime(self.power_consumed_per_day,self.length_of_autonomy,self.quantity,self.capacity,self.dod,self.rte,self.warranty_length,self.warranty_soh,self.warranty_cycle)
        self.cost_rating = cost_rating(self.cost * self.quantity,self.lifetime)
        self.warranty_rating = warranty_rating(self.warranty_length,self.lifetime)
        self.capacity_rating = capacity_rating(self.quantity,self.capacity,self.dod,self.rte,self.power_consumed_per_day,self.length_of_autonomy)
        self.power_rating = power_rating(self.continuous_rating,self.instantaneous_rating,self.avg_usage_per_hour)
        self.normalized_rating = normalized_rating(self.power_rating,self.capacity_rating,self.cost_rating,self.warranty_rating)
        return

battery_list = []
datas = pd.read_csv(r"BATTERY_DATASET.csv")
datas = datas.values

for row in datas:
    temp = battery()
    temp.name = row[0]
    temp.capacity = row[1]
    temp.dod = row[2]
    temp.rte = row[3]
    temp.warranty_length = row[4]
    temp.warranty_soh = row[5]
    temp.cost = row[6]
    temp.continuous_rating = row[7]
    temp.instantaneous_rating = row[8]
    temp.warranty_cycle = row[9]
    temp.power_consumed_per_day = power_consumed_per_day
    temp.length_of_autonomy = length_of_autonomy
    temp.avg_usage_per_hour = avg_usage_per_hour
    temp.process()
    battery_list.append(temp)

battery_list.sort(key = lambda x : x.normalized_rating,reverse = True)
rating_list = []
for model in battery_list:
    data = []
    data.append(model.name)
    data.append(round(model.normalized_rating,4))
    data.append(model.cost_rating)
    rating_list.append(data)

# generating rating list - csv
columns = ['Battery Model','Normalized Rating','Average Yearly Cost']
result = pd.DataFrame(rating_list,columns = columns)
result.to_csv(r"result.csv",index = False)

# plotting stuffs

# take battery models into consideration
def rating_bar() :
    x_label = []
    y_label = []
    for model in rating_list:
        x_label.append(model[0])
        y_label.append(model[1])
    plt.barh(x_label,y_label)
    plt.show()

rating_bar()