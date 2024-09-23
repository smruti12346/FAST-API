from pymongo import MongoClient
uri = "mongodb+srv://prabhucharanthetechnovate:pbJ76c9FKuSByMK1@cluster0.qagcixp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
my_client = MongoClient(uri)
# db = my_client["zvu_ecom_db"]
db = my_client["riverranch_ecom_db"]
# db = my_client["ecommerce_project"]