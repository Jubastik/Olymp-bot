import datetime
import matplotlib as mp
import matplotlib.pyplot as plt
import os
import api_interface as api
from config import PATH_TO_PHOTOS


def new_time_format(time_obj):
    msg = ""
    if time_obj.tm_yday - 1 > 0:
        msg += str(time_obj.tm_yday - 1) + " "
        if time_obj.tm_yday - 1 in [11, 12, 13, 14]:
            msg += "дней "
        elif (time_obj.tm_yday - 1) % 10 == 1:
            msg += "день "
        elif (time_obj.tm_yday - 1) % 10 in [2, 3, 4]:
            msg += "дня "
        elif (time_obj.tm_yday - 1) % 10 in [5, 6, 7, 8, 9, 0]:
            msg += "дней "
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
    if period == 31:
        stats = api.get_stat_by_id(user_id, period * (count+1))
    else:
        stats = api.get_stat_by_id(user_id, period * count)
    print(stats)
    dates = []
    tasks = []
    times = []
    if plot_type == "task":
        end = datetime.datetime.now().date()
        start = end - datetime.timedelta(days=count*period - 1)
        for i in range(datetime.timedelta(days=count * period).days):
            print(start)
            if str(start) not in stats:
                tasks.append(0)
                dates.append(str(start))
            else:
                dates.append(str(start))
                tasks.append(stats[str(start)]["task_count"])
            start += datetime.timedelta(days=1)

        if period == 1:
            dates_output = []
            for i in dates:
                dates_output.append(i[8:10] + "-" + i[5:7])
            fig, ax = plt.subplots()  # Create a figure containing a single axes.
            ax.plot(dates_output, tasks)  # Plot some data on the axes.
            ax.set_xticklabels(dates_output,
                               rotation=-45)
            file_name = user_id
            plt.savefig(PATH_TO_PHOTOS + '{}.png'.format(file_name))
        elif period == 31:
            dates = dates[::-1]
            month = []
            month_tasks = {}
            month_tasks_output = []
            for i in dates:
                if str(i)[:7] not in month and len(month) < count:
                    month.append(str(i)[0:7])
            for i in month:
                month_tasks[i] = 0
            for i in dates:
                if str(i) in stats:
                    if str(i)[0:7] in month_tasks:
                        month_tasks[str(i)[0:7]] += stats[str(i)]["task_count"]
                    else:
                        month_tasks[str(i)[0:7]] = stats[str(i)]["task_count"]
            for i in month:
                month_tasks_output.append(month_tasks[i])
            month_output = month[::-1]
            month_tasks_output = month_tasks_output[::-1]
            fig, ax = plt.subplots()  # Create a figure containing a single axes.
            ax.plot(month_output, month_tasks_output)  # Plot some data on the axes.
            ax.set_xticklabels(labels=month_output,rotation=-30)
            file_name = user_id
            plt.savefig(PATH_TO_PHOTOS + '{}.png'.format(file_name))

    elif plot_type == "time":
        end = datetime.datetime.now().date()
        start = end - datetime.timedelta(days=count * period - 1)
        for i in range(datetime.timedelta(days=count * period).days):
            print(start)
            if str(start) not in stats:
                tasks.append(0)
                dates.append(str(start))
            else:
                dates.append(str(start))
                tasks.append(stats[str(start)]["timer_count"] / 3600)
            start += datetime.timedelta(days=1)

        if period == 1:
            dates_output = []
            for i in dates:
                dates_output.append(i[8:10] + "-" + i[5:7])
            fig, ax = plt.subplots()  # Create a figure containing a single axes.
            ax.plot(dates_output, tasks)  # Plot some data on the axes.
            ax.set_xticklabels(dates_output,
                               rotation=-45)
            file_name = user_id
            plt.savefig(PATH_TO_PHOTOS + '{}.png'.format(file_name))
        elif period == 31:
            dates = dates[::-1]
            month = []
            month_tasks = {}
            month_tasks_output = []
            for i in dates:
                if str(i)[:7] not in month and len(month) < count:
                    month.append(str(i)[0:7])
            for i in month:
                month_tasks[i] = 0
            for i in dates:
                if str(i) in stats:
                    if str(i)[0:7] in month_tasks:
                        month_tasks[str(i)[0:7]] += stats[str(i)]["timer_count"] / 3600
                    else:
                        month_tasks[str(i)[0:7]] = stats[str(i)]["timer_count"] / 3600
            for i in month:
                month_tasks_output.append(month_tasks[i])
            month_output = month[::-1]
            month_tasks_output = month_tasks_output[::-1]
            fig, ax = plt.subplots()  # Create a figure containing a single axes.
            ax.plot(month_output, month_tasks_output)  # Plot some data on the axes.
            ax.set_xticklabels(labels=month_output, rotation=-30)
            file_name = user_id
            plt.savefig(PATH_TO_PHOTOS + '{}.png'.format(file_name))
    return True

    return False


if __name__ == "__main__":
    create_plot(plot_type="task", period=1, count=1, user_id=1)
