def new_time_format(time_obj):
    msg = ""
    if time_obj.tm_hour > 0:
        msg += str(time_obj.tm_hour) + " "
        if time_obj.tm_hour in [1,21]:
            msg += "час "
        elif time_obj.tm_hour % 10 in [2,3,4]:
            msg += "часа "
        elif time_obj.tm_hour % 10 in [5,6,7,8,9,0] or time_obj.tm_hour == 11:
            msg += "часов "
    if time_obj.tm_min > 0:
        msg += str(time_obj.tm_min) + " "
        if time_obj.tm_min in [1, 21,31,41,51]:
            msg += "минуту "
        elif time_obj.tm_min % 10 in [2, 3, 4]:
            msg += "минуты "
        elif time_obj.tm_min % 10 in [5, 6, 7, 8, 9, 0] or time_obj.tm_min == 11:
            msg += "минут "
    if time_obj.tm_sec > 0:
        msg += str(time_obj.tm_sec) + " "
        if time_obj.tm_sec in [1, 21,31,41,51]:
            msg += "секунду "
        elif time_obj.tm_sec % 10 in [2, 3, 4]:
            msg += "секунды "
        elif time_obj.tm_sec % 10 in [5, 6, 7, 8, 9, 0] or time_obj.tm_sec == 11:
            msg += "секунд "
    if time_obj.tm_sec == 0 and time_obj.tm_hour == 0 and time_obj.tm_min == 0:
        msg += "0 секунд"
    return msg
