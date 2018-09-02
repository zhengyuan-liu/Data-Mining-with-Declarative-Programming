# Part 2: K-Nearest Neighbors Classifier (KNN)

## 1. Dataset: Hill-Valley Data Set[1]
The dataset is in Hill-Valley folder, there are eight files, the first seven files are original:

(a) Hill_Valley_without_noise_Training.data 

(b) Hill_Valley_without_noise_Testing.data 

These first two datasets (without noise) are a training/testing set pair where the hills or valleys have a smooth transition. 

(c) Hill_Valley_with_noise_Training.data 

(d) Hill_Valley_with_noise_Testing.data 

These next two datasets (with noise) are a training/testing set pair where the terrain is uneven, and the hill or valley is not as obvious when viewed closely. 

(e) Hill_Valley_sample_arff.text 

The sample ARFF file is useful for setting up experiments, but is not necessary. 

(f) Hill_Valley_visual_examples.jpg

This graphic file shows two example instances from the data. 

(g) Hill-Valley.names

The description of the dataset.

There are 2 additional files:

(h) HV_Training.data: first 200 tuples of Hill_Valley_with_noise_Training.data

(i) HV_Testing.data: firt 100 tuples of Hill_Valley_with_noise_Testing.data

These two files are abridgment verisons of Hill_Valley_with_noise dataset, since running on the original Hill_Valley_with_noise dataset will cost a lot of time and memory. These abridgment verisons are good samples to show the effect of the KNN algorithm, so they are used as the default dataset.

## 2. SQL Program in IDM DB2
Since IBM DB2 Express Edition seems not working well on the up-to-date Mac OS, I used IBM DB2 Developer Community Edition to implement SQL program, which is a database server running in a Docker container. To run the DB2 script, you need to run it in the Docker container with the DB2 server. (It should also work in any OS with a DB2 server, but not tested) I used the default SAMPLE database of DB2 as the database of this project.

### (1) generate preprocessed data and load_data.sh (HAS BEEN DONE)
This step runs a python script db2_preprocess.py, which reads the original csv-format training data and testing data, generate preprocessed data (adding a Point ID column which used in the verticalization step), and at the mean time generates a DB2 script load_data.sh. The hyper-parameter K is also assigned in this step.

#### Usage:

	$ python db2_preprocess.py K path-of-training-data path-of-testing-data  # set K and path of training data and testing data
or

	$ python db2_preprocess.py K  # set K and using default path of training data and testing data
or

	$ python db2_preprocess.py    # using default arguments

#### Default arguments:
	K = 1
	train_data_filename = "Hill-Valley/HV_Training.data"
	test_data_filename = "Hill-Valley/HV_Testing.data"

#### Output:
	training_preprocessed.data
	testing_preprocessed.data
	load_data.sh

* This step has been done with the default dataset and hyper-parameter K, and you can run it again to change dataset and K.

### (2) Verticalize Table
This step first reads the preprocessed training and testing data into DB2 table TRAINSET and TESTSET by running load_data.sh, then verticalize them into four tables: VTRAIN, TRAIN_LABEL, VTEST, TEST_LABEL by running verticalize.sh. The schema of VTRAIN (VTEST) and TRAIN_LABEL (TEST_LABEL) are:

	VTRAIN (VTEST) (
		PID INTEGER, 
		ColID INTEGER,
		ColValue DOUBLE
	)
	TRAIN_LABEL (TEST_LABEL) (
		PID INTEGER, 
		PLabel INTEGER
	)

Usage:

	$ bash ./load_data.sh
	$ bash ./verticalize.sh

### (3) KNN classification
This step run the KNN classification algorithm on the verticalized table, and output the classification results (in table RESULTS) and accuracy (in table ACCURACY). The schema of RESULTS and ACCURACY are:

	RESULTS (TEST_PID INTEGER, PREDICTED_CLASS INTEGER)
	ACCURACY (TEST_NUMBER INTEGER, TRUE_CLASSIFIED INTEGER, ACCURACY DOUBLE)

