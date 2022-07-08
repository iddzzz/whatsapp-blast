from wablast import Blast
import time


def test_send_messages_with_variables():
    Blast.send_messages_with_variables(1, './contact/qurban-akses-test.xlsx')


def test_send_messages_with_variables_2():
    b = Blast('root-profile.ini')
    try:
        b.access()
        b.looptilactive()
        b.send_messages_with_variables('./contact/qurban-akses-test.xlsx', col_filter='kirim')
    except Exception as why:
        print('Error', why)
    finally:
        while True:
            command = input('Exit press y: ')
            if command == 'y':
                b.close()
                break


def test_isname_exist():
    b = Blast('root-profile.ini')
    try:
        b.access()
        b.looptilactive()
        if b.is_name_exist('Mother'):
            print('Mother is in my contact')
        time.sleep(15)
    except Exception as why:
        print('Error', why)
    finally:
        b.close()


if __name__ == "__main__":
    test_send_messages_with_variables_2()