from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import mmh3
from pyspark.sql.functions import udf
from pyspark.sql.types import LongType
import hashlib

def compute_hash(url, text):
  if url is None:
    url = ''

  if text is None:
    text = ''
  
  total = (url + text).encode("utf-8")
  return mmh3.hash64(total)[0]
  #return hashlib.md5(total).digest()


def main():
  spark = SparkSession.builder.config("spark.local.dir", "/media/hd/spark-tmp").config("spark.driver.memory", "16G") .master("local[8]").appName('spark-stats').getOrCreate()
  df = spark.read.parquet("/media/hd2/allmeta/2Ben/")
  df = df.select('url', 'caption')
  udf_compute_hash = udf(compute_hash, LongType())
  df = df.withColumn("hash", udf_compute_hash(df["url"], df["caption"]))
  df = df.select('hash')
  df.repartition(64).write.mode("overwrite").parquet("/media/hd2/allmeta/2Ben_hashes")

if __name__ == "__main__":
  main()
