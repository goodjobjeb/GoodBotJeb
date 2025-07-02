import re

def parse_timestamp(timestamp):
    if not timestamp:
        return None, None

    def parse(time_str):
        parts = list(map(float, time_str.split(':')))
        if len(parts) == 3:
            return parts[0]*3600 + parts[1]*60 + parts[2]
        elif len(parts) == 2:
            return parts[0]*60 + parts[1]
        return float(time_str)

    if '-' in timestamp:
        start, end = timestamp.split('-', 1)
        return parse(start), parse(end)
    
    return parse(timestamp), None

def validate_timestamp_format(timestamp):
    return re.match(r'^(\d+:)?\d+:\d+(?:-\d+:\d+:\d+)?$', timestamp) is not None
