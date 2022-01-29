import pandas as pd
import contact


# Get df rekening, excel to pd df
def get_rekening(the_path, the_header=3):
    df = pd.read_excel(the_path, header=the_header)
    return df[['Nama', 'No. rekening', 'Nama Rekening', 'Nama Bank']]


# Verifikasi nama
def verify(list_one, list_two):
    final_one = []
    final_two = []
    for item in list_one:
        final_one.append(item)
        if item in list_two:
            final_two.append(item)
        else:
            final_two.append('-')
    # for item in list_two:
    #     if item in final_two:
    #         continue
    #     else:
    #         final_two.append(item)
    #         final_one.append('-')
    return final_one, final_two


if __name__ == '__main__':
    data = get_rekening()
    data = list(data['Nama'].values)
    data_two = contact.get_the_ready()
    data_two = list(data_two['CABANG'].values)

    banding_one, banding_two = verify(data_two, data)

    for i, isi in enumerate(banding_one):
        print('{} = {}'.format(isi, banding_two[i]))
    print(len(banding_one))