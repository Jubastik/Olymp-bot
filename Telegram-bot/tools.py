import datetime
import matplotlib as mp
import matplotlib.pyplot as plt
import os
import api_interface as api
from config import PATH_TO_PHOTOS


def new_time_format(time_obj):
    msg = ""
    if time_obj.tm_hour > 0:
        msg += str(time_obj.tm_hour) + " "
        if time_obj.tm_hour in [11, 12, 13, 14]:
            msg += "часов "
        elif time_obj.tm_hour in [1, 21]:
            msg += "час "
        elif time_obj.tm_hour % 10 in [2, 3, 4]:
            msg += "часа "
        elif time_obj.tm_hour % 10 in [5, 6, 7, 8, 9, 0]:
            msg += "часов "
    if time_obj.tm_min > 0:
        msg += str(time_obj.tm_min) + " "
        if time_obj.tm_min in [11, 12, 13, 14]:
            msg += "минут"
        elif time_obj.tm_min in [1, 21, 31, 41, 51]:
            msg += "минуту "
        elif time_obj.tm_min % 10 in [2, 3, 4]:
            msg += "минуты "
        elif time_obj.tm_min % 10 in [5, 6, 7, 8, 9, 0]:
            msg += "минут "
    if time_obj.tm_sec > 0:
        msg += str(time_obj.tm_sec) + " "
        if time_obj.tm_sec in [11, 12, 13, 14]:
            msg += "секунд "
        elif time_obj.tm_sec in [1, 21, 31, 41, 51]:
            msg += "секунду "
        elif time_obj.tm_sec % 10 in [2, 3, 4]:
            msg += "секунды "
        elif time_obj.tm_sec % 10 in [5, 6, 7, 8, 9, 0]:
            msg += "секунд "
    if time_obj.tm_sec == 0 and time_obj.tm_hour == 0 and time_obj.tm_min == 0:
        msg += "0 секунд"
    return msg


def create_plot(plot_type="task", period=1, count=1, user_id=1):
    stats = api.get_stat_by_id(user_id, period * count)
    print(stats)
    dates = []
    tasks = []
    times = []
    if plot_type == "task":
        if period == 1:
            end = datetime.datetime.now().date()
            start = end - datetime.timedelta(days=count - 1)
            for i in range(datetime.timedelta(days=count).days):
                print(start)
                if str(start) not in stats:
                    tasks.append(0)
                    dates.append(str(start)[-5:])
                else:
                    dates.append(str(start)[-5:])
                    tasks.append(stats[str(start)]["task_count"])
                start += datetime.timedelta(days=1)
            fig, ax = plt.subplots()  # Create a figure containing a single axes.
            ax.plot(dates, tasks)  # Plot some data on the axes.
            file_name = user_id
            plt.savefig(PATH_TO_PHOTOS + '{}.png'.format(file_name))
    elif plot_type == "time":
        if period == 1:
            end = datetime.datetime.now().date()
            start = end - datetime.timedelta(days=count - 1)
            for i in range(datetime.timedelta(days=count).days):
                print(start)
                if str(start) not in stats:
                    times.append(0)
                    dates.append(str(start)[-5:])
                else:
                    dates.append(str(start)[-5:])
                    times.append(stats[str(start)]["task_count"])
                start += datetime.timedelta(days=1)
            fig, ax = plt.subplots()  # Create a figure containing a single axes.
            ax.plot(dates, times)  # Plot some data on the axes.
            file_name = user_id
            plt.savefig(PATH_TO_PHOTOS + '{}.png'.format(file_name))
    return True

    return False


if __name__ == "__main__":
    create_plot(plot_type="task", period=1, count=1, user_id=1)
