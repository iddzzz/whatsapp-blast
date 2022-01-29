import math
import contact

# filter duplicate item in a list
import main


def filter_duplicate(the_list):
    new_list = []
    for item in the_list:
        if item in new_list:
            continue
        new_list.append(item)
    return new_list


# Replace item nan with -, list -> list
def replace_nan(the_list):
    new_list = []
    for item in the_list:
        try:
            if math.isnan(item):
                new_list.append('-')
            else:
                new_list.append(item)
        except Exception as why:
            print(why)
            new_list.append(item)
    return new_list


# Convert item float to int
def convert_to_int(the_list):
    new_list = []
    for item in the_list:
        try:
            if isinstance(item, float):
                new_list.append(int(item))
            else:
                new_list.append(item)
        except Exception as why:
            print(why)
            new_list.append(item)
    return new_list


# Convert 1D list to 2D partial 5 items list
def list_partition(the_list):
    final_list = []
    part_list = []
    i = 0
    for item in the_list:
        i += 1
        part_list.append(item)
        if i >= 5:
            final_list.append(part_list)
            part_list=[]
            i = 0
    if len(the_list) % 5 == 0:
        return final_list
    final_list.append(part_list)
    return final_list


def ganti_sapaan(nama, the_string, placeholder='<<sapaan>>'):
    nama = nama.split()
    if nama[0] == 'Bu':
        the_string = the_string.replace(placeholder, 'Bu')
    elif nama[0] == 'Mas':
        the_string = the_string.replace(placeholder, 'Mas')
    elif nama[0] == 'Mub':
        the_string = the_string.replace(placeholder, 'Pak')
    elif nama[0] == 'KC':
        the_string = the_string.replace(placeholder, 'Pak')
    else:
        the_string = the_string.replace(placeholder, 'Pak')
    return the_string


if __name__ == '__main__':
    pesan = main.message()
    print(ganti_sapaan('Dino har', pesan))
