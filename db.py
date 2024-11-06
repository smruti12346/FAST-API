from pymongo import MongoClient
# uri = "mongodb://technovate:pbJ76c9FKuSByMK1@ec2-52-2-7-108.compute-1.amazonaws.com:27017/"
uri = "mongodb+srv://prabhucharanthetechnovate:pbJ76c9FKuSByMK1@cluster0.qagcixp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
my_client = MongoClient(uri)
# db = my_client["zvu_ecom_db"]
db = my_client["riverranch_ecom_db"]
# db = my_client["ecommerce_project"]
# db = my_client["thera_posture_ecom_db"]
# db = my_client["thread_fusion_ecom_db"]