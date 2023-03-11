import ipaddress
import platform
import re
import shutil
import subprocess
import telebot
from threading import Timer
from datetime import date
import requests
import time
import matplotlib.pyplot as plt


# use masscan on windows and linux
def masscan(target):
    global program
    startupinfo = None
    if system == 'Windows':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    process = subprocess.Popen(
        [program, target, '-oL', 'ip.txt', '--rate=5000', '--wait=0', '-c', 'config.txt'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
    stdout, stderr = process.communicate()


def hidden_launch_python(script):
    if system == 'Windows':
        process = subprocess.Popen([shutil.which('python'), script], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        process = subprocess.Popen(['python3', script], stdout=subprocess.PIPE, shell=False)
    stdout, stderr = process.communicate()
    if stdout:
        print(stdout.decode())
    if stderr:
        print(stderr.decode())


def check_ip_subnets(filename_subnets):
    currentdata = str(date.today())
    result = filename_subnets + ' ' + currentdata + '\n'
    folder = 'subnets/'
    with open(folder + filename_subnets + '.txt', 'r') as f:
        for target in f:
            target = target.strip()
            start_time = time.perf_counter()
            network = ipaddress.ip_network(target)
            print(f'\nTarget: {filename_subnets}, {target}, Addresses: {network.num_addresses}\n')
            masscan(target)
            hidden_launch_python('check.py')
            end_time = time.perf_counter()
            print(f"Total time taken: {end_time - start_time:0.2f} seconds")
            final = open('final.txt', 'r')
            lines = final.readlines()
            for line in lines:
                result = result + line
        if result.find(':') == -1:
            return ''
    find_highest_matrix_version(filename_subnets, result)
    return result


def create_diagram(savefile):
    # Чтение данных из файла
    data = []
    with open('diagram.txt', 'r') as f:
        for line in f:
            data.append(int(line.strip()))

    # Подсчет числа повторений каждого числа
    counts = {}
    for num in data:
        counts[num] = counts.get(num, 0) + 1

    # Построение диаграммы в процентах повторений
    total = len(data)
    labels = []
    sizes = []
    for num, count in counts.items():
        labels.append(str(num))
        sizes.append(count / total * 100)

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    ax.set_title('TorrServer online ' + str(date.today()))
    # plt.show()

    # Сохранение диаграммы в файл png
    fig.savefig(savefile)

def send_diagram(savefile, channel):
    desc = '<b>Данный канал является демонстрационной версией бота-сканера TorrServer</b>\n\nРазумеется, он не может быть публичным. Так как сервера не резиновые. Cоздан приватный канал. Доступ в него будет стоить 300 рублей <b>ЕДИНОРАЗОВО</b>. Какие преимущества: Получаете навсегда автообновляемый список серверов с разных стран(отсортированных по хостингам). Вам не надо каждый месяц оплачивать сервер, заниматься установкой(ведь это не всем под силу), Вы просто пользуетесь чужим без ограничений. Так же для людей с приватного канала создан чат, где будет оказываться поддержка и общение администратора с пользователями. Плюс к этому - в приватном канале число хостингов равно пятнадцати.\n\nЧтобы оставить заявку на приватный канал, пишите @armkiriman с пометкой "private"'
    with open('id_d.txt', 'r+') as id_file:
        id_post = id_file.readline()
        if id_post == '':
            with open(savefile, 'rb') as photo:
                message = bot.send_photo(chat_id=channel, photo=photo, caption=desc, parse_mode='HTML')
                id_file.write(str(message.message_id))
        else:
            try:
                photo = telebot.types.InputMediaPhoto(open(savefile, 'rb'))
                bot.edit_message_media(chat_id=channel, message_id=id_post, media=photo, reply_markup=None)
                bot.edit_message_caption(chat_id=channel, message_id=id_post, caption=desc, parse_mode='HTML')
            except Exception as e:
                pass

def start_bot():
    global TORRSERV_HOSTING
    global TORRSERV_URLS
    file = open("diagram.txt", "w")

    # print(check_ip_subnets('sbcloud'))
    # savefile = 'diagram.png'
    # create_diagram(savefile)
    # send_diagram(savefile, '@publicchannel')

    bot_edit_post(check_ip_subnets('ihor'), channel_id, 20)

    path = '/var/www/oblako/' # nginx directory
    with open(path + 'constant.js', 'w') as f:
        f.write("const TORRSERV_HOSTING = {\n")
        for key, value in TORRSERV_HOSTING.items():
            f.write(f"    {key}: '{value}',\n")
        f.write("}\n\n")

        f.write("const TORRSERV_URLS = {\n")
        for key, value in TORRSERV_URLS.items():
            f.write(f"    {key}: '{value}',\n")
        f.write("}\n")

    merge_files(path, 't1.js', 'constant.js', 't2.js', 'torrserver.js')

    savefile = 'diagram.png'
    create_diagram(savefile)
    send_diagram(savefile, "@channel_id")

    set_js_constant()  # nulling constants for plugins
    Timer(60 * 60 * 6, start_bot).start()


def merge_files(path, file1, file2, file3, merged_file):
    with open(path + file1, 'r', encoding='utf-8') as f1, \
            open(path + file2, 'r', encoding='utf-8') as f2, \
            open(path + file3, 'r', encoding='utf-8') as f3, \
            open(path + merged_file, 'w', encoding='utf-8') as out_file:
        out_file.write(f1.read())
        out_file.write(f2.read())
        out_file.write(f3.read())


def bot_edit_post(text, channel_id, id):
    try:
        bot.edit_message_text(remove_duplicate_lines(text), channel_id, id)
    except:
        return


def get_matrix_version(link):
    try:
        with requests.get(link.strip() + "/echo", timeout=0.3) as response:
            if response.status_code == 200:
                html_content = response.content
                if html_content.startswith(b'MatriX'):
                    version = None
                    print(html_content.decode())
                    pattern = r"\.(\d+)[^\d]*"
                    match = re.search(pattern, html_content.decode())
                    if match:
                        version = match.group(1)
                    return version

    except Exception as e:
        print(e)
    return None


def find_highest_matrix_version(title, servers):
    global TORRSERV_HOSTING
    global TORRSERV_URLS

    highest_version = None
    highest_version_server = None

    for server in servers.split('\n'):
        if server.startswith('http'):
            version = get_matrix_version(server)
            if version is not None:
                with open('diagram.txt', 'a') as f:
                    f.write(version + '\n')
                if highest_version is None or int(version) > int(highest_version):
                    highest_version = version
                    highest_version_server = server

    if highest_version_server is not None:
        index = len(TORRSERV_HOSTING)
        TORRSERV_HOSTING[index] = ' ' + title
        TORRSERV_URLS[index] = highest_version_server


def remove_duplicate_lines(string):
    lines_seen = set()
    out_string = ''
    for line in string.split("\n"):
        if len(out_string) > 3996: break
        if line not in lines_seen:
            out_string += line + "\n"
            lines_seen.add(line)
    return out_string


def set_js_constant():
    global TORRSERV_HOSTING
    global TORRSERV_URLS
    TORRSERV_HOSTING = {
        0: 'Не выбран',
    }

    TORRSERV_URLS = {
        0: '',
    }


bot = telebot.TeleBot('APIKEY')

channel_id = '-XXXXXXXXXXXXX' # private
# channel_id  = '@channel' # public

system = platform.system()
arch = platform.architecture()[0][:-3]
program = 'masscan'
if system == 'Windows':
    program = program + arch + '.exe'

if __name__ == '__main__':
    set_js_constant()
    start_bot()
