# In this file, you can define the mapping between the column names in the CSV files and the column names used in the application
# If a column name in the CSV files changes, you can change it here and the application will still work
# To do this, you need to change the values in feature_map and license_map
# E.g. if cluster_id is renamed to cluster_id_new in the CSV files, you need to change the entry
#   "cluster_id": "cluster_id"
# to
#   "cluster_id": "cluster_id_new"


# Mapping for feature_usage files
feature_map = {
    "cluster_id": "cluster_id",
    "app_instance_id": "app_instance_id",
    "time": "time",
    "feature_mask": "feature_mask",
}

# Mapping for license_usage files
license_map = {
    "grant_id": "grant_id",
    "feature_name": "feature_name",
    "cluster_id": "cluster_id",
    "resource_id": "resource_id",
    "service_id": "service_id",
    "start_time": "start_time",
    "end_time": "end_time",
}
