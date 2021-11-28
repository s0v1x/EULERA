import random

def rand_agent(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)


def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "%.2f%s" % (num, ["", "K", "M", "G", "T", "P"][magnitude])

def str_time(intrv):
    intrv = intrv.total_seconds()
    hours = intrv // 3600
    minutes = (intrv % 3600) // 60
    if hours == 1:
        if minutes > 1:
            return str(int(hours)) + " hour " + str(int(minutes)) + " minutes"
        elif minutes == 1:
            return str(int(hours)) + " hour " + str(int(minutes)) + " minute"
        else:
            return str(int(hours)) + " hour "
    elif hours == 2:
        if minutes > 1:
            return str(int(hours)) + " hours " + str(int(minutes)) + " minutes"
        elif minutes == 1:
            return str(int(hours)) + " hours " + str(int(minutes)) + " minute"
        else:
            return str(int(hours)) + " hours "
    else:
        if minutes > 1:
            return str(int(minutes)) + " minutes"
        else:
            return str(int(minutes)) + " minute"