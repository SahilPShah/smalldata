import pymysql.cursors
def main():
    # Connect to the database
    connection = pymysql.connect(host='smalldata411.web.illinois.edu',
                                 user='smalldata_sahils2',
                                 password='whitesox2005',
                                 db='smalldata411_musicAggDB',
                                 port='3306')





if __name__  == "__main__": main()