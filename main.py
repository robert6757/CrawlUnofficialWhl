import requests
from lxml import etree
import os

def find_all_files(path, all_files):
    file_list = os.listdir(path)
    for file in file_list:
        cur_path = os.path.join(path, file)
        if os.path.isdir(cur_path):
            # 递归调用
            find_all_files(file, all_files)
        else:
            all_files.add(file)
    return all_files

class AutoDownWhl():
    def __init__(self):
        # 包地址
        self.url = 'https://www.lfd.uci.edu/~gohlke/pythonlibs/'
        # 下载地址
        # https://download.lfd.uci.edu/pythonlibs/x6hvwk7i/cp36/atom-0.7.0-cp37-cp37m-win32.whl
        self.base_url = 'https://download.lfd.uci.edu/pythonlibs/x6hvwk7i/'
        # 模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36'
        }
        # self.target_folder = r'E:/PythonRep/unofficial_win_packages/'
        self.target_folder = r'F:\gitworkspace\mine\CrawlUnofficialWhl\test'

    # 获取选择器与包名
    def getLib(self):
        raw_text = requests.get(self.url, headers=self.headers).content
        seletor = etree.HTML(raw_text)
        lib_names = seletor.xpath('//ul[@class="pylibs"]//li//strong//text()')
        return seletor, lib_names

    # 输出所有包名
    def print_AllLib(self, lib_names):
        print('\n------------------共查找到' + str(len(lib_names)) + '个包------------------\n')
        for i in range(len(lib_names)):
            if i and i % 15 == 0:
                print('\n')
            print(lib_names[i], end=' ')

    # 搜索与下载
    def searchDown(self, downloadMethod='axel'):
        seletor, lib_names = self.getLib()
        self.print_AllLib(lib_names)

        # 列举已下载的所有库
        downloaded_package = set()
        find_all_files(self.target_folder, downloaded_package)

        # 依次下载所有库
        lib_count = len(lib_names)
        for index, lib_name in enumerate(lib_names):
            detail_libs = seletor.xpath('//ul[@class="pylibs"]//li[' + str(index+2) + ']//ul//li//text()')
            for detail_lib in detail_libs:
                detail_name = detail_lib.strip().replace('‑', '-')
                if detail_name.endswith('.whl') == False:
                    continue

                # 下载未还未下载的库
                if detail_name in downloaded_package:
                    continue
                print('开始下载-->' + detail_name)
                # 获取cp字段，如atom-0.7.0-cp37-cp37m-win32.whl，获取cp37
                detail_name_split = detail_name.split('-')
                if len(detail_name_split) > 3:
                    cp_tag = detail_name.split('-')[2] + '/'
                if cp_tag.startswith('pp'):
                    # pp开头，则转为pypy，如：ad3-2.2.1-pp37-pypy37_pp73-win_amd64.whl
                    cp_tag = cp_tag.replace('pp', 'pypy')
                if cp_tag.endswith('38/') or cp_tag.endswith('39/') or cp_tag.endswith('310/')\
                        or cp_tag == 'py3/' or cp_tag == 'py2/' or 'py2.py3/':
                    # 对于高版本Python和固定大版本的Python是没有子目录的
                    download_url = self.base_url + detail_name
                else:
                    download_url = self.base_url + cp_tag + detail_name
                if downloadMethod == 'curl':
                    cmd = 'curl -s -o %s/%s %s' % (self.target_folder, detail_name, download_url)
                else:
                    cmd = 'axel %s' % download_url
                while True:
                    cmd_res = os.system(cmd)
                    if cmd_res == 0:
                        print('下载完毕-->' + detail_name )
                        break
                    else:
                        print('下载失败-->' + detail_name)
            print("Download percentage: %d/%d" % (index, lib_count))

if __name__ == '__main__':
    dw = AutoDownWhl()
    dw.searchDown(downloadMethod='curl')
