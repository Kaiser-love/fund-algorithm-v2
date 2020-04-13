from pinyin import pinyin


def count_file_lines(filename):
    filename = "data/" + filename + "/train.tsv"
    """
    快速统计文件行数
    :param filename:
    :return:
    """
    count = 0
    fp = open(filename, "rb")
    byte_n = bytes("\n", encoding="utf-8")
    while 1:
        buffer = fp.read(16 * 1024 * 1024)
        if not buffer:
            count += 1  # 包含最后一行空行 ''
            break
        count += buffer.count(byte_n)
    fp.close()
    return count


def page_list(file_path, page, count=10):
    file_path = "data/" + file_path + "/train.tsv"
    index = 0
    result = []
    page_ends = page * count
    page_starts = (page - 1) * count
    with open(file_path, mode='r', encoding='utf-8') as f:
        first_line = f.readline()  # 读完第一行后,光标到了第一行结尾 ,继续读取文件从第二行开始
        for line in f:
            index += 1
            if page_ends < index:
                break
            if page_starts < index:
                line_str = line.split("~")
                if int(line_str[2]) == 0:
                    page_ends += 1
                    continue
                result.append({
                    "id": index,
                    "text": line_str[0],
                    "label": line_str[1].replace("\n", ""),
                    "exist": 1
                })
    # for i in range(len(result)):
    #     print(result[i])
    return result


def modify_line(file_path, line, content):
    file_path = "data/" + file_path + "/train.tsv"
    line += 1
    with open(file_path, 'r+', encoding='utf8') as f:
        cont = 1
        while True:
            cont += 1
            f.readline()
            if cont == int(line):
                f.seek(f.tell())
                f.write(content + "\n")
                break


if __name__ == '__main__':
    # page_list('data/fund_risk/train.tsv', 1)
    # modify_line('data/fund_risk/train.tsv', 1, "高收益~1~1")
    print(pinyin.get("诋毁其他基金管理人", format='strip'))
