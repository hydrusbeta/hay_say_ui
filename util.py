import os
import socket


def scale_bytes(size_in_bytes):
    # Convert the given number of bytes into a more human-readable number by scaling it to kB, MB, GB, etc.
    # For example, 1234 becomes "1.21 kB"
    # size_in_bytes must be non-negative. Otherwise, behavior is undefined. The maximum scale is Zettabytes, ZB.
    scales = [(0, 'bytes'), (10, 'kB'), (20, 'MB'), (30, 'GB'), (40, 'TB'), (50, 'PB'), (60, 'EB'), (70, 'ZB')]

    scaled_to_zero_decimals = [size_in_bytes >> scale[0] for scale in scales] + [0]
    index = scaled_to_zero_decimals.index(0) - 1
    index = 0 if index < 0 else index
    scaled_to_two_decimals = "{:.2f}".format(size_in_bytes / pow(2, scales[index][0]))

    # return a different precision for bytes than for other scales
    if index == 0:
        return str(scaled_to_zero_decimals[index]) + ' ' + scales[index][1]
    return scaled_to_two_decimals + ' ' + scales[index][1]


def get_size_of_directory(path):
    # returns the sum of the sizes of all files in the specified directory. Links are not counted.
    sizes = [os.path.getsize(os.path.join(dirpath, filename)) for dirpath, dirnames, filenames in os.walk(path)
             for filename in filenames if not os.path.islink(os.path.join(dirpath, filename))]
    return sum(sizes)


def internet_available():
    # Return True if connectivity to GitHub is available. Otherwise, return False.
    # Taken from https://stackoverflow.com/questions/20913411/test-if-an-internet-connection-is-present-in-python
    try:
        host = socket.gethostbyname("github.com")
        s = socket.create_connection((host, 443), timeout=2)
        s.close()
        return True
    except Exception:
        return False