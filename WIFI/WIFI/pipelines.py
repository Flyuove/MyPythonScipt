# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import pymysql

class JsonWithEncodingPipeline(object):
    '''保存到文件中对应的class
           1、在settings.py文件中配置
           2、在自己实现的爬虫类中yield item,会自动执行'''
    def __init__(self):
        self.file = open('./result.txt', mode='wb') # 保存为json文件
    def process_item(self, item, spider):
        jsontext = json.dumps(dict(item), ensure_ascii=False) + ",\n"
        self.file.write(jsontext.encode("utf-8")) # 写入文件中
        # self.file.write(item['mac'].encode("utf-8"))
        # self.file.write(item['date'].encode("utf-8"))
        # self.file.write("\n")
        return item

    def spider_closed(self, spider):  # 爬虫结束时关闭文件
        self.file.close()


class MysqlWithEncodingPipeline(object):
    '''保存到数据库中对应的class
       1、在settings.py文件中配置
       2、在自己实现的爬虫类中yield item,会自动执行'''

    def __init__(self, dbConnect):
        self.dbConnect = dbConnect
        ''' 这里注释中采用写死在代码中的方式连接线程池，可以从settings配置文件中读取，更加灵活
            self.dbpool=adbapi.ConnectionPool('MySQLdb',
                                          host='127.0.0.1',
                                          db='crawlpicturesdb',
                                          user='root',
                                          passwd='123456',
                                          cursorclass=MySQLdb.cursors.DictCursor,
                                          charset='utf8',
                                          use_unicode=False)'''

    @classmethod
    def from_settings(cls, settings):
        '''1、@classmethod声明一个类方法，而对于平常我们见到的则叫做实例方法。
           2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
           3、可以通过类来调用，就像C.f()，相当于java中的静态方法'''
        dbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
        )

        dbConnect = pymysql.Connect(**dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(dbConnect)  # 相当于dbpool付给了这个类，self中可以得到

    # pipeline默认调用
    def process_item(self, item, spider):

        cursor = self.dbConnect.cursor()
        try:
            sqlInsert = "insert into wifi_log(mac,datetime,sign_day) values('%s','%s',date_format(now(),'%%Y-%%m-%%d'));" % (item['mac'], item['date'])
            print(sqlInsert)
            cursor.execute(sqlInsert)
            self.dbConnect.commit()
        except Exception as e:
            print("Reason:", e)
            self.dbConnect.rollback()
        return item


