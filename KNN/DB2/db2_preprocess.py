import csv
import sys

# default value
K = 1
train_data_filename = "Hill-Valley/HV_Training.data"
test_data_filename = "Hill-Valley/HV_Testing.data"

train_preprocessed_filename = "training_preprocessed.data"
test_preprocessed_filename = "testing_preprocessed.data"
database_name = "SAMPLE"
train_table_name = "TRAINSET"
test_table_name = "TESTSET"
sql_filename = "load_data.sql"
script_filename = "load_data.sh"

drop_table_procedure = '''CREATE OR REPLACE PROCEDURE drop_table_if_exists(IN TableName VARCHAR(50))
LANGUAGE SQL
BEGIN
    DECLARE STMT VARCHAR(200);
    IF EXISTS (SELECT NAME FROM SYSIBM.SYSTABLES WHERE NAME = TableName)
    THEN
        SET STMT = 'DROP TABLE ' || TableName;
        EXECUTE IMMEDIATE STMT;
    END IF;
END'''


# generate CREATE TABLE SQL statement
def generate_create_statement(name, heads):
    statement = "CREATE TABLE " + name + " (PID INTEGER NOT NULL, "
    for i in range(len(heads) - 1):
        statement += heads[i] + " DOUBLE, "
    statement += heads[-1] + " INTEGER)"
    return statement


# preprocess data by adding point id to each line
def preprocess_data(filename, new_filename):
    heads = []
    with open(filename, 'r') as file:
        lines = file.readlines()
        i = 0
        with open(new_filename, 'w') as new_file:
            for line in lines:
                if i == 0:
                    heads = line.split(',')
                    new_file.write("PID,"+line)  # add PID (Point ID) to head
                else:
                    new_file.write(str(i) + "," + line)  # add id to each line
                i += 1
    return heads


def generate_load_data_sql(heads):
    with open(sql_filename, 'w') as sql_file:
        sql_file.write("CONNECT TO %s\n" % database_name)
        sql_file.write("\n")

        sql_file.write(drop_table_procedure + "\n")
        sql_file.write("\n")

        sql_file.write("CALL drop_table_if_exists('K')\n")
        sql_file.write("CREATE TABLE K (K INTEGER)\n")
        sql_file.write("INSERT INTO K VALUES (%d)\n" % K)
        sql_file.write("\n")

        create_trainset_sql = generate_create_statement(train_table_name, heads)
        sql_file.write("CALL drop_table_if_exists('%s')\n" % train_table_name)
        sql_file.write(create_trainset_sql + "\n")
        sql_file.write("IMPORT FROM '%s' OF DEL INSERT INTO %s\n" % (train_preprocessed_filename, train_table_name))
        sql_file.write("\n")

        create_testset_sql = generate_create_statement(test_table_name, heads)
        sql_file.write("CALL drop_table_if_exists('%s')\n" % test_table_name)
        sql_file.write(create_testset_sql + "\n")
        sql_file.write("IMPORT FROM '%s' OF DEL INSERT INTO %s\n" % (test_preprocessed_filename, test_table_name))
        sql_file.write("\n")


def generate_load_data_script(heads):
    with open(script_filename, 'w') as script_file:
        script_file.write('db2 "CONNECT TO %s"\n' % database_name)
        script_file.write("\n")

        script_file.write('db2 "%s"\n' % drop_table_procedure)
        script_file.write("\n")

        script_file.write('db2 "CALL drop_table_if_exists(\'K\')"\n')
        script_file.write('db2 "CREATE TABLE K (K INTEGER)"\n')
        script_file.write('db2 "INSERT INTO K VALUES (%d)"\n' % K)
        script_file.write("\n")

        create_trainset_sql = generate_create_statement(train_table_name, heads)
        script_file.write('db2 "CALL drop_table_if_exists(\'%s\')"\n' % train_table_name)
        script_file.write('db2 "' + create_trainset_sql + '"\n')
        script_file.write('db2 "IMPORT FROM \'%s\' OF DEL INSERT INTO %s"\n' % (train_preprocessed_filename, train_table_name))
        script_file.write("\n")

        create_testset_sql = generate_create_statement(test_table_name, heads)
        script_file.write('db2 "CALL drop_table_if_exists(\'%s\')"\n' % test_table_name)
        script_file.write('db2 "' + create_testset_sql + '"\n')
        script_file.write('db2 "IMPORT FROM \'%s\' OF DEL INSERT INTO %s"\n' % (test_preprocessed_filename, test_table_name))
        script_file.write("\n")


if __name__ == "__main__":
    heads = []
    train_data = []
    train_label = []
    test_data = []
    test_label = []

    if len(sys.argv) == 4:
        K = sys.argv[1]
        train_data_filename = sys.argv[2]
        test_data_filename = sys.argv[3]
    elif len(sys.argv) == 2:
        K = sys.argv[1]
        print("Using default training and testing files:")
        print("training_data_filename = Hill-Valley/HV_Training.data")
        print("testing_data_filename = Hill-Valley/HV_Training.data")
    elif len(sys.argv) == 1:
        print("Using default arguments:")
        print("K = 1")
        print("training_data_filename = Hill-Valley/HV_Training.data")
        print("testing_data_filename = Hill-Valley/HV_Training.data")
    else:
        print("Error: invalid arguments")
        print("Usage: python generate_datalog")
        print("Usage: python generate_datalog K training_data_filename testing_data_filename")
        exit(1)

    heads = preprocess_data(train_data_filename, train_preprocessed_filename)
    preprocess_data(test_data_filename, test_preprocessed_filename)
    # generate_load_data_sql(heads)  # only for debug
    generate_load_data_script(heads)
