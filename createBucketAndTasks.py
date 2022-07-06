from influxdb_client import InfluxDBClient
from influxdb_client.client import tasks_api, bucket_api
import json

with open("config.json", "r") as f:
    config = json.load(f)

class Orga():
    def __init__(self, name, id):
        self.name = name
        self.id = id

organization = Orga(config['InfluxAPI']['org'],config['InfluxAPI']['org_id'])
client = InfluxDBClient(url=config['InfluxAPI']['url'], token=config['InfluxAPI']['token'],
                            org=config['InfluxAPI']['org'])
taskapi = tasks_api.TasksApi(influxdb_client=client)
bucketapi = bucket_api.BucketsApi(influxdb_client=client)

bucketapi.create_bucket(bucket=None,bucket_name="1s_max",org_id=organization.id, retention_rules=None)
bucketapi.create_bucket(bucket=None,bucket_name="1s_min",org_id=organization.id, retention_rules=None)
bucketapi.create_bucket(bucket=None,bucket_name="1m_max",org_id=organization.id, retention_rules=None)
bucketapi.create_bucket(bucket=None,bucket_name="1m_min",org_id=organization.id, retention_rules=None)
bucketapi.create_bucket(bucket=None,bucket_name="1h_max",org_id=organization.id, retention_rules=None)
bucketapi.create_bucket(bucket=None,bucket_name="1h_min",org_id=organization.id, retention_rules=None)
bucketapi.create_bucket(bucket=None,bucket_name="8h_max",org_id=organization.id, retention_rules=None)
bucketapi.create_bucket(bucket=None,bucket_name="8h_min",org_id=organization.id, retention_rules=None)
flux1s_max = """from(bucket: "RawData")
    |> range(start: -30s)
    |> filter(fn: (r) => r._measurement == "root")
    |> aggregateWindow(every: 1s, fn: max)
    |> to(bucket: "1s_max", org: "mcx")"""
flux1s_min = """from(bucket: "RawData")
    |> range(start: -30s)
    |> filter(fn: (r) => r._measurement == "root")
    |> aggregateWindow(every: 1s, fn: min)
    |> to(bucket: "1s_min", org: "mcx")"""
flux1m_max = """from(bucket: "1s_max")
    |> range(start: -1m)
    |> filter(fn: (r) => r._measurement == "root")
    |> aggregateWindow(every: 1m, fn: max)
    |> to(bucket: "1m_max", org: "mcx")"""
flux1m_min = """from(bucket: "1s_min")
    |> range(start: -1m)
    |> filter(fn: (r) => r._measurement == "root")
    |> aggregateWindow(every: 1m, fn: min)
    |> to(bucket: "1m_min", org: "mcx")"""
flux1h_max = """from(bucket: "1m_max")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "root")
    |> aggregateWindow(every: 1h, fn: max)
    |> to(bucket: "1h_max", org: "mcx")"""
flux1h_min = """from(bucket: "1m_min")
    |> range(start: -1h)
    |> filter(fn: (r) => r._measurement == "root")
    |> aggregateWindow(every: 1h, fn: min)
    |> to(bucket: "1h_min", org: "mcx")"""
flux8h_max = """from(bucket: "1h_max")
    |> range(start: -8h)
    |> filter(fn: (r) => r._measurement == "root")
    |> aggregateWindow(every: 8h, fn: max)
    |> to(bucket: "8h_max", org: "mcx")"""
flux8h_min = """from(bucket: "1h_max")
    |> range(start: -8h)
    |> filter(fn: (r) => r._measurement == "root")
    |> aggregateWindow(every: 8h, fn: min)
    |> to(bucket: "8h_min", org: "mcx")"""

taskapi.create_task_every("1s_max",flux1s_max,"1s",organization)
taskapi.create_task_every("1s_min",flux1s_max,"1s",organization)
taskapi.create_task_every("1m_max",flux1m_max,"1m",organization)
taskapi.create_task_every("1m_min",flux1m_min,"1m",organization)
taskapi.create_task_every("1h_max",flux1h_max,"1h",organization)
taskapi.create_task_every("1h_min",flux1h_min,"1h",organization)
taskapi.create_task_every("8h_max",flux8h_max,"8h",organization)
taskapi.create_task_every("8h_min",flux8h_min,"8h",organization)

print("success")
