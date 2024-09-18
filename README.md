# Real Estate Data Engineering

The project involves developing a real-time streaming pipeline for real estate data from a website (Redfin.com). Extracts data by mimicking the browser as human, streaming the data into Kafka and processing the data using Spark before storing it in Cassandra..

Real Estate Website: https://www.redfin.com/


## Tech Stack

- **Language:** [Python](https://www.python.org/)
- **Web Scraping:** [Playwright](https://playwright.dev/)
- **Stream Processing:** [Kafka](https://kafka.apache.org/), [Spark Streaming](https://spark.apache.org/docs/latest/streaming-programming-guide.html)


- **Containerization:** [Docker](https://www.docker.com/), [Docker Compose](https://docs.docker.com/compose/)
- **Database:** [Cassandra](https://cassandra.apache.org/_/index.html)



<!-- Tools and Technologies:

Playwright for web scraping.
Kafka for real-time data streaming.
Spark for data processing.
Cassandra for data storage.
Docker for orchestration of services. -->


## System Architecture

![Architecture Diagram]("https://github.com/Prudhvi-reddy/Real_Estate_DE/blob/bs4-1/Images/Architecture.png")



# Project Pipeline: Real Estate Data Engineering Streaming Pipeline

## 1. Extract Data from Real Estate Website (https://www.redfin.com)

The project begins with extracting data from Redfin, a popular real estate website, using the Playwright library.

- **Browsers & User Agents**: 
  - Utilizes Playwright to open various browsers (Chromium, Firefox, WebKit) with randomized user agents to mimic human browsing behavior and evade detection.
  
- **Navigation**: 
  - For each property search and listing page, a new browser context is initiated with a different user agent, ensuring each request appears unique.

- **Timing**: 
  - Introduces random delays between page navigations to simulate human-like interactions and avoid detection by the website.

- **Data Extraction**: 
  - Extracts key property details:
    - **Address**: Location of the property.
    - **Price**: Listed price.
    - **Link**: URL to the property detail page.
    - **Beds**: Number of bedrooms.
    - **Baths**: Number of bathrooms.
    - **Area (sqft)**: Total area in square feet.
    - **Images**: URLs of images by parsing `<img>` tags.

- **User Agents**:
    - 
   **Chromium**
    - **User Agent String**: `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3`
    - **Description**: This user agent string represents a Chromium-based browser running on Windows 10, version 64-bit. It indicates that the browser uses WebKit as its rendering engine and Chrome version 58.

    **Firefox**
    - **User Agent String**: `Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0`
    - **Description**: This user agent string corresponds to Firefox running on Windows 10, version 64-bit. It uses the Gecko rendering engine and is identified as Firefox version 54.

    **Webkit**
    - **User Agent String**: `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.3 Safari/602.3.12`
    - **Description**: This user agent string denotes a WebKit-based browser running on macOS Sierra (OS X 10.12.6). It indicates Safari version 10.0.3 and uses WebKit as its rendering engine.
These user agents are used to simulate different browsers and platforms during web scraping to mimic human behavior and avoid detection.




## 2. Send Data to Kafka

After extraction, data is serialized as JSON and sent to an Apache Kafka topic named "properties."

- **KafkaProducer**: 
  - Configured to connect to the Kafka broker and publish messages to the "properties" topic for real-time data streaming.
  - Kafka enables real-time streaming of data, allowing the system to process property listings as they are scraped

## 3. Data Processing with Spark

The `spark-consumer.py` script processes streamed data from Kafka using Apache Spark.

- **Spark Configuration**: 
  - Configured to connect to Cassandra and Kafka using `spark-cassandra-connector` and `spark-sql-kafka-0-10`.

- **Data Schema**: 
  - Defines a schema for parsing JSON data with fields such as `StringType` for text and `ArrayType` for image lists.

- **Stream Processing**: 
  - Reads and processes data from Kafka in real-time and passes it to the next step for storage.

## 4. Cassandra Data Storage

Processed data is stored in Cassandra for long-term storage and querying.

- **Cassandra Keyspace and Table Creation**: 
  - Creates keyspace `property_streams` and table `properties` if not already present.

- **Data Insertion**: 
  - Inserts data into the Cassandra table using Spark's `foreachBatch` function for efficient batch processing.

## 5. Orchestration with Docker

The pipeline is orchestrated using Docker to manage services and dependencies.

- **Docker Compose**: 
  - Defines services and their configurations in `docker-compose.yml`.

- **Services Configuration**:
  - **Zookeeper**: Manages Kafka's distributed metadata.
  - **Kafka Broker**: Handles streaming data and topics.
  - **Spark**: Includes master and worker nodes for distributed processing.
  - **Cassandra**: Stores processed data in a distributed database.

- **Networking**: 
  - Services are connected via a Docker network (`datamasterylab`) for effective communication.


