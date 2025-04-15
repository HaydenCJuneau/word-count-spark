from pyspark.sql import SparkSession
import os
from dotenv import load_dotenv

load_dotenv()

# S3 paths
S3_INPUT = 's3a://hjuneaubucket/little-grandfather.txt'
S3_OUTPUT = 's3a://hjuneaubucket/output/'

# Spark Session
spark = SparkSession.builder \
    .appName("WordCount") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.367") \
    .getOrCreate()

# Hadoop S3 Configuration
hadoop_conf = spark.sparkContext._jsc.hadoopConfiguration()
hadoop_conf.set("fs.s3a.access.key", os.getenv("AWS_ACCESS_KEY_ID"))
hadoop_conf.set("fs.s3a.secret.key", os.getenv("AWS_SECRET_ACCESS_KEY"))
hadoop_conf.set("fs.s3a.endpoint", "s3.amazonaws.com")

# Word Count Logic
text_file = spark.sparkContext.textFile(S3_INPUT)
counts = text_file.flatMap(lambda line: line.split()) \
                  .map(lambda word: (word, 1)) \
                  .reduceByKey(lambda a, b: a + b)
counts.saveAsTextFile(S3_OUTPUT)
spark.stop()