import xlrd


filename = "../sql/创建用户.xlsx"
sheet_name = "oracle数据库"


def make_sql_sh():
    print("hello")


if __name__ == '__main__':
    data = xlrd.open_workbook(filename)
    table = data.sheet_by_name(sheet_name)
    names = data.sheet_names()  # 返回book中所有工作表的名字
    #data.sheet_loaded(sheet_name)
    rowx = table.nrows  # 获取该sheet中的有效行数
    # todo 数字会变成浮点型，逻辑加入判断浮点型 https://www.cnblogs.com/xxiong1031/p/7069006.html
    shell_filename = str(table.row(1)[0].value) + ".sh"
    file = open("../sql/" + shell_filename + "", "w+", encoding="UTF-8")
    file.write("#!/bin/bash\n")
    file.write("sql / as sysdba << EOF\n")
    for row in range(1, rowx):
        username = str(table.row(row)[11].value)
        password = str(table.row(row)[12].value)
        table_name = str(table.row(row)[13].value)
        table_dir = str(table.row(row)[14].value)
        # todo 表空间位置加入
        sql = "CREATE TABLESPACE " + table_name + " DATAFILE " \
              "'" + table_dir + table_name + ".DBF' size 2048M " \
            " AUTOEXTEND on next 100M maxsize unlimited EXTENT MANAGEMENT" \
            " LOCAL uniform size 10M SEGMENT SPACE MANAGEMENT AUTO;\n"
        file.write(sql)
        upper_username = username.upper()
        sql = "CREATE TABLESPACE " + upper_username + "_INDEX " \
              "DATAFILE '" + table_dir + upper_username + "_INDEX.DBF'  " \
              "size 512M  AUTOEXTEND on next 10M maxsize unlimited EXTENT MANAGEMENT LOCAL uniform size 1M " \
              "SEGMENT SPACE MANAGEMENT AUTO;\n"
        file.write(sql)
        sql = "create user " + username + " identified by  " + password + " default " \
              "tablespace " + table_name + " temporary tablespace TEMP profile DEFAULT;\n"
        file.write(sql)
        sql = "grant dba,connect,resource to " + username + ";\n"
        file.write(sql)
        sql = "commit;\n"
        file.write(sql)
    file.write("EOF\n")
    #
    # table.row_slice(rowx)  # 返回由该列中所有的单元格对象组成的列表
    #
    # table.row_types(rowx, start_colx=0, end_colx=None)  # 返回由该行中所有单元格的数据类型组成的列表
    #
    # table.row_values(rowx, start_colx=0, end_colx=None)  # 返回由该行中所有单元格的数据组成的列表
    #
    # table.row_len(rowx)  # 返回该列的有效单元格长度