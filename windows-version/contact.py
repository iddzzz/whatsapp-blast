import pandas as pd
import numpy as np
import math
import utils


# list kontak ke google contact siap upload
def ready_contact(nama_nama, nomors, file_csv='google-contact-ready.csv'):
    df_reference = pd.read_csv('reference.csv')
    header_contact = list(df_reference.columns.values)
    new_contact = np.empty([len(nama_nama), len(header_contact)])
    new_contact[:] = np.NaN
    new_contact = pd.DataFrame(new_contact, columns=header_contact)
    new_contact['Name'] = nama_nama
    new_contact['Phone 1 - Type'] = 'Mobile'
    new_contact['Phone 1 - Value'] = nomors
    pd.DataFrame.to_csv(new_contact, file_csv, index=False)


# filter kontak nama KC, NaN dan 0 dihapus, output : pandas dataframe
def filter_kc(file_excel='blast.xlsx', kolom_kc='KC'):
    df = pd.read_excel(file_excel)
    return df[[type(item) == str for item in df[kolom_kc]]]


# ganti dan ngambil nama & kontak menjadi list
def ganti_ambil_kc(df, kolom_nama='KC', kolom_nomor='NO KC', kolom_code='KODE', kolom_cabang='CABANG'):
    nama_nama = list(df[kolom_nama].values)
    nomor = list(df[kolom_nomor].values)
    kode = [int(item) for item in list(df[kolom_code].values)]
    cabang = list(df[kolom_cabang].values)
    for i, item in enumerate(nama_nama):
        nama_nama[i] = 'KC {} {} {}'.format(kode[i], item, cabang[i])
    return nama_nama, nomor


# ganti dan ngambil nama & kontak menjadi list
def ganti_ambil_mb(df, kolom_nama='mb', kolom_nomor='NO mb'):
    nama_nama = list(df[kolom_nama].values)
    nomor = list(df[kolom_nomor].values)
    for i, item in enumerate(nama_nama):
        nama_nama[i] = 'mb {}'.format(item)
    return nama_nama, nomor


# ambil nama-nama target, excel -> pandas DataFrame
def ambil_kontak(path_excel="blast.xlsx"):
    df = pd.read_excel(path_excel)
    return df[:][:-1]


# Filter based on value > cutoff, pd df -> pd df
def filter_cutoff(dataframe, kolom_filter, cutoff=0.0):
    # filterring nan value
    df = dataframe[[True != math.isnan(value) for value in dataframe[kolom_filter]]]
    df = df[[value > cutoff for value in df[kolom_filter]]]
    return df


# filter non-absolut, in/out-side alternative, df -> df, df
def filter_absolute(dataframe, kolom_filter='ALT'):
    df_outer = dataframe[[type(value) == float for value in dataframe[kolom_filter]]]
    df_inner = dataframe[[type(value) == str for value in dataframe[kolom_filter]]]
    return df_outer, df_inner


# ganti nama ALT, pd df -> list
def ganti_ambil_alt(dataframe, kolom_nama='ALT', kolom_cabang='CABANG'):
    nama_nama = list(dataframe[kolom_nama].values)
    cabang = list(dataframe[kolom_cabang].values)
    for i, name in enumerate(nama_nama):
        nama_nama[i] = "{} {}".format(name, cabang[i])
    return nama_nama


# Ambil data based on key column (like vlookup), list -> list
def vlookup(dataframe, key_list, kolom_key, kolom_ambil):
    result = []
    for item in key_list:
        df = dataframe[[value == item for value in dataframe[kolom_key]]]
        the_data = df[kolom_ambil].values
        if math.isnan(the_data):
            result.append('-')
        result.append(the_data)
    return result


# Ambil data rekening, df -> list, list, list, list
def ambil_data_rekening(dataframe, kolom_satu='CABANG', kolom_dua='NO REK',
                        kolom_tiga='NAMA REK', kolom_empat='BANK'):
    satu = list(dataframe[kolom_satu].values)
    dua = list(dataframe[kolom_dua].values)
    dua = utils.convert_to_int(utils.replace_nan(dua))
    tiga = utils.replace_nan(list(dataframe[kolom_tiga].values))
    empat = utils.replace_nan(list(dataframe[kolom_empat].values))
    return satu, dua, tiga, empat


