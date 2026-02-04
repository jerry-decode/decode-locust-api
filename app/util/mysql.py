import pymysql

from app.config import MYSQL_SERVER, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DB


class DatabaseConn:
    def __init__(self, database=MYSQL_DB):
        # 数据库初始化连接
        self._mysql = pymysql.connect(
            host=MYSQL_SERVER,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=int(MYSQL_PORT),
            database=database,
            connect_timeout=1
        )
        self._conn = self._mysql.cursor(pymysql.cursors.DictCursor)

    def run(self, sql: str, values: list) -> any:
        try:
            self._mysql.ping(reconnect=True)
            self._conn.execute(sql, values)
            self._mysql.commit()
            _results = self._conn.fetchall()
        except Exception as error:
            self._mysql.rollback()
            raise error
        finally:
            self._conn.close()
            self._mysql.close()
        return _results


class Db(DatabaseConn):
    """
    数据库查询（链式调用）使用介绍:
    1、必须按顺序调用，不可把select、insert、update、delete调用在其它条件前面
    2、除了Db()初始化外，其他函数都可省略
    ## 查询语句 select
        Db().fields().join().where().group_by().having().orderby().limit().select()
    ## 插入语句 insert
        Db().fields().values().insert()
    ## 更新语句 update
        Db().set().where().update()
    ## 删除语句 delete
        Db().where().delete()
    """

    def __init__(self, database, table):
        """
        :param table: 表名 可接别名
        :param database: 库名 不传默认走配置
        """
        super().__init__(database)
        # 公共
        self._table = f"`{table}`"
        self._column = "*"
        self._where = ""
        self._format_values = []
        # select
        self._group_by = ""
        self._having = ""
        self._orderby = ""
        self._limit = ""
        # insert
        self._value = ""
        # update
        self._set = ""

    def fields(self, *args):
        """
        用于select语句获取字段，或insert语句插入字段
        column("id", "name", "age")
        :param args: "id", "name", "age"
        """
        self._column = ', '.join(args)
        return self

    def leftJoin(self, other_table: str, alias: str, **kwargs):
        """
        用于select语句 多表联查
        join('s_user_other', ['id', 'uid'])
        :param other_table: 需要连接表名 可接别名
        :param alias: 表别名
        :param kwargs: 连接条件 tableA.field=tableB.field
        """
        on_expression = [f"{alias}.`{key}` = {value}" for key, value in kwargs.items()]
        on_expression = " AND ".join(on_expression)
        self._table += f" LEFT JOIN `{other_table}` AS {alias} ON {on_expression}"
        return self

    def rightJoin(self, other_table: str, alias: str, **kwargs):
        """
        用于select语句 多表联查
        rightJoin('s_user_other', 'a', ID='uid')
        :param other_table: 需要连接表名 可接别名
        :param alias: 表别名
        :param kwargs: 连接条件 field=tableB.field
        """
        on_expression = [f"{alias}.`{key}` = {value}" for key, value in kwargs.items()]
        on_expression = " AND ".join(on_expression)
        self._table += f" RIGHT JOIN `{other_table}` AS {alias} ON {on_expression}"
        return self

    def innerJoin(self, other_table: str, alias: str, **kwargs):
        """
        用于select语句 多表联查
        innerJoin('s_user_other', 'a', ID='uid')
        :param other_table: 需要连接表名 可接别名
        :param alias: 表别名
        :param kwargs: 连接条件  field=tableB.field
        """
        on_expression = [f"{alias}.`{key}` = {value}" for key, value in kwargs.items()]
        on_expression = " AND ".join(on_expression)
        self._table += f" INNER JOIN `{other_table}` AS {alias} ON {on_expression}"
        return self

    def where(self, where: str, *args):
        """
        用于select、update、delete语句 查询条件
        where('id = ? and uname = ?', s_id, uname)
        :param where: where 'id = ? and uname = ?'
        :param args: s_id, uname
        :return:
        """
        self._format_values.extend(args)
        self._where = f" WHERE {where.replace('?', '%s')}"
        return self

    def group(self, *args):
        """
        用于select语句 分组
        group('uname')
        :param args: "age", "uname"
        :return:
        """
        group = ', '.join(args)
        self._group_by = f" GROUP BY {group}"
        return self

    def having(self, having: str, *args):
        """
        用于select语句 分组条件
        having('age > %s', 1)
        :param having: age > %s
        :param args: age实际值
        :return:
        """
        self._format_values.extend(args)
        self._having = f" HAVING {having}".replace('?', "%s")
        return self

    def order(self, by: str, direction: str):
        """
        用于select语句 排序
        order('id', DType.DESC)
        :param by: 表字段名称
        :param direction: ASC or DESC
        :return:
        """
        self._orderby = f" ORDER BY {by} {direction.upper()}"
        return self

    def limit(self, first: int, second: int = None):
        """
        用于select语句 分页
        limit(10) or limit(10, 20)
        :param first: 10
        :param second: 20
        :return:
        """
        if second:
            self._limit = f" LIMIT {first}, {second}"
        else:
            self._limit = f" LIMIT {first}"
        return self

    def values(self, *args):
        """
        用于insert语句插入字段值
        values('id', 'username', 'create_time')
        :param args: id, user, ...
        :return:
        """
        for v in args:
            self._format_values.append(v)
            self._value += "%s, "

        self._value = self._value[:-2]
        return self

    def set(self, **kwargs):
        """
        用于update语句修改字段
        set(uname='zhou', age=18)
        :param kwargs: name="John", age=18
        """
        for key, value in kwargs.items():
            self._set += f'{key} = %s, '
            self._format_values.append(value)
        self._set = self._set[:-2]
        return self

    def select(self):
        """
        用于select语句 执行查询结果
        :return: 查询结果 格式为列表包裹字典[{}]
        """
        _sql = f"SELECT {self._column} FROM {self._table}{self._where}{self._group_by}{self._having}{self._orderby}{self._limit};"
        return self.run(_sql, self._format_values)

    def insert(self):
        """
        用于insert语句 执行insert
        """
        _sql = f"INSERT INTO {self._table} ({self._column}) VALUES ({self._value});"
        return self.run(_sql, self._format_values)

    def update(self):
        """
        用于update语句 执行update
        """
        _sql = "UPDATE" + f" {self._table} SET {self._set}{self._where};"
        self.run(_sql, self._format_values)

    def delete(self):
        """
        用于delete语句 执行delete
        """
        _sql = "DELETE FROM" + f" {self._table}{self._where}"
        self.run(_sql, self._format_values)

    def get_select_sql(self):
        _sql = f"SELECT {self._column} FROM {self._table}{self._where}{self._group_by}{self._having}{self._orderby}{self._limit};"
        print(_sql, self._format_values)

    def get_insert_sql(self):
        _sql = f"INSERT INTO {self._table} ({self._column}) VALUES ({self._value});"
        print(_sql, self._format_values)

    def get_update_sql(self):
        _sql = "UPDATE" + f" {self._table} SET {self._set}{self._where};"
        print(_sql, self._format_values)

    def get_delete_sql(self):
        _sql = "DELETE FROM" + f" {self._table}{self._where}"
        print(_sql, self._format_values)
