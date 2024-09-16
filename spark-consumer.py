import logging

from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField,StringType, ArrayType


def create_cassandra_session

def  create_keyspace(session):
    session.execute("""
                    CRAETE KEYSPACE IF NOT EXISTS property_streams
                    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
                    """)
    print("keyspace created succesfully............##")


def create_table(session):
    session.execute("""
        CREATE TABLE IF NOT EXISTS property_streams.properties (
                    price text,
                    title text,
                    link text,
                    pictures, list<text>,
                    address text,
                    bedrooms text,
                    bathrooms text,
                    sqft text,
                    PRIMARY_KEY(link)
        );           
    """)

    print("Table created Successfully............")


def insert_data(session, **kwargs):
    print("Insersting data .............")
    session.execute("""
        INSERT INTO property_streams.properties(price, title, link, pictures, address, bedrooms, bathrooms,sqft)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, kwargs.values())

    print("Data inserted successfully..................")


def create_cassandra_session():
    session = Cluster(["localhost"]).connect()

    if session is not None:
        create_keyspace(session)
        create_table(session)

    return session



def main():
    logging.basicConfig(level=logging.INFO)

    spark = (SparkSession.builder.appName("SparkConsumer")
             .config("spark.cassandra.connection.host", "localhost")
             .config("spark.jar.package", "com.datastax.spark:spark-cassandra-connector_2.13:3.4.1",
                     "org.apache.spark:spark-sql-kafka-0-10_2.13:3.4.1") #get these details from mvnrepository using cassandra 3.4.1
             .getOrCreate()
             )
    
    kafka_df = (spark.readStream.format("kafka")
                .option("kafka.bootstarp.servers", "localhost:9092")
                .option("subscribe", "properties")
                .option("startingOffsets", "earliest")
                .load()
                )
    
    schema = StructType([
        StructField("price", StringType(), True),
        StructField("title", StringType(), True), # type: ignore
        StructField("Link", StringType(), True),
        StructField("pictures", ArrayType(StringType()), True), # type: ignore
        StructField("address", StringType(), True),
        StructField("bedrooms", StringType(), True),
        StructField("bathrooms", StringType(), True),
        StructField("sqft", StringType(), True)
    ])

    kafka_df = (kafka_df.selectExpr("CAST(value AS STRING) as value")
     .select(from_json(col("value"), schema).alias("data"))
     .select("data.*")
     )
    
    cassandra_query = (kafka_df.writeStream
                       .foreachBatch(lambda batch_df, batch_id: batch_df.foreach(
                           lambda row: insert_data(create_cassandra_session(), **row.asDict())
                       ))
                       .start()
                       .awaitTermination()
                       )
    

    




if __name__ == '__main__':
    main()

# import pyspark
# print(pyspark.__version__)