The accuracy table will finally show in the terminal, e.g.:

	TEST_NUMBER TRUE_CLASSIFIED ACCURACY                
	----------- --------------- ------------------------
		100              55   +5.50000000000000E-001

Usage:

	$ bash ./knn.sh

Since this script involves SQL operations inserting a big table, DB2 may raise "The transaction log for the database is full" error. If this happens, using the following commands to update log configurations of DB2[2]:

	$ db2 update db cfg using LOGFILSIZ 10240
	$ db2 update db cfg using LOGPRIMARY 100
	$ db2 update db cfg using LOGSECOND 100
	$ db2stop force  
	$ db2start


## 3. Datalog Program in DeALS

### (1) Generate DeALS program knn.deal (HAS BEEN DONE)
This step read the original dataset, and output the target DeALS program knn.deal with the veritcalized facts. The database schema is:

	database( { train(Id:integer, ColId:integer, Value:float),
	            train_labels(Id:integer, Label:integer),
	            test(Id:integer, ColId:integer, Value:float),
	            test_labels(Id:integer, Label:integer),
	            define_k(K:integer)
	          } ).

Usage:

	$ python generate_datalog.py K path-of-training-data path-of-testing-data
or

	$ python generate_datalog.py K  # set K and using default path of training data and test data
or

	$ python generate_datalog.py    # using default arguments

Default arguments:

	K = 1
	train_data_filename = "Hill-Valley/HV_Training.data"
	test_data_filename = "Hill-Valley/HV_Testing.data"

Output:

	knn.deal

* This step has been done with the default dataset and hyper-parameter K, and you can run it again to change dataset and K.

(2) Run the knn.deal by DeALS
This step run the knn.deal by DeALS-0.91, and output true_classify(T), test_count(C), and accuracy(A).

	./runfile.sh DeALS-0.91.jar knn.deal

This step is very time-consuming, may take hours to finish.


## 4. KNN Classification Results on Hill-Valley dataset
Because of long running time of experiments, I only run the following experiments on 2 groups of dataset:

(1) HV_Training.data, HV_Testing.data, K = 1:

	TEST_NUMBER TRUE_CLASSIFIED ACCURACY                
	----------- --------------- ------------------------
		100              55                      55%

(2) Hill_Valley_without_noise_Training.data, Hill_Valley_without_noise_Testing.data, K = 1:

	TEST_NUMBER TRUE_CLASSIFIED ACCURACY                
	----------- --------------- ------------------------
		606             376                      62%


## 5. Structure of the submission zip:
KNN-Submission

|--DB2

   |--Hill-Valley: Dataset Folder
   
   |--db2_preprocessed.py: python script to generate preprocessed data and load_data.sh
   
   |--training_preprocessed.data: preprocessed training dataset generated by db2_preprocessed.py
   
   |--testing_preprocessed.data: preprocessed training dataset generated by db2_preprocessed.py
   
   |--load_data.sh: DB2 script to load preprocessed data to DB2 TRAINSET and TESTSET table
   
   |--verticalize.sh: DB2 script to verticalize data in TRAINSET and TESTSET to VTRAIN, TRAIN_LABEL, VTEST, TEST_LABEL table
   
   |--knn.sh: Run KNN algorithm on verticalized data and get classification results and accruacy

|--DeALS

   |--Hill-Valley: Dataset Folder
   
   |--generate_datalog.py: python script to generate Datalog program for KNN algorithm
   
   |--knn.deal: Datalog program for KNN algorithm generated by generate_datalog
   
   |--DeALS-0.91.jar: jar of DeALS
   
   |--runfile.sh: run script of DeALS

|--README


## Reference:
[1] Hill-Valley Data Set, http://archive.ics.uci.edu/ml/datasets/hill-valley

[2] DB2 “The transaction log for the database is full” Problem and Solution - CSDN Blog, https://blog.csdn.net/kongxx/article/details/41203939