def generating_for_blast():
    new = ambil_kontak("blast.xlsx")
    new = filter_cutoff(new, 'EST')
    mb_based = filter_cutoff(new, 'mb WA')
    kc_based = filter_cutoff(new, 'KC WA')

    mb_outer, mb_inner = filter_absolute(mb_based)
    kc_outer, kc_inner = filter_absolute(kc_based)

    names_mb, _ = ganti_ambil_mb(mb_outer)
    names_kc, _ = ganti_ambil_kc(kc_outer)
    alt_mb = ganti_ambil_alt(mb_inner)
    alt_kc = ganti_ambil_alt(kc_inner)

    new = names_mb + names_kc + alt_mb + alt_kc

    return utils.filter_duplicate(new)


def generating_for_blast_rekening():
    new = ambil_kontak("blast.xlsx") # pd df
    new = filter_cutoff(new, 'EST') # pd df
    new = filter_cutoff(new, 'SDH DFTR') # pd df
    mb_based = filter_cutoff(new, 'mb WA') # pd df
    kc_based = filter_cutoff(new, 'KC WA') # pd df

    mb_outer, mb_inner = filter_absolute(mb_based) # pd df
    kc_outer, kc_inner = filter_absolute(kc_based) # pd df

    names_mb, _ = ganti_ambil_mb(mb_outer)
    cab_mb, rek_mb, nama_rek_mb, bank_mb = ambil_data_rekening(mb_outer)

    names_kc, _ = ganti_ambil_kc(kc_outer)
    cab_kc, rek_kc, nama_rek_kc, bank_kc = ambil_data_rekening(kc_outer)

    alt_mb = ganti_ambil_alt(mb_inner)
    cab_alt_mb, rek_alt_mb, nama_rek_alt_mb, bank_alt_mb = ambil_data_rekening(mb_inner)

    alt_kc = ganti_ambil_alt(kc_inner)
    cab_alt_kc, rek_alt_kc, nama_rek_alt_kc, bank_alt_kc = ambil_data_rekening(kc_inner)

    new = names_mb + names_kc + alt_mb + alt_kc
    cabangs = cab_mb + cab_kc + cab_alt_mb + cab_alt_kc
    rekenings = rek_mb + rek_kc + rek_alt_mb + rek_alt_kc
    rek_names = nama_rek_mb + nama_rek_kc + nama_rek_alt_mb + nama_rek_alt_kc
    banks = bank_mb + bank_kc + bank_alt_mb + bank_alt_kc

    return new, cabangs, rekenings, rek_names, banks


def generating_for_blast_rekening_terkirim():
    new = ambil_kontak("blast.xlsx")  # pd df
    new = filter_cutoff(new, 'NOMINAL')  # pd df
    # new = filter_cutoff(new, 'SDH DFTR')  # pd df
    mb_based = filter_cutoff(new, 'mb WA')  # pd df
    kc_based = filter_cutoff(new, 'KC WA')  # pd df

    mb_outer, mb_inner = filter_absolute(mb_based)  # pd df
    kc_outer, kc_inner = filter_absolute(kc_based)  # pd df

    names_mb, _ = ganti_ambil_mb(mb_outer)
    cab_mb, nominal_mb, nama_rek_mb, bank_mb =\
        ambil_data_rekening(mb_outer, 'CABANG', 'NOMINAL', 'KE AN', 'KE BANK')

    names_kc, _ = ganti_ambil_kc(kc_outer)
    cab_kc, nominal_kc, nama_rek_kc, bank_kc =\
        ambil_data_rekening(kc_outer, 'CABANG', 'NOMINAL', 'KE AN', 'KE BANK')

    alt_mb = ganti_ambil_alt(mb_inner)
    cab_alt_mb, nominal_alt_mb, nama_rek_alt_mb, bank_alt_mb =\
        ambil_data_rekening(mb_inner, 'CABANG', 'NOMINAL', 'KE AN', 'KE BANK')

    alt_kc = ganti_ambil_alt(kc_inner)
    cab_alt_kc, nominal_alt_kc, nama_rek_alt_kc, bank_alt_kc =\
        ambil_data_rekening(kc_inner, 'CABANG', 'NOMINAL', 'KE AN', 'KE BANK')

    new = names_mb + names_kc + alt_mb + alt_kc
    cabangs = cab_mb + cab_kc + cab_alt_mb + cab_alt_kc
    nominals = nominal_mb + nominal_kc + nominal_alt_mb + nominal_alt_kc
    rek_names = nama_rek_mb + nama_rek_kc + nama_rek_alt_mb + nama_rek_alt_kc
    banks = bank_mb + bank_kc + bank_alt_mb + bank_alt_kc

    return new, cabangs, nominals, rek_names, banks


