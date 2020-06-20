import mysql.connector
import sys


def test():
    password = sys.argv[1]
    try:
        connection = mysql.connector.connect(host="localhost",
                                             database="moviedb",
                                             user="root",
                                             password=password)
        cursor = connection.cursor()
        cursor.execute("show tables")
        connection.close
    except mysql.connector.Error as e:
        print("not connected. Error : %s" % e)
        
def main():
    test()
if __name__ == "__main__":
    main()
