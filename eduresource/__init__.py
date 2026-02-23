# Cấu hình PyMySQL để tương thích với Django MySQL backend
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