def generating_custom(file_excel="blast.xlsx",
                      cutoff_1='EST', kolom_1='CABANG', kolom_2='NOMINAL', kolom_3='KE AN', kolom_4='KE BANK'):
    new = ambil_kontak(file_excel)  # pd df
    new = filter_cutoff(new, cutoff_1)  # pd df
    # new = filter_cutoff(new, 'SDH DFTR')  # pd df
    mb_based = filter_cutoff(new, 'mb WA')  # pd df
    kc_based = filter_cutoff(new, 'KC WA')  # pd df

    mb_outer, mb_inner = filter_absolute(mb_based)  # pd df
    kc_outer, kc_inner = filter_absolute(kc_based)  # pd df

    names_mb, _ = ganti_ambil_mb(mb_outer)
    satu_mb, dua_mb, tiga_mb, empat_mb =\
        ambil_data_rekening(mb_outer, kolom_1, kolom_2, kolom_3, kolom_4)

    names_kc, _ = ganti_ambil_kc(kc_outer)
    satu_kc, dua_kc, tiga_kc, empat_kc =\
        ambil_data_rekening(kc_outer, kolom_1, kolom_2, kolom_3, kolom_4)

    alt_mb = ganti_ambil_alt(mb_inner)
    satu_alt_mb, dua_alt_mb, tiga_alt_mb, empat_alt_mb =\
        ambil_data_rekening(mb_inner, kolom_1, kolom_2, kolom_3, kolom_4)

    alt_kc = ganti_ambil_alt(kc_inner)
    satu_alt_kc, dua_alt_kc, tiga_alt_kc, empat_alt_kc =\
        ambil_data_rekening(kc_inner, kolom_1, kolom_2, kolom_3, kolom_4)

    new = names_mb + names_kc + alt_mb + alt_kc
    the_satu = satu_mb + satu_kc + satu_alt_mb + satu_alt_kc
    the_dua = dua_mb + dua_kc + dua_alt_mb + dua_alt_kc
    the_tiga = tiga_mb + tiga_kc + tiga_alt_mb + tiga_alt_kc
    the_empat = empat_mb + empat_kc + empat_alt_mb + empat_alt_kc

    return new, the_satu, the_dua, the_tiga, the_empat

# Get the ready dataframe for blasting
def get_the_ready():
    new = ambil_kontak("blast.xlsx")
    new = filter_cutoff(new, 'EST')
    new = filter_cutoff(new, 'SDH DFTR')
    return new


if __name__ == '__main__':
    # new = filter_kc('blast.xlsx', 'mb')
    # names, numbers = ganti_ambil_mb(new)
    # ready_contact(names, numbers)

    # print(generating_for_blast())
    # print(len(generating_for_blast()))

    testing_nama, the_wilayah, the_link, _, _ = generating_custom(kolom_1='WILAYAH', kolom_2='LINK')
    print(' ')
    for i, isi in enumerate(testing_nama):
        print(isi, the_wilayah[i], the_link[i])
    print(len(testing_nama))
