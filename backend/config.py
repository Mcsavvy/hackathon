"""Application Configurations."""

from pathlib import Path

BASEDIR = Path(__file__).parent.parent

BACKEND = BASEDIR.joinpath("backend")
DATABASE = BACKEND.joinpath("database")

PHONE_DB = DATABASE.joinpath("phones_raw.json")
PHONE_SCHEMA = BACKEND.joinpath("schemas", "phones.json")

LAPTOP_DB = DATABASE.joinpath("laptops_raw.json")
LAPTOP_SCHEMA = BACKEND.joinpath("schemas", "laptop.json")
LAPTOP_VECTORS = DATABASE.joinpath("laptops.npy")
LAPTOP_PAYLOADS = [
    DATABASE.joinpath(f"laptops_classified_by_specs.json"),
    DATABASE.joinpath(f"laptops_classified_by_groups.json")
]
LAPTOPS_COLLECTION_NAME = "laptops"



QDRANT_BATCH_SIZE = 256
QDRANT_HOST = "https://9e14e244-10a1-4914-865e-cff41e27beb0.us-east-1-0.aws.cloud.qdrant.io:6333"
QDRANT_PORT = 6333
QDRANT_API_KEY = "v7wdIWddLlZ94IU6b2jiMBrTrP52QUBoWI8dhl9_knDqcRuLXLERJw"
QDRANT_INIT_KWARGS = dict(
    url=QDRANT_HOST,
    port=QDRANT_PORT,
    api_key=QDRANT_API_KEY,
    prefer_grpc=True
)

DEVICESPECS_API_KEY = "164e48576397651b4fa37ecfa73037320086b0359d0363e9445736b4022005d361d87b40ba6bf62c16f7c78edbe8439138ce3b32a396c0e4f2b68d76ccef2f3ed9b6a180aac04f11c2a42ee81ead3b8c9a72d69fe572dacb1a14bfa97578b6beedf9866ff7f2f4e437ecce40306412556f7f2993d38cde4e258f9cee9b03a38b"

COHERE_API_KEY = "DIxJ3D2pL7viHFOdAhUdmEkjebVzTtUvDBRZ1fqO"