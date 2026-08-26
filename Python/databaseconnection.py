#Connects to HIDS database, executes and commits SQL
def query(sql):
        if sql == "": return False
        import MySQLdb
        from warnings import filterwarnings
        filterwarnings('ignore', category = MySQLdb.Warning)
        conn = MySQLdb.connect(host="foo",port=3306,user="foo",passwd="foo",db="foo")
        cursor = conn.cursor()
        try:
                cursor.execute(sql)
                conn.commit()
                return cursor.fetchall()
        except MySQLdb.Error, e:
                try:
                        print "MySQL Error [%d]: %s\nQUERY: %s" % (e.args[0], e.args[1], sql)
                except IndexError:
                        print "MySQL Error: %s" % str(e)
        except MySQLdb.Warning, e:
                try:
                        print "MySQL Warning [%d]: %s\nQUERY: %s" % (e.args[0], e.args[1], sql)
                except IndexError:
                        print "MySQL Warning: %s" % str(e)
        cursor.close()
