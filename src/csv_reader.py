# -*- coding: utf-8 -*-
import csv
import os

csv_path = "/yiyuan/data/home/wanghuozhu/ws/other/MalConv-keras/example.csv"
old_sample_dir = "/yiyuan/data/home/wanghuozhu/ws/share/0win_share/pe_virus_backup/"
new_sample_dir = "/yiyuan/data/home/wanghuozhu/ws/share/0win_share/malconv_keras_samples/"
filename_col_index = 0


def read_row():
    with open(csv_path, 'r') as csvfile:
        f_csv = csv.reader(csvfile)
        row_index = 1
        for row in f_csv:
            print("\n row_index: %s row: %s" % (row_index, row))
            if len(row) != 0:
                sample_name = row[filename_col_index]
                print("sample_name: %s" % sample_name)
                if len(sample_name) != 0:
                    old_path_name = old_sample_dir + sample_name
                    if os.path.isfile(old_path_name):
                        os.rename(old_path_name, new_sample_dir + sample_name)
                        row_index = row_index + 1


def main():
    read_row()


if __name__ == '__main__':
    main()
