import csv
import sys

# default value
K = 1
train_data_filename = "Hill-Valley/HV_Training.data"
test_data_filename = "Hill-Valley/HV_Testing.data"

target_filename = "knn.deal"

datalog_schema = '''
database( { train(Id:integer, ColId:integer, Value:float),
            train_labels(Id:integer, Label:integer),
            test(Id:integer, ColId:integer, Value:float),
            test_labels(Id:integer, Label:integer),
            define_k(K:integer)
          } ).
'''

datalog_rules = '''
% Compute distance
dis2_col(Id1, Id2, Col, D2) <- test(Id1, Col, V1), train(Id2, Col, V2), D2 = (V1-V2) * (V1-V2).
dis2(Id1, Id2, sum<D2>) <- dis2_col(Id1, Id2, Col, D2).

% KNN classification
smaller_count(Id, Train_id1, count<Train_id2>) <- dis2(Id, Train_id1, D1), dis2(Id, Train_id2, D2), D2 < D1.
knn(Id, Train_id, Label) <- train_labels(Train_id, Label), test_labels(Id, _), ~smaller_count(Id, Train_id, C). % Min Dis
knn(Id, Train_id, Label) <- train_labels(Train_id, Label), smaller_count(Id, Train_id, C), define_k(K), C < K.

vote(Id, Label, count<Train_id>) <- knn(Id, Train_id, Label).
not_max(Id, Label1) <- vote(Id, Label1, C1), vote(Id, Label2, C2), C1 < C2.
knn_classify(Id, min<Label>) <- vote(Id, Label, C), ~not_max(Id, Label). % If there is multiply choices, return the min index

export knn_classify(Id, Label).
query knn_classify(Id, Label).

% Compute accuracy
true_classify(count<Id>) <- knn_classify(Id, Label), test_labels(Id, Label).
test_count(count<Id>) <- test_labels(Id, _).
accuracy(A) <- true_classify(T), test_count(C), A = T / C.

export true_classify(T).
query true_classify(T).

export test_count(C).
query test_count(C).

export accuracy(A).
query accuracy(A).
'''


def write_schema():
    with open(target_filename, 'w') as target_file:
        target_file.write(datalog_schema)
        target_file.write('\n')


def write_rules():
    with open(target_filename, 'a') as target_file:
        target_file.write(datalog_rules)


def define_k():
    with open(target_filename, 'a') as target_file:
        line = "define_k(" + str(K) + ').'
        target_file.write(line + '\n')
        target_file.write('\n')


def generate_datalog_fact(fact_name, data):
    prefix = fact_name + "("
    postfix = ")."
    with open(target_filename, 'a') as target_file:
        for row in data:
            line = prefix + str(row[0])
            for i in range(1, len(row)):
                line += ',' + str(row[i])
            line += postfix
            target_file.write(line + '\n')
        target_file.write('\n')


if __name__ == "__main__":
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

    with open(train_data_filename, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        i = 0
        for line in lines:
            if i == 0:
                i += 1
                continue
            for j in range(0, len(line)-1):
                train_data.append([i, j, line[j]])
            train_label.append([i, line[-1]])
            i += 1

    with open(test_data_filename, 'r') as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        i = 0
        for line in lines:
            if i == 0:
                i += 1
                continue
            for j in range(0, len(line)-1):
                test_data.append([i, j, line[j]])
            test_label.append([i, line[-1]])
            i += 1

    # generate DeAL program
    write_schema()
    define_k()
    generate_datalog_fact("train", train_data)
    generate_datalog_fact("test", test_data)
    generate_datalog_fact("train_labels", train_label)
    generate_datalog_fact("test_labels", test_label)
    write_rules()
    print("Finished. The generated Datalog program file is " + target_filename)